
"""Security tests for intelligence source validation."""

import pytest

from src.config_loader import (
    validate_source_url,
    get_source,
    ConfigurationError,
    SecurityValidationError,
)


ALLOWED_HOSTS = ["www.cisa.gov"]


def test_approved_https_source():
    validate_source_url(
        "https://www.cisa.gov/feed.json",
        ALLOWED_HOSTS,
    )


@pytest.mark.parametrize(
    "url",
    [
        "http://www.cisa.gov/feed.json",
        "https://example.com/feed.json",
        "https://www.cisa.gov.example.com",
        "https://www.cisa.gov@example.com",
        "https://user:password@www.cisa.gov",
        "https://www.cisa.gov:8080",
        "https://127.0.0.1",
        "https://169.254.169.254",
        "file:///etc/passwd",
        "https://www.cisa.gov/#fragment",
        "not-a-url",
        "https://www.cisa.gov:invalid",
        "https://www.cisa.gov\\@example.com",
        "https://www.cisa.gov/\nfeed.json",
    ],
)
def test_unauthorized_source_rejected(url):
    with pytest.raises(SecurityValidationError):
        validate_source_url(url, ALLOWED_HOSTS)


def test_empty_allowlist_rejected():
    with pytest.raises(SecurityValidationError):
        validate_source_url(
            "https://www.cisa.gov",
            [],
        )


def test_enabled_source():
    source = get_source("cisa_kev")

    assert source["enabled"] is True


def test_disabled_source():
    with pytest.raises(ConfigurationError):
        get_source("nvd")


def test_unknown_source():
    with pytest.raises(ConfigurationError):
        get_source("unauthorized_source")
