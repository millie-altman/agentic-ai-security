
"""Application-level security and integrity regression tests."""

import logging
import runpy
import sys

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import httpx
import pytest
import respx

import main as app

from src.config_loader import ConfigurationError

from src.collectors.cisa_collector import CollectionError

from src.schemas.intelligence import CISACatalog

from src.processing.normalizer import IntelligenceNormalizer

from src.storage.json_storage import (
    JSONStorage,
    StorageError,
)


@pytest.fixture
def sample_catalog():

    return {
        "title": "Synthetic CISA Catalog",
        "catalogVersion": "2026.11.25",
        "dateReleased": "2026-11-25T12:00:00Z",
        "count": 1,
        "vulnerabilities": [
            {
                "cveID": "CVE-2026-12345",
                "vendorProject": "Example Vendor",
                "product": "Example Product",
                "vulnerabilityName": "Example Vulnerability",
                "dateAdded": "2026-11-25",
                "shortDescription": "Synthetic vulnerability.",
                "requiredAction": "Apply security updates.",
                "dueDate": "2026-12-16",
                "knownRansomwareCampaignUse": "Unknown",
                "notes": "",
                "cwes": ["CWE-79"],
            }
        ],
    }


@pytest.fixture
def isolated_storage(tmp_path, monkeypatch):

    storage = JSONStorage(tmp_path / "data")

    monkeypatch.setattr(
        app,
        "JSONStorage",
        lambda: storage,
    )

    return storage


@pytest.fixture
def mocked_source(sample_catalog):

    with respx.mock as router:

        router.get(
            "https://www.cisa.gov/sites/default/files/"
            "feeds/known_exploited_vulnerabilities.json"
        ).mock(
            return_value=httpx.Response(
                200,
                json=sample_catalog,
            )
        )

        yield router


@pytest.fixture
def normalized_data(sample_catalog):

    catalog = CISACatalog.model_validate(sample_catalog)

    collected_at = datetime.now(timezone.utc)

    records = IntelligenceNormalizer().normalize_cisa_catalog(
        catalog,
        collected_at=collected_at,
    )

    return catalog, records, collected_at


@pytest.mark.parametrize(
    "configuration",
    [
        None,
        [],
        "invalid",
        123,
        True,
    ],
)
def test_invalid_logging_configuration(configuration):

    with pytest.raises(ConfigurationError):

        app.configure_logging({
            "logging": configuration,
        })


def test_http_logging_restricted():

    app.configure_logging({
        "logging": {"level": "DEBUG"},
    })

    assert (
        logging.getLogger("httpx").level
        == logging.WARNING
    )

    assert (
        logging.getLogger("httpcore").level
        == logging.WARNING
    )


def test_valid_normalization(normalized_data):

    catalog, records, collected_at = normalized_data

    app.verify_normalized_records(
        catalog,
        records,
        collected_at,
    )


def test_empty_normalization(normalized_data):

    catalog, _, collected_at = normalized_data

    catalog.count = 0
    catalog.vulnerabilities = []

    app.verify_normalized_records(
        catalog,
        [],
        collected_at,
    )


def test_unexpected_normalized_cve(normalized_data):

    catalog, records, collected_at = normalized_data

    records[0].cve_id = "CVE-2026-99999"

    with pytest.raises(
        app.PipelineError,
        match="Unexpected normalized CVE",
    ):

        app.verify_normalized_records(
            catalog,
            records,
            collected_at,
        )


def test_duplicate_normalized_cve(normalized_data):

    catalog, records, collected_at = normalized_data

    second_vulnerability = (
        catalog.vulnerabilities[0].model_copy(deep=True)
    )

    second_vulnerability.cveID = "CVE-2026-54321"

    catalog.vulnerabilities.append(second_vulnerability)
    catalog.count = 2

    records.append(
        records[0].model_copy(deep=True)
    )

    with pytest.raises(
        app.PipelineError,
        match="Duplicate normalized CVE",
    ):

        app.verify_normalized_records(
            catalog,
            records,
            collected_at,
        )


def test_inconsistent_source_identifiers(normalized_data):

    catalog, records, collected_at = normalized_data

    catalog.vulnerabilities.append(
        catalog.vulnerabilities[0].model_copy(deep=True)
    )

    catalog.count = 2

    records.append(
        records[0].model_copy(deep=True)
    )

    with pytest.raises(
        app.PipelineError,
        match="Source catalog",
    ):

        app.verify_normalized_records(
            catalog,
            records,
            collected_at,
        )


