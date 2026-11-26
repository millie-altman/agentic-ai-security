
"""Automated tests for the ThreatLens CISA KEV collector."""

import httpx
import pytest
import respx

from src.collectors.cisa_collector import (
    CISACollector,
    CollectionError,
    ResponseValidationError,
)


@pytest.fixture
def collector():
    instance = CISACollector()

    # Disable retry delays during automated tests.
    instance.retry_delay = 0

    return instance


@pytest.fixture
def sample_catalog():
    """Synthetic CISA catalog for offline testing."""

    return {
        "title": "CISA Known Exploited Vulnerabilities",
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
                "shortDescription": "Synthetic test vulnerability.",
                "requiredAction": "Apply security updates.",
                "dueDate": "2026-12-16",
                "knownRansomwareCampaignUse": "Unknown",
                "notes": "",
                "cwes": ["CWE-79"],
            }
        ],
    }


@respx.mock
def test_successful_collection(collector, sample_catalog):

    route = respx.get(collector.url).mock(
        return_value=httpx.Response(
            200,
            json=sample_catalog,
        )
    )

    catalog = collector.collect()

    assert route.called
    assert catalog.count == 1
    assert (
        catalog.vulnerabilities[0].cveID
        == "CVE-2026-12345"
    )


@respx.mock
def test_invalid_json(collector):

    respx.get(collector.url).mock(
        return_value=httpx.Response(
            200,
            content=b"invalid json",
            headers={"Content-Type": "application/json"},
        )
    )

    with pytest.raises(ResponseValidationError):
        collector.collect()


@respx.mock
def test_invalid_catalog_structure(collector):

    respx.get(collector.url).mock(
        return_value=httpx.Response(
            200,
            json={"unexpected": "data"},
        )
    )

    with pytest.raises(ResponseValidationError):
        collector.collect()


@respx.mock
def test_catalog_count_mismatch(collector, sample_catalog):

    sample_catalog["count"] = 100

    respx.get(collector.url).mock(
        return_value=httpx.Response(
            200,
            json=sample_catalog,
        )
    )

    with pytest.raises(ResponseValidationError):
        collector.collect()


@respx.mock
def test_unexpected_content_type(collector):

    respx.get(collector.url).mock(
        return_value=httpx.Response(
            200,
            text="<html>Unexpected response</html>",
            headers={"Content-Type": "text/html"},
        )
    )

    with pytest.raises(ResponseValidationError):
        collector.collect()


@respx.mock
def test_oversized_declared_response(collector):

    collector.max_response_size = 100

    respx.get(collector.url).mock(
        return_value=httpx.Response(
            200,
            content=b"A" * 200,
            headers={"Content-Type": "application/json"},
        )
    )

    with pytest.raises(ResponseValidationError):
        collector.collect()


@respx.mock
def test_oversized_actual_response(collector):

    collector.max_response_size = 100

    respx.get(collector.url).mock(
        return_value=httpx.Response(
            200,
            content=b"A" * 200,
            headers={
                "Content-Type": "application/json",
                "Content-Length": "50",
            },
        )
    )

    with pytest.raises(ResponseValidationError):
        collector.collect()


@respx.mock
def test_redirect_rejected(collector):

    route = respx.get(collector.url).mock(
        return_value=httpx.Response(
            302,
            headers={
                "Location": "https://example.com/feed.json"
            },
        )
    )

    with pytest.raises(CollectionError):
        collector.collect()

    assert route.call_count == 1


@respx.mock
def test_http_not_found(collector):

    route = respx.get(collector.url).mock(
        return_value=httpx.Response(404)
    )

    with pytest.raises(CollectionError):
        collector.collect()

    assert route.call_count == 1


@respx.mock
def test_server_error_retries(collector):

    route = respx.get(collector.url).mock(
        return_value=httpx.Response(503)
    )

    with pytest.raises(CollectionError):
        collector.collect()

    assert route.call_count == collector.max_retries + 1


@respx.mock
def test_timeout_retries(collector):

    route = respx.get(collector.url).mock(
        side_effect=httpx.ReadTimeout("Simulated timeout")
    )

    with pytest.raises(CollectionError):
        collector.collect()

    assert route.call_count == collector.max_retries + 1


@respx.mock
def test_recovery_after_temporary_failure(
    collector,
    sample_catalog,
):

    route = respx.get(collector.url).mock(
        side_effect=[
            httpx.Response(503),
            httpx.Response(200, json=sample_catalog),
        ]
    )

    catalog = collector.collect()

    assert catalog.count == 1
    assert route.call_count == 2
