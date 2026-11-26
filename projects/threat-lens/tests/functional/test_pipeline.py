
"""Automated tests for ThreatLens application orchestration."""

import pytest
import respx
import httpx

import main as app

from src.config_loader import ConfigurationError

from src.collectors.cisa_collector import CollectionError

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


def test_successful_pipeline(
    isolated_storage,
    mocked_source,
):

    result = app.run_pipeline()

    assert result["status"] == "SUCCESS"
    assert result["records_collected"] == 1
    assert result["records_normalized"] == 1
    assert result["unique_records"] == 1
    assert result["duplicates_removed"] == 0
    assert result["records_reloaded"] == 1
    assert result["integrity_verified"] is True


def test_pipeline_creates_snapshots(
    isolated_storage,
    mocked_source,
):

    app.run_pipeline()

    assert len(
        list(isolated_storage.raw_directory.glob("*.json"))
    ) == 1

    assert len(
        list(isolated_storage.processed_directory.glob("*.json"))
    ) == 1

    assert len(
        list(isolated_storage.raw_directory.glob("*.sha256"))
    ) == 1

    assert len(
        list(isolated_storage.processed_directory.glob("*.sha256"))
    ) == 1


def test_pipeline_execution_duration(
    isolated_storage,
    mocked_source,
):

    result = app.run_pipeline()

    assert result["duration_seconds"] >= 0


def test_successful_application_exit(
    isolated_storage,
    mocked_source,
    capsys,
):

    assert app.main() == 0

    output = capsys.readouterr().out

    assert "THREATLENS" in output
    assert "SUCCESS" in output


def raise_error(error):

    def failing_function(*args, **kwargs):
        raise error

    return failing_function


@pytest.mark.parametrize(
    "error, expected_exit_code",
    [
        (ConfigurationError("Test"), 1),
        (CollectionError("Test"), 2),
        (StorageError("Test"), 3),
        (app.PipelineError("Test"), 4),
        (RuntimeError("Test"), 5),
        (KeyboardInterrupt(), 130),
    ],
)
def test_controlled_exit_codes(
    monkeypatch,
    error,
    expected_exit_code,
):

    monkeypatch.setattr(
        app,
        "run_pipeline",
        raise_error(error),
    )

    assert app.main() == expected_exit_code


def test_invalid_logging_level():

    with pytest.raises(ConfigurationError):

        app.configure_logging({
            "logging": {
                "level": "INVALID"
            }
        })


def test_processed_integrity_failure(
    isolated_storage,
    mocked_source,
    monkeypatch,
):

    monkeypatch.setattr(
        isolated_storage,
        "load_intelligence",
        lambda path: [],
    )

    with pytest.raises(
        app.PipelineError,
        match="Processed intelligence",
    ):

        app.run_pipeline()


def test_normalization_count_mismatch(
    isolated_storage,
    mocked_source,
    monkeypatch,
):

    monkeypatch.setattr(
        app.IntelligenceNormalizer,
        "normalize_cisa_catalog",
        lambda self, catalog, collected_at=None: [],
    )

    with pytest.raises(
        app.PipelineError,
        match="Normalization record count",
    ):

        app.run_pipeline()