def test_normalized_record_identity_mismatch(normalized_data):

    catalog, records, collected_at = normalized_data

    records[0].record_id = uuid4()

    with pytest.raises(
        app.PipelineError,
        match="record identity mismatch",
    ):

        app.verify_normalized_records(
            catalog,
            records,
            collected_at,
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_id", "unauthorized_source"),
        ("source_version", "invalid_version"),
        ("source_published_at", None),
        (
            "collected_at",
            datetime(2020, 1, 1, tzinfo=timezone.utc),
        ),
    ],
)
def test_source_provenance_mismatch(
    normalized_data,
    field,
    value,
):

    catalog, records, collected_at = normalized_data

    setattr(records[0].source, field, value)

    with pytest.raises(
        app.PipelineError,
        match="source provenance mismatch",
    ):

        app.verify_normalized_records(
            catalog,
            records,
            collected_at,
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("title", "Modified title"),
        ("description", "Modified description"),
        ("vendor", "Modified vendor"),
        ("product", "Modified product"),
        ("remediation", "Modified remediation"),
        ("notes", "Modified notes"),
        ("cwes", ["CWE-999"]),
        ("known_exploited", False),
        ("ai_analyzed", True),
        ("human_reviewed", True),
    ],
)
def test_normalized_content_mismatch(
    normalized_data,
    field,
    value,
):

    catalog, records, collected_at = normalized_data

    setattr(records[0], field, value)

    with pytest.raises(
        app.PipelineError,
        match="intelligence field mismatch",
    ):

        app.verify_normalized_records(
            catalog,
            records,
            collected_at,
        )


def test_valid_deduplication(normalized_data):

    _, records, _ = normalized_data

    app.verify_deduplicated_records(
        records + records,
        records,
    )


def test_empty_deduplication():

    app.verify_deduplicated_records([], [])


def test_deduplication_dropped_record(normalized_data):

    _, records, _ = normalized_data

    with pytest.raises(
        app.PipelineError,
        match="record identity mismatch",
    ):

        app.verify_deduplicated_records(
            records,
            [],
        )


def test_deduplication_duplicate_identifiers(normalized_data):

    _, records, _ = normalized_data

    with pytest.raises(
        app.PipelineError,
        match="Duplicate identifiers",
    ):

        app.verify_deduplicated_records(
            records,
            records + records,
        )


def test_deduplication_unexpected_identifier(normalized_data):

    _, records, _ = normalized_data

    modified = records[0].model_copy(deep=True)
    modified.record_id = uuid4()

    with pytest.raises(
        app.PipelineError,
        match="record identity mismatch",
    ):

        app.verify_deduplicated_records(
            records,
            [modified],
        )


def test_deduplication_modified_content(normalized_data):

    _, records, _ = normalized_data

    modified = records[0].model_copy(deep=True)
    modified.description = "Modified intelligence."

    with pytest.raises(
        app.PipelineError,
        match="record content mismatch",
    ):

        app.verify_deduplicated_records(
            records,
            [modified],
        )


def test_deduplication_latest_record_verified(normalized_data):

    _, records, _ = normalized_data

    older = records[0]

    newer = older.model_copy(deep=True)

    newer.source.collected_at += timedelta(seconds=1)
    newer.description = "Updated intelligence."

    app.verify_deduplicated_records(
        [older, newer],
        [newer],
    )

    with pytest.raises(
        app.PipelineError,
        match="record content mismatch",
    ):

        app.verify_deduplicated_records(
            [older, newer],
            [older],
        )


def test_deduplication_timestamp_tie(normalized_data):

    _, records, _ = normalized_data

    first = records[0]

    second = first.model_copy(deep=True)
    second.description = "Conflicting intelligence."

    app.verify_deduplicated_records(
        [first, second],
        [first],
    )


def test_pipeline_deduplication_failure(
    isolated_storage,
    mocked_source,
    monkeypatch,
):

    monkeypatch.setattr(
        app.IntelligenceDeduplicator,
        "deduplicate",
        lambda self, records: [],
    )

    with pytest.raises(
        app.PipelineError,
        match="record identity mismatch",
    ):

        app.run_pipeline()

    assert not list(
        isolated_storage.raw_directory.glob("*.json")
    )

    assert not list(
        isolated_storage.processed_directory.glob("*.json")
    )


