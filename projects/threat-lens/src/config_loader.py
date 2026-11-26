
"""
ThreatLens Configuration Loader

Loads application settings and intelligence source configuration.
Validates approved sources and enforces initial network security
boundaries before intelligence collection.
"""

from pathlib import Path
from urllib.parse import urlsplit

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"


class ConfigurationError(Exception):
    """Raised when configuration is missing or invalid."""


class SecurityValidationError(ConfigurationError):
    """Raised when configuration violates security requirements."""


def load_yaml(file_path: Path) -> dict:
    """Safely load a YAML configuration file."""

    try:
        with file_path.open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file)

    except (OSError, yaml.YAMLError) as exc:
        raise ConfigurationError(
            f"Unable to load configuration: {file_path.name}"
        ) from exc

    if not isinstance(config, dict):
        raise ConfigurationError(
            f"Invalid configuration structure: {file_path.name}"
        )

    return config


def load_settings() -> dict:
    """Load ThreatLens application settings."""

    return load_yaml(CONFIG_DIR / "settings.yaml")


def load_sources() -> dict:
    """Load the approved intelligence source registry."""

    config = load_yaml(CONFIG_DIR / "sources.yaml")
    sources = config.get("sources")

    if not isinstance(sources, dict):
        raise ConfigurationError(
            "Intelligence source registry is missing or invalid."
        )

    return sources


def validate_source_url(
    url: str,
    allowed_hosts: list[str],
) -> None:
    """Validate an intelligence source URL."""

    if not isinstance(url, str) or not url:
        raise SecurityValidationError("Invalid source URL.")

    if not isinstance(allowed_hosts, list) or not allowed_hosts:
        raise SecurityValidationError("Invalid hostname allowlist.")

    if any(
        not isinstance(host, str) or not host
        for host in allowed_hosts
    ):
        raise SecurityValidationError("Invalid allowlist entry.")

    if any(
        char.isspace() or ord(char) < 32 or ord(char) == 127
        for char in url
    ) or "\\" in url:
        raise SecurityValidationError(
            "URL contains prohibited characters."
        )

    try:
        parsed = urlsplit(url)
        port = parsed.port
        hostname = parsed.hostname

    except ValueError as exc:
        raise SecurityValidationError(
            "Malformed source URL."
        ) from exc

    if parsed.scheme != "https":
        raise SecurityValidationError(
            "Intelligence sources must use HTTPS."
        )

    if not hostname:
        raise SecurityValidationError(
            "Source URL does not contain a hostname."
        )

    if parsed.username is not None or parsed.password is not None:
        raise SecurityValidationError(
            "Credentials are prohibited in source URLs."
        )

    approved_hosts = {
        host.lower() for host in allowed_hosts
    }

    if hostname.lower() not in approved_hosts:
        raise SecurityValidationError(
            "Source hostname is not allowlisted."
        )

    if port not in (None, 443):
        raise SecurityValidationError(
            "Nonstandard HTTPS ports are prohibited."
        )

    if parsed.fragment:
        raise SecurityValidationError(
            "URL fragments are prohibited."
        )


def get_source(source_id: str) -> dict:
    """Retrieve and validate an enabled intelligence source."""

    sources = load_sources()

    if source_id not in sources:
        raise ConfigurationError(
            f"Unknown intelligence source: {source_id}"
        )

    source = sources[source_id]

    if not isinstance(source, dict):
        raise ConfigurationError(
            f"Invalid source configuration: {source_id}"
        )

    if source.get("enabled") is not True:
        raise ConfigurationError(
            f"Intelligence source is disabled: {source_id}"
        )

    validate_source_url(
        source.get("url", ""),
        source.get("allowed_hosts", []),
    )

    return source
