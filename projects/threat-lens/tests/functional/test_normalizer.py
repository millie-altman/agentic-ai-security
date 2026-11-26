
"""Automated tests for intelligence normalization."""

from datetime import datetime, timezone

import pytest

from src.processing.normalizer import IntelligenceNormalizer

from src.schemas.intelligence import (
    CISACatalog,
    IntelligenceType,
    SeverityLevel,
)


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
                "notes": "https://example.com/advisory",
                "cwes": ["CWE-79"],
            }
        ],
    })


def test_catalog_normalization(sample_catalog):

    records = IntelligenceNormalizer().normalize_cisa_catalog(
        sample_catalog
    )

    assert len(records) == 1

    record = records[0]

    assert record.cve_id == "CVE-2026-12345"
    assert record.vendor == "Example Vendor"
    assert record.product == "Example Product"
    assert record.title == "Example Vulnerability"
    assert record.description == "Synthetic vulnerability."
    assert record.remediation == "Apply security updates."
    assert record.known_exploited is True
    assert record.intelligence_type == IntelligenceType.VULNERABILITY


def test_deterministic_record_id(sample_catalog):

    normalizer = IntelligenceNormalizer()

    first = normalizer.normalize_cisa_catalog(sample_catalog)
    second = normalizer.normalize_cisa_catalog(sample_catalog)

    assert first[0].record_id == second[0].record_id


def test_different_cves_have_different_ids(sample_catalog):

    normalizer = IntelligenceNormalizer()

    first = normalizer.normalize_cisa_catalog(sample_catalog)

    sample_catalog.vulnerabilities[0].cveID = "CVE-2026-54321"

    second = normalizer.normalize_cisa_catalog(sample_catalog)

    assert first[0].record_id != second[0].record_id


def test_source_provenance(sample_catalog):

    record = IntelligenceNormalizer().normalize_cisa_catalog(
        sample_catalog
    )[0]

    assert record.source.source_id == "cisa_kev"
    assert record.source.trust_level.value == "high"
    assert record.source.source_version == "2026.11.25"
    assert record.source.source_published_at == sample_catalog.dateReleased


def test_notes_and_cwes_preserved(sample_catalog):

    record = IntelligenceNormalizer().normalize_cisa_catalog(
        sample_catalog
    )[0]

    assert record.notes == "https://example.com/advisory"
    assert record.cwes == ["CWE-79"]


def test_security_conscious_defaults(sample_catalog):

    record = IntelligenceNormalizer().normalize_cisa_catalog(
        sample_catalog
    )[0]

    assert record.severity == SeverityLevel.UNKNOWN
    assert record.ai_analyzed is False
    assert record.human_reviewed is False


def test_ransomware_tag(sample_catalog):

    payload = sample_catalog.model_dump()

    payload["vulnerabilities"][0][
        "knownRansomwareCampaignUse"
    ] = "Known"

    catalog = CISACatalog.model_validate(payload)

    record = IntelligenceNormalizer().normalize_cisa_catalog(
        catalog
    )[0]

    assert "ransomware-associated" in record.tags


def test_unknown_ransomware_not_tagged(sample_catalog):

    record = IntelligenceNormalizer().normalize_cisa_catalog(
        sample_catalog
    )[0]

    assert "ransomware-associated" not in record.tags


def test_collection_timestamp(sample_catalog):

    timestamp = datetime(
        2026, 11, 25, 12, 30,
        tzinfo=timezone.utc,
    )

    record = IntelligenceNormalizer().normalize_cisa_catalog(
        sample_catalog,
        collected_at=timestamp,
    )[0]

    assert record.source.collected_at == timestamp


def test_empty_catalog(sample_catalog):

    payload = sample_catalog.model_dump()

    payload["count"] = 0
    payload["vulnerabilities"] = []

    catalog = CISACatalog.model_validate(payload)

    records = IntelligenceNormalizer().normalize_cisa_catalog(
        catalog
    )

    assert records == []
