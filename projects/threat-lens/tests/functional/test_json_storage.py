
"""Automated tests for local intelligence storage."""

import hashlib
import json

import pytest

from src.storage.json_storage import (
    JSONStorage,
    StorageError,
)

from src.schemas.intelligence import (
    CISACatalog,
    IntelligenceRecord,
    IntelligenceType,
    SourceMetadata,
)


@pytest.fixture
def storage(tmp_path):
    """Use isolated temporary storage during testing."""

    return JSONStorage(tmp_path / "data")


@pytest.fixture
def sample_catalog():

    return CISACatalog.model_validate({
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
    })


@pytest.fixture
def sample_record():

    return IntelligenceRecord(
        intelligence_type=IntelligenceType.VULNERABILITY,
        title="Example Vulnerability",
        description="Synthetic intelligence record.",
        cve_id="CVE-2026-12345",
        source=SourceMetadata(
            source_id="cisa_kev",
            source_name="CISA KEV",
            source_url="https://www.cisa.gov/",
        ),
    )


def test_storage_directories_created(storage):

    assert storage.raw_directory.is_dir()
    assert storage.processed_directory.is_dir()


def test_save_cisa_catalog(storage, sample_catalog):

    path = storage.save_cisa_catalog(sample_catalog)

    assert path.exists()
    assert path.parent == storage.raw_directory
    assert path.suffix == ".json"


def test_save_intelligence(storage, sample_record):

    path = storage.save_intelligence([sample_record])

    assert path.exists()
    assert path.parent == storage.processed_directory


def test_checksum_created(storage, sample_record):

    path = storage.save_intelligence([sample_record])

    checksum_path = path.with_suffix(".sha256")

    assert checksum_path.exists()

    expected = hashlib.sha256(
        path.read_bytes()
    ).hexdigest()

    assert checksum_path.read_text() == expected


def test_catalog_round_trip(storage, sample_catalog):

    path = storage.save_cisa_catalog(sample_catalog)

    loaded = storage.load_cisa_catalog(path)

    assert loaded == sample_catalog


def test_intelligence_round_trip(storage, sample_record):

    path = storage.save_intelligence([sample_record])

    loaded = storage.load_intelligence(path)

    assert loaded == [sample_record]


def test_tampered_snapshot_rejected(storage, sample_record):

    path = storage.save_intelligence([sample_record])

    path.write_text("tampered intelligence")

    with pytest.raises(StorageError, match="integrity"):
        storage.load_intelligence(path)


def test_missing_checksum_rejected(storage, sample_record):

    path = storage.save_intelligence([sample_record])

    path.with_suffix(".sha256").unlink()

    with pytest.raises(StorageError):
        storage.load_intelligence(path)


def test_path_traversal_rejected(storage):

    unauthorized_path = (
        storage.data_directory / ".." / "outside.json"
    )

    with pytest.raises(StorageError, match="outside"):
        storage.load_intelligence(unauthorized_path)


def test_unique_snapshot_filenames(storage, sample_record):

    first = storage.save_intelligence([sample_record])
    second = storage.save_intelligence([sample_record])

    assert first != second
    assert first.exists()
    assert second.exists()


def test_empty_intelligence_snapshot(storage):

    path = storage.save_intelligence([])

    assert storage.load_intelligence(path) == []


def test_missing_snapshot_rejected(storage):

    path = storage.processed_directory / "missing.json"

    with pytest.raises(StorageError):
        storage.load_intelligence(path)


def test_invalid_schema_with_valid_checksum(
    storage,
    sample_record,
):

    path = storage.save_intelligence([sample_record])

    content = json.dumps(
        [{"unexpected": "invalid intelligence"}]
    ).encode("utf-8")

    path.write_bytes(content)

    path.with_suffix(".sha256").write_text(
        hashlib.sha256(content).hexdigest(),
        encoding="ascii",
    )

    with pytest.raises(StorageError, match="validation"):
        storage.load_intelligence(path)