def test_pipeline_in_place_mutation_rejected(
    isolated_storage,
    mocked_source,
    monkeypatch,
):

    def malicious_deduplication(self, records):

        records[0].description = "Modified intelligence."

        return records

    monkeypatch.setattr(
        app.IntelligenceDeduplicator,
        "deduplicate",
        malicious_deduplication,
    )

    with pytest.raises(
        app.PipelineError,
        match="record content mismatch",
    ):

        app.run_pipeline()

    assert not list(
        isolated_storage.processed_directory.glob("*.json")
    )


def test_raw_catalog_content_mismatch(
    isolated_storage,
    mocked_source,
    monkeypatch,
):

    original_loader = isolated_storage.load_cisa_catalog

    def modified_loader(path):

        catalog = original_loader(path)

        catalog.vulnerabilities[0].shortDescription = (
            "Modified intelligence."
        )

        return catalog

    monkeypatch.setattr(
        isolated_storage,
        "load_cisa_catalog",
        modified_loader,
    )

    with pytest.raises(
        app.PipelineError,
        match="Raw catalog round-trip",
    ):

        app.run_pipeline()


def test_processed_same_count_content_mismatch(
    isolated_storage,
    mocked_source,
    monkeypatch,
):

    original_loader = isolated_storage.load_intelligence

    def modified_loader(path):

        records = original_loader(path)

        records[0].description = "Modified intelligence."

        return records

    monkeypatch.setattr(
        isolated_storage,
        "load_intelligence",
        modified_loader,
    )

    with pytest.raises(
        app.PipelineError,
        match="Processed intelligence",
    ):

        app.run_pipeline()


def test_raw_storage_failure_prevents_success(
    isolated_storage,
    mocked_source,
    monkeypatch,
    capsys,
):

    def fail_storage(*args, **kwargs):

        raise StorageError("Synthetic storage failure.")

    monkeypatch.setattr(
        isolated_storage,
        "save_cisa_catalog",
        fail_storage,
    )

    assert app.main() == 3

    assert "SUCCESS" not in capsys.readouterr().out

    assert not list(
        isolated_storage.processed_directory.glob("*.json")
    )


def test_processed_storage_failure_prevents_success(
    isolated_storage,
    mocked_source,
    monkeypatch,
    capsys,
):

    def fail_storage(*args, **kwargs):

        raise StorageError("Synthetic storage failure.")

    monkeypatch.setattr(
        isolated_storage,
        "save_intelligence",
        fail_storage,
    )

    assert app.main() == 3

    assert "SUCCESS" not in capsys.readouterr().out


def test_integrity_failure_prevents_success(
    isolated_storage,
    mocked_source,
    monkeypatch,
    capsys,
):

    monkeypatch.setattr(
        isolated_storage,
        "load_intelligence",
        lambda path: [],
    )

    assert app.main() == 4

    assert "SUCCESS" not in capsys.readouterr().out


@pytest.mark.parametrize(
    "exception_type,expected_exit_code",
    [
        (ConfigurationError, 1),
        (CollectionError, 2),
        (StorageError, 3),
        (app.PipelineError, 4),
        (RuntimeError, 5),
    ],
)
def test_sensitive_exception_details_not_logged(
    monkeypatch,
    caplog,
    capsys,
    exception_type,
    expected_exit_code,
):

    sensitive_value = "SYNTHETIC_SENSITIVE_VALUE"

    def fail_pipeline():

        raise exception_type(sensitive_value)

    monkeypatch.setattr(
        app,
        "run_pipeline",
        fail_pipeline,
    )

    with caplog.at_level(logging.ERROR):

        assert app.main() == expected_exit_code

    assert sensitive_value not in caplog.text
    assert sensitive_value not in capsys.readouterr().out


def test_cli_entry_point(monkeypatch):

    observed_exit_codes = []

    def invalid_configuration():

        raise ConfigurationError(
            "Synthetic configuration failure."
        )

    monkeypatch.setattr(
        "src.config_loader.load_settings",
        invalid_configuration,
    )

    def capture_exit(code):

        observed_exit_codes.append(code)

        raise SystemExit(code)

    monkeypatch.setattr(
        sys,
        "exit",
        capture_exit,
    )

    with pytest.raises(SystemExit) as result:

        runpy.run_module(
            "main",
            run_name="__main__",
        )

    assert result.value.code == 1
    assert observed_exit_codes == [1]
