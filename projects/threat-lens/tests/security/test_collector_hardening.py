
"""Security regression tests for intelligence collection."""

import json

import httpx
import pytest
import respx

from src.collectors import cisa_collector

from src.collectors.cisa_collector import (
    CISACollector,
    CollectionError,
    ResponseValidationError,
)

from src.config_loader import (
    ConfigurationError,
    SecurityValidationError,
)


@pytest.fixture
def collector():

    instance = CISACollector()
    instance.retry_delay = 0

    return instance


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


@pytest.mark.parametrize(
    "configuration",
    [
        {},
        {"collection": None},
        {"collection": []},
        {"collection": "invalid"},
    ],
)
def test_invalid_collection_configuration(
    monkeypatch,
    configuration,
):

    monkeypatch.setattr(
        cisa_collector,
        "load_settings",
        lambda: configuration,
    )

    with pytest.raises(ConfigurationError):
        CISACollector()


@pytest.mark.parametrize(
    "attribute,value",
    [
        ("timeout", 0),
        ("timeout", 121),
        ("timeout", True),
        ("timeout", "30"),
        ("max_retries", -1),
        ("max_retries", 6),
        ("retry_delay", -1),
        ("retry_delay", 31),
        ("max_response_size", 0),
        ("max_response_size", 51 * 1024 * 1024),
        ("max_response_size", None),
    ],
)
def test_invalid_collection_limits(
    collector,
    attribute,
    value,
):

    setattr(collector, attribute, value)

    with pytest.raises(
        ConfigurationError,
        match="Invalid collection limit",
    ):
        collector.collect()


def test_missing_collection_limit(monkeypatch):

    monkeypatch.setattr(
        cisa_collector,
        "load_settings",
        lambda: {"collection": {}},
    )

    with pytest.raises(ConfigurationError):
        CISACollector()


def test_modified_source_url_rejected(collector):

    collector.url = "https://example.com/feed.json"

    with pytest.raises(SecurityValidationError):
        collector.collect()


@pytest.mark.parametrize(
    "content_length",
    [
        "invalid",
        "-1",
        "+10",
        "1.5",
        "10, 20",
        "9" * 21,
    ],
)
def test_invalid_content_length_rejected(
    collector,
    content_length,
):

    response = httpx.Response(
        200,
        headers={
            "Content-Type": "application/json",
            "Content-Length": content_length,
        },
    )

    with pytest.raises(
        ResponseValidationError,
        match="Content-Length",
    ):
        collector._validate_response_headers(response)


@pytest.mark.parametrize(
    "encoding",
    [
        "gzip",
        "deflate",
        "br",
        "zstd",
    ],
)
def test_compressed_response_rejected(
    collector,
    encoding,
):

    response = httpx.Response(
        200,
        headers={
            "Content-Type": "application/json",
            "Content-Encoding": encoding,
        },
    )

    with pytest.raises(
        ResponseValidationError,
        match="Compressed",
    ):
        collector._validate_response_headers(response)


def test_missing_content_length_allowed(collector):

    response = httpx.Response(
        200,
        headers={
            "Content-Type": "application/json",
        },
    )

    assert (
        collector._validate_response_headers(response)
        is None
    )


def test_identity_encoding_allowed(collector):

    response = httpx.Response(
        200,
        headers={
            "Content-Type": "application/json",
            "Content-Encoding": "identity",
            "Content-Length": "100",
        },
    )

    assert (
        collector._validate_response_headers(response)
        == 100
    )


@respx.mock
def test_content_length_mismatch(
    collector,
    sample_catalog,
):

    content = json.dumps(sample_catalog).encode("utf-8")

    respx.get(collector.url).mock(
        return_value=httpx.Response(
            200,
            content=content,
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(len(content) + 10),
            },
        )
    )

    with pytest.raises(
        ResponseValidationError,
        match="Content-Length",
    ):
        collector.collect()


@respx.mock
def test_empty_response_rejected(collector):

    respx.get(collector.url).mock(
        return_value=httpx.Response(
            200,
            content=b"",
            headers={
                "Content-Type": "application/json",
            },
        )
    )

    with pytest.raises(
        ResponseValidationError,
        match="Empty",
    ):
        collector.collect()


def test_duplicate_json_keys_rejected(collector):

    content = (
        b'{"count": 1, "count": 2, '
        b'"vulnerabilities": []}'
    )

    with pytest.raises(ResponseValidationError):
        collector._validate_catalog(content)


@pytest.mark.parametrize(
    "constant",
    [
        "NaN",
        "Infinity",
        "-Infinity",
    ],
)
def test_invalid_json_constants_rejected(
    collector,
    constant,
):

    content = (
        f'{{"count": {constant}}}'
    ).encode("utf-8")

    with pytest.raises(ResponseValidationError):
        collector._validate_catalog(content)


def test_duplicate_cve_identifiers_rejected(
    collector,
    sample_catalog,
):

    sample_catalog["vulnerabilities"].append(
        sample_catalog["vulnerabilities"][0].copy()
    )

    sample_catalog["count"] = 2

    content = json.dumps(sample_catalog).encode("utf-8")

    with pytest.raises(
        ResponseValidationError,
        match="Duplicate CVE",
    ):
        collector._validate_catalog(content)


def test_empty_catalog_allowed(
    collector,
    sample_catalog,
):

    sample_catalog["count"] = 0
    sample_catalog["vulnerabilities"] = []

    content = json.dumps(sample_catalog).encode("utf-8")

    catalog = collector._validate_catalog(content)

    assert catalog.count == 0


@pytest.mark.parametrize(
    "attempt,expected",
    [
        (0, 30),
        (1, 60),
        (2, 60),
        (4, 60),
    ],
)
def test_retry_delay_is_bounded(
    collector,
    attempt,
    expected,
):

    collector.retry_delay = 30

    assert (
        collector._calculate_retry_delay(attempt)
        == expected
    )


@respx.mock
def test_rate_limit_recovery(
    collector,
    sample_catalog,
):

    route = respx.get(collector.url).mock(
        side_effect=[
            httpx.Response(429),
            httpx.Response(
                200,
                json=sample_catalog,
            ),
        ]
    )

    catalog = collector.collect()

    assert catalog.count == 1
    assert route.call_count == 2


@respx.mock
def test_unrecoverable_request_error(collector):

    route = respx.get(collector.url).mock(
        side_effect=httpx.RemoteProtocolError(
            "Synthetic protocol failure."
        )
    )

    with pytest.raises(
        CollectionError,
        match="Unrecoverable",
    ):
        collector.collect()

    assert route.call_count == 1


@respx.mock
def test_invalid_response_not_retried(collector):

    route = respx.get(collector.url).mock(
        return_value=httpx.Response(
            200,
            content=b"invalid json",
            headers={
                "Content-Type": "application/json",
            },
        )
    )

    with pytest.raises(ResponseValidationError):
        collector.collect()

    assert route.call_count == 1


@respx.mock
def test_zero_retries_respected(collector):

    collector.max_retries = 0

    route = respx.get(collector.url).mock(
        return_value=httpx.Response(503)
    )

    with pytest.raises(CollectionError):
        collector.collect()

    assert route.call_count == 1
