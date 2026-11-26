
"""Automated tests for intelligence deduplication."""

from datetime import datetime, timezone
from uuid import NAMESPACE_URL, uuid5

import pytest

from src.processing.deduplicator import IntelligenceDeduplicator

from src.schemas.intelligence import (
    IntelligenceRecord,
    SourceMetadata,
    IntelligenceType,
)


@pytest.fixture
def deduplicator():
    return IntelligenceDeduplicator()


def make_record(
    cve_id="CVE-2026-12345",
    source_id="cisa_kev",
    hour=12,
    description="Synthetic vulnerability.",
):
    """Create synthetic intelligence with a stable identity."""

    source = SourceMetadata(
        source_id=source_id,
        source_name=source_id,
        source_url="https://example.com/",
        collected_at=datetime(
            2026, 11, 25, hour, 0,
            tzinfo=timezone.utc,
        ),
    )

    return IntelligenceRecord(
        record_id=uuid5(
            NAMESPACE_URL,
            f"threatlens:{source_id}:{cve_id}",
        ),
        intelligence_type=IntelligenceType.VULNERABILITY,
        title="Example Vulnerability",
        description=description,
        source=source,
        cve_id=cve_id,
    )


def test_empty_input(deduplicator):

    assert deduplicator.deduplicate([]) == []


def test_single_record(deduplicator):

    record = make_record()

    result = deduplicator.deduplicate([record])

    assert len(result) == 1
    assert result[0] == record


def test_identical_duplicates_removed(deduplicator):

    first = make_record()
    second = make_record()

    result = deduplicator.deduplicate(
        [first, second]
    )

    assert len(result) == 1


def test_latest_record_retained(deduplicator):

    older = make_record(
        hour=9,
        description="Older intelligence.",
    )

    newer = make_record(
        hour=12,
        description="Updated intelligence.",
    )

    result = deduplicator.deduplicate(
        [older, newer]
    )

    assert len(result) == 1
    assert result[0].description == "Updated intelligence."


def test_older_record_does_not_replace_newer(deduplicator):

    newer = make_record(hour=12)
    older = make_record(hour=9)

    result = deduplicator.deduplicate(
        [newer, older]
    )

    assert result[0] == newer


def test_different_cves_preserved(deduplicator):

    first = make_record(cve_id="CVE-2026-12345")
    second = make_record(cve_id="CVE-2026-54321")

    result = deduplicator.deduplicate(
        [first, second]
    )

    assert len(result) == 2


def test_different_sources_preserved(deduplicator):

    cisa = make_record(source_id="cisa_kev")
    nvd = make_record(source_id="nvd")

    result = deduplicator.deduplicate(
        [cisa, nvd]
    )

    assert len(result) == 2


def test_timestamp_tie_retains_first(deduplicator):

    first = make_record(
        description="First record.",
    )

    second = make_record(
        description="Second record.",
    )

    result = deduplicator.deduplicate(
        [first, second]
    )

    assert result[0] == first


def test_deduplication_is_idempotent(deduplicator):

    records = [
        make_record(),
        make_record(),
        make_record(cve_id="CVE-2026-54321"),
    ]

    first = deduplicator.deduplicate(records)
    second = deduplicator.deduplicate(first)

    assert first == second


def test_input_list_not_modified(deduplicator):

    records = [
        make_record(),
        make_record(),
    ]

    original = records.copy()

    deduplicator.deduplicate(records)

    assert records == original
    assert len(records) == 2
