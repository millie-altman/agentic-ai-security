
"""
ThreatLens Intelligence Schemas

Defines source-specific and standardized intelligence data models.

External intelligence must be validated before entering the
ThreatLens processing pipeline.
"""

from datetime import date, datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    AwareDatetime,
)


# ============================================================
# Intelligence classifications
# ============================================================

class IntelligenceType(str, Enum):
    VULNERABILITY = "vulnerability"
    THREAT_ACTOR = "threat_actor"
    SECURITY_ADVISORY = "security_advisory"
    INCIDENT = "incident"
    INDICATOR = "indicator"
    RESEARCH = "research"


class TrustLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class RansomwareAssociation(str, Enum):
    KNOWN = "Known"
    UNKNOWN = "Unknown"


# ============================================================
# CISA KEV source-specific schemas
# ============================================================

class CISAVulnerability(BaseModel):
    """Validate an individual CISA KEV vulnerability."""

    model_config = ConfigDict(extra="ignore")

    cveID: str = Field(
        pattern=r"^CVE-[0-9]{4}-[0-9]{4,}$",
        max_length=32,
    )

    vendorProject: str = Field(min_length=1, max_length=500)
    product: str = Field(min_length=1, max_length=500)
    vulnerabilityName: str = Field(min_length=1, max_length=1000)

    dateAdded: date

    shortDescription: str = Field(
        min_length=1,
        max_length=20000,
    )

    requiredAction: str = Field(
        min_length=1,
        max_length=20000,
    )

    dueDate: date

    knownRansomwareCampaignUse: RansomwareAssociation

    notes: str = Field(default="", max_length=20000)

    cwes: list[str] = Field(default_factory=list)


class CISACatalog(BaseModel):
    """Validate the complete CISA KEV catalog."""

    model_config = ConfigDict(extra="ignore")

    title: str
    catalogVersion: str
    dateReleased: AwareDatetime
    count: int = Field(ge=0)

    vulnerabilities: list[CISAVulnerability]


# ============================================================
# Standardized source provenance
# ============================================================

class SourceMetadata(BaseModel):
    """Preserve the origin and collection context of intelligence."""

    model_config = ConfigDict(extra="forbid")

    source_id: str
    source_name: str
    source_url: HttpUrl

    trust_level: TrustLevel = TrustLevel.UNKNOWN

    collected_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ============================================================
# Standardized intelligence schema
# ============================================================

class IntelligenceRecord(BaseModel):
    """
    Common intelligence format used throughout ThreatLens.

    All supported intelligence sources will eventually be
    normalized into this structure.
    """

    model_config = ConfigDict(extra="forbid")

    record_id: UUID = Field(default_factory=uuid4)

    intelligence_type: IntelligenceType

    title: str = Field(min_length=1, max_length=1000)

    description: str = Field(
        min_length=1,
        max_length=20000,
    )

    source: SourceMetadata

    cve_id: str | None = Field(
        default=None,
        pattern=r"^CVE-[0-9]{4}-[0-9]{4,}$",
        max_length=32,
    )

    vendor: str | None = None
    product: str | None = None

    severity: SeverityLevel = SeverityLevel.UNKNOWN

    known_exploited: bool | None = None

    ransomware_association: RansomwareAssociation = (
        RansomwareAssociation.UNKNOWN
    )

    date_added: date | None = None
    remediation_due_date: date | None = None

    remediation: str | None = None

    cwes: list[str] = Field(default_factory=list)
    indicators: list[str] = Field(default_factory=list)
    mitre_techniques: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)

    ai_analyzed: bool = False
    human_reviewed: bool = False
