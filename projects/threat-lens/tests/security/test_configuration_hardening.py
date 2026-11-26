
"""Security regression tests for configuration handling."""

import pytest

from src import config_loader

from src.config_loader import (
    ConfigurationError,
    SecurityValidationError,
    load_yaml,
    load_sources,
    get_source,
    validate_source_url,
)


def test_missing_configuration_file(tmp_path):

    missing_file = tmp_path / "missing.yaml"

    with pytest.raises(ConfigurationError):
        load_yaml(missing_file)


def test_malformed_yaml_rejected(tmp_path):

    config_file = tmp_path / "invalid.yaml"

    config_file.write_text(
        "sources: [invalid",
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError):
        load_yaml(config_file)


@pytest.mark.parametrize(
    "content",
    [
        "",
        "null",
        "- source_one\n- source_two",
        "invalid_configuration",
    ],
)
def test_non_mapping_configuration_rejected(
    tmp_path,
    content,
):

    config_file = tmp_path / "invalid.yaml"

    config_file.write_text(
        content,
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError):
        load_yaml(config_file)


def test_unsafe_yaml_tag_rejected(tmp_path):

    config_file = tmp_path / "unsafe.yaml"

    config_file.write_text(
        "value: !!python/object:builtins.object {}",
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError):
        load_yaml(config_file)


@pytest.mark.parametrize(
    "registry",
    [
        {},
        {"sources": None},
        {"sources": []},
        {"sources": "invalid"},
    ],
)
def test_invalid_source_registry_rejected(
    monkeypatch,
    registry,
):

    monkeypatch.setattr(
        config_loader,
        "load_yaml",
        lambda path: registry,
    )

    with pytest.raises(ConfigurationError):
        load_sources()


@pytest.mark.parametrize(
    "source",
    [
        None,
        [],
        "invalid",
    ],
)
def test_invalid_source_definition_rejected(
    monkeypatch,
    source,
):

    monkeypatch.setattr(
        config_loader,
        "load_sources",
        lambda: {"test_source": source},
    )

    with pytest.raises(ConfigurationError):
        get_source("test_source")


@pytest.mark.parametrize(
    "url",
    [
        None,
        "",
        123,
        [],
    ],
)
def test_invalid_url_type_rejected(url):

    with pytest.raises(SecurityValidationError):

        validate_source_url(
            url,
            ["www.cisa.gov"],
        )


@pytest.mark.parametrize(
    "allowed_hosts",
    [
        None,
        "www.cisa.gov",
        [None],
        [123],
        [""],
    ],
)
def test_invalid_allowlist_rejected(allowed_hosts):

    with pytest.raises(SecurityValidationError):

        validate_source_url(
            "https://www.cisa.gov/feed.json",
            allowed_hosts,
        )


def test_missing_hostname_rejected():

    with pytest.raises(SecurityValidationError):

        validate_source_url(
            "https:///feed.json",
            ["www.cisa.gov"],
        )


def test_case_insensitive_hostname_validation():

    validate_source_url(
        "https://WWW.CISA.GOV/feed.json",
        ["www.cisa.gov"],
    )


def test_standard_https_port_allowed():

    validate_source_url(
        "https://www.cisa.gov:443/feed.json",
        ["www.cisa.gov"],
    )


@pytest.mark.parametrize(
    "enabled",
    [
        False,
        None,
        "true",
        1,
    ],
)
def test_source_requires_explicit_enablement(
    monkeypatch,
    enabled,
):

    monkeypatch.setattr(
        config_loader,
        "load_sources",
        lambda: {
            "test_source": {
                "enabled": enabled,
                "url": "https://www.cisa.gov/feed.json",
                "allowed_hosts": ["www.cisa.gov"],
            }
        },
    )

    with pytest.raises(ConfigurationError):
        get_source("test_source")
