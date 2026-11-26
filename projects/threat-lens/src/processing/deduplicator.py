
"""
ThreatLens Intelligence Deduplicator

Removes duplicate intelligence records while preserving
source provenance and the most recently collected data.

Cross-source intelligence correlation is handled separately.
"""

import logging
from uuid import UUID

from src.schemas.intelligence import IntelligenceRecord


logger = logging.getLogger(__name__)


class IntelligenceDeduplicator:
    """Remove duplicate standardized intelligence records."""

    def deduplicate(
        self,
        records: list[IntelligenceRecord],
    ) -> list[IntelligenceRecord]:
        """Retain the latest collected record for each identity."""

        unique_records: dict[UUID, IntelligenceRecord] = {}

        for record in records:

            existing = unique_records.get(record.record_id)

            if existing is None:
                unique_records[record.record_id] = record
                continue

            if (
                record.source.collected_at
                > existing.source.collected_at
            ):
                unique_records[record.record_id] = record

        result = list(unique_records.values())

        duplicates_removed = len(records) - len(result)

        logger.info(
            "Deduplication complete: %s input records, "
            "%s unique records, %s duplicates removed.",
            len(records),
            len(result),
            duplicates_removed,
        )

        return result
