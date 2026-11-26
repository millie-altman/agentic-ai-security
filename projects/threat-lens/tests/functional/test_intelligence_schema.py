
"""Functional tests for ThreatLens intelligence schemas."""

import pytest

from pydantic import ValidationError

from src.schemas.intelligence import (
    CISAVulnerability,
    IntelligenceRecord,
    IntelligenceType,
    SourceMetadata,
    SeverityLevel,
)


def sample_cisa_record():
    """Synthetic vulnerability data for testing."""

    return {
        "cveID": "CVE-2026-12345",
        "vendorProject": "Example Vendor",
        "product": "Example Product",
        "vulnerabilityName": "Example Vulnerability",
        "dateAdded": "2026-11-25",
        "shortDescription": "Synthetic test vulnerability.",
        "requiredAction": "Apply vendor security updates.",
        "dueDate": "2026-12-16",
        "knownRansomwareCampaignUse": "Unknown",
        "notes": "",
        "cwes": ["CWE-79"],
    }


def test_valid_cisa_vulnerability():
    record = CISAVulnerability(**sample_cisa_record())

    assert record.cveID == "CVE-2026-12345"
    assert record.vendorProject == "Example Vendor"


def test_invalid_cve_identifier():
    data = sample_cisa_record()
    data["cveID"] = "INVALID-CVE"

    with pytest.raises(ValidationError):
        CISAVulnerability(**data)


def test_missing_required_field():
    data = sample_cisa_record()
    del data["product"]

    with pytest.raises(ValidationError):
        CISAVulnerability(**data)


def test_invalid_date():
    data = sample_cisa_record()
    data["dateAdded"] = "not-a-date"

    with pytest.raises(ValidationError):
        CISAVulnerability(**data)


def test_oversized_description():
    data = sample_cisa_record()
    data["shortDescription"] = "A" * 20001

    with pytest.raises(ValidationError):
        CISAVulnerability(**data)


def test_standardized_intelligence_record():
    source = SourceMetadata(
        source_id="cisa_kev",
        source_name="CISA KEV",
        source_url="https://www.cisa.gov/",
        trust_level="high",
    )

    record = IntelligenceRecord(
        intelligence_type=IntelligenceType.VULNERABILITY,
        title="Example Vulnerability",
        description="Synthetic test intelligence.",
        source=source,
        cve_id="CVE-2026-12345",
        known_exploited=True,
    )

    assert record.severity == SeverityLevel.UNKNOWN
    assert record.ai_analyzed is False
    assert record.human_reviewed is False
    assert record.known_exploited is True


def test_unexpected_intelligence_field():
    source = SourceMetadata(
        source_id="cisa_kev",
        source_name="CISA KEV",
        source_url="https://www.cisa.gov/",
    )

    with pytest.raises(ValidationError):
        IntelligenceRecord(
            intelligence_type="vulnerability",
            title="Example Vulnerability",
            description="Synthetic test intelligence.",
            source=source,
            unauthorized_field="unexpected data",
        )
