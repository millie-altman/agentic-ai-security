
"""
ThreatLens Intelligence Normalizer

Transforms source-specific intelligence into standardized
ThreatLens intelligence records.

Normalization does not establish factual accuracy or
make external content safe for AI processing.
"""

from datetime import datetime, timezone
from uuid import NAMESPACE_URL, uuid5

from src.config_loader import get_source

from src.schemas.intelligence import (
    CISACatalog,
    CISAVulnerability,
    IntelligenceRecord,
    IntelligenceType,
    SourceMetadata,
    SeverityLevel,
)


class IntelligenceNormalizer:
    """Normalize intelligence from supported sources."""

    def normalize_cisa_vulnerability(
        self,
        vulnerability: CISAVulnerability,
        source: SourceMetadata,
    ) -> IntelligenceRecord:
        """Convert a CISA vulnerability into a common record."""

        record_id = uuid5(
            NAMESPACE_URL,
            f"threatlens:cisa_kev:{vulnerability.cveID}",
        )

        tags = [
            "cisa-kev",
            "known-exploited",
            "vulnerability",
        ]

        if vulnerability.knownRansomwareCampaignUse.value == "Known":
            tags.append("ransomware-associated")

        return IntelligenceRecord(
            record_id=record_id,

            intelligence_type=IntelligenceType.VULNERABILITY,

            title=vulnerability.vulnerabilityName,
            description=vulnerability.shortDescription,

            source=source,

            cve_id=vulnerability.cveID,
            vendor=vulnerability.vendorProject,
            product=vulnerability.product,

            severity=SeverityLevel.UNKNOWN,
            known_exploited=True,

            ransomware_association=(
                vulnerability.knownRansomwareCampaignUse
            ),

            date_added=vulnerability.dateAdded,
            remediation_due_date=vulnerability.dueDate,

            remediation=vulnerability.requiredAction,
            notes=vulnerability.notes,

            cwes=vulnerability.cwes,

            tags=tags,

            ai_analyzed=False,
            human_reviewed=False,
        )

    def normalize_cisa_catalog(
        self,
        catalog: CISACatalog,
        collected_at: datetime | None = None,
    ) -> list[IntelligenceRecord]:
        """Normalize an entire validated CISA catalog."""

        source_config = get_source("cisa_kev")

        source = SourceMetadata(
            source_id="cisa_kev",
            source_name=source_config["name"],
            source_url=source_config["url"],
            trust_level=source_config["trust_level"],
            source_version=catalog.catalogVersion,
            source_published_at=catalog.dateReleased,
            collected_at=(
                collected_at or datetime.now(timezone.utc)
            ),
        )

        return [
            self.normalize_cisa_vulnerability(
                vulnerability,
                source,
            )
            for vulnerability in catalog.vulnerabilities
        ]
