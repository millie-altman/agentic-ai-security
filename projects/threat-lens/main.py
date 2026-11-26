
"""
ThreatLens — Cyber Threat Intelligence

Application entry point for the foundational
intelligence collection and processing pipeline.

Cyber Grad Chronicles
"""

import logging
import sys
import time

from datetime import datetime, timezone

from src.config_loader import (
    load_settings,
    ConfigurationError,
)

from src.collectors.cisa_collector import (
    CISACollector,
    CollectionError,
)

from src.processing.normalizer import (
    IntelligenceNormalizer,
)

from src.processing.deduplicator import (
    IntelligenceDeduplicator,
)

from src.storage.json_storage import (
    JSONStorage,
    StorageError,
)


logger = logging.getLogger("threatlens")


class PipelineError(Exception):
    """Raised when pipeline verification fails."""


def configure_logging(settings: dict) -> None:
    """Initialize application logging."""

    logging_settings = settings.get("logging", {})

    level_name = str(
        logging_settings.get("level", "INFO")
    ).upper()

    allowed_levels = {
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    }

    if level_name not in allowed_levels:
        raise ConfigurationError(
            "Invalid application logging level."
        )

    logging.basicConfig(
        level=getattr(logging, level_name),
        format=(
            "%(asctime)sZ | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    logging.Formatter.converter = time.gmtime


def print_banner() -> None:
    """Display application identification."""

    print()
    print("=" * 60)
    print("THREATLENS")
    print("Cyber Threat Intelligence")
    print("Version 0.1.0 | Cyber Grad Chronicles")
    print("=" * 60)
    print()


def run_pipeline() -> dict:
    """Execute the complete intelligence pipeline."""

    start_time = time.perf_counter()

    logger.info("Initializing intelligence pipeline.")

    # Initialize application components.

    collector = CISACollector()
    normalizer = IntelligenceNormalizer()
    deduplicator = IntelligenceDeduplicator()
    storage = JSONStorage()

    # Collect source intelligence.

    logger.info("Collecting CISA KEV intelligence.")

    catalog = collector.collect()

    collected_at = datetime.now(timezone.utc)

    # Normalize source intelligence.

    logger.info("Normalizing intelligence records.")

    records = normalizer.normalize_cisa_catalog(
        catalog,
        collected_at=collected_at,
    )

    if len(records) != catalog.count:
        raise PipelineError(
            "Normalization record count mismatch."
        )

    # Remove duplicate intelligence records.

    logger.info("Deduplicating intelligence records.")

    unique_records = deduplicator.deduplicate(
        records
    )

    duplicates_removed = (
        len(records) - len(unique_records)
    )

    # Persist source and processed intelligence.

    logger.info("Persisting intelligence snapshots.")

    raw_path = storage.save_cisa_catalog(
        catalog
    )

    processed_path = storage.save_intelligence(
        unique_records
    )

    # Reload and verify persisted intelligence.

    logger.info("Verifying stored intelligence.")

    loaded_catalog = storage.load_cisa_catalog(
        raw_path
    )

    loaded_records = storage.load_intelligence(
        processed_path
    )

    if loaded_catalog != catalog:
        raise PipelineError(
            "Raw catalog round-trip verification failed."
        )

    if loaded_records != unique_records:
        raise PipelineError(
            "Processed intelligence verification failed."
        )

    unique_ids = {
        record.record_id
        for record in loaded_records
    }

    if len(unique_ids) != len(loaded_records):
        raise PipelineError(
            "Duplicate identifiers remain after processing."
        )

    duration = time.perf_counter() - start_time

    logger.info(
        "Intelligence pipeline completed successfully."
    )

    return {
        "source": "CISA KEV",
        "catalog_version": catalog.catalogVersion,
        "collected_at": collected_at.isoformat(),
        "records_collected": catalog.count,
        "records_normalized": len(records),
        "unique_records": len(unique_records),
        "duplicates_removed": duplicates_removed,
        "records_reloaded": len(loaded_records),
        "raw_snapshot": raw_path.name,
        "processed_snapshot": processed_path.name,
        "integrity_verified": True,
        "duration_seconds": round(duration, 2),
        "status": "SUCCESS",
    }


def print_summary(summary: dict) -> None:
    """Display intelligence collection statistics."""

    print()
    print("=" * 60)
    print("INTELLIGENCE COLLECTION SUMMARY")
    print("=" * 60)

    print(f"Source:             {summary['source']}")
    print(f"Catalog version:    {summary['catalog_version']}")
    print(f"Collected at:       {summary['collected_at']}")
    print(f"Records collected:  {summary['records_collected']:,}")
    print(f"Records normalized: {summary['records_normalized']:,}")
    print(f"Unique records:     {summary['unique_records']:,}")
    print(f"Duplicates removed: {summary['duplicates_removed']:,}")
    print(f"Records reloaded:   {summary['records_reloaded']:,}")

    print(
        "Integrity verified: "
        f"{summary['integrity_verified']}"
    )

    print(
        "Execution time:     "
        f"{summary['duration_seconds']} seconds"
    )

    print(f"Pipeline status:    {summary['status']}")

    print()
    print("GENERATED SNAPSHOTS")
    print("-" * 60)
    print(f"Raw:       {summary['raw_snapshot']}")
    print(f"Processed: {summary['processed_snapshot']}")

    print("=" * 60)
    print()


def main() -> int:
    """Initialize and execute ThreatLens."""

    try:
        settings = load_settings()

        configure_logging(settings)

        print_banner()

        summary = run_pipeline()

        print_summary(summary)

        return 0

    except ConfigurationError:
        logger.error("Application configuration failed.")
        return 1

    except CollectionError:
        logger.error("Intelligence collection failed.")
        return 2

    except StorageError:
        logger.error("Intelligence storage failed.")
        return 3

    except PipelineError:
        logger.error("Pipeline integrity verification failed.")
        return 4

    except KeyboardInterrupt:
        logger.warning("Execution interrupted by user.")
        return 130

    except Exception as exc:
        logger.error(
            "Unexpected application failure: %s",
            type(exc).__name__,
        )
        return 5


if __name__ == "__main__":
    sys.exit(main())
