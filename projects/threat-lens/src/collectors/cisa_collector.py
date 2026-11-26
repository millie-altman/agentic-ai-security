
"""
ThreatLens CISA KEV Collector

Retrieves and validates the CISA Known Exploited
Vulnerabilities catalog using controlled HTTP requests.

External intelligence is treated as untrusted data.
"""

import json
import logging
import time

import httpx

from pydantic import ValidationError

from src.config_loader import (
    get_source,
    load_settings,
    ConfigurationError,
)
from src.schemas.intelligence import CISACatalog


logger = logging.getLogger(__name__)


class CollectionError(Exception):
    """Raised when intelligence collection fails."""


class ResponseValidationError(CollectionError):
    """Raised when an intelligence response is invalid."""


class CISACollector:
    """Collect vulnerability intelligence from CISA KEV."""

    def __init__(self):
        self.source = get_source("cisa_kev")
        self.settings = load_settings()

        self.url = self.source["url"]

        collection = self.settings["collection"]

        self.timeout = collection["request_timeout_seconds"]
        self.max_retries = collection["max_retries"]
        self.retry_delay = collection["retry_delay_seconds"]
        self.max_response_size = collection[
            "max_response_size_bytes"
        ]

        self._validate_limits()

    def _validate_limits(self):
        """Validate resource consumption limits."""

        limits = {
            "timeout": (self.timeout, 1, 120),
            "max_retries": (self.max_retries, 0, 5),
            "retry_delay": (self.retry_delay, 0, 30),
            "max_response_size": (
                self.max_response_size,
                1,
                50 * 1024 * 1024,
            ),
        }

        for name, (value, minimum, maximum) in limits.items():
            if (
                type(value) is not int
                or not minimum <= value <= maximum
            ):
                raise ConfigurationError(
                    f"Invalid collection limit: {name}"
                )

    def _download(self, client: httpx.Client) -> bytes:
        """Download a response while enforcing size limits."""

        with client.stream("GET", self.url) as response:

            response.raise_for_status()

            content_type = response.headers.get(
                "content-type", ""
            ).split(";")[0].strip().lower()

            if content_type != "application/json":
                raise ResponseValidationError(
                    "Unexpected response content type."
                )

            content_length = response.headers.get(
                "content-length"
            )

            if content_length is not None:
                try:
                    declared_size = int(content_length)
                except ValueError as exc:
                    raise ResponseValidationError(
                        "Invalid Content-Length header."
                    ) from exc

                if (
                    declared_size < 0
                    or declared_size > self.max_response_size
                ):
                    raise ResponseValidationError(
                        "Declared response size exceeds limits."
                    )

            data = bytearray()

            for chunk in response.iter_bytes(
                chunk_size=65536
            ):
                if (
                    len(data) + len(chunk)
                    > self.max_response_size
                ):
                    raise ResponseValidationError(
                        "Response exceeded maximum allowed size."
                    )

                data.extend(chunk)

            return bytes(data)

    def _validate_catalog(self, data: bytes) -> CISACatalog:
        """Validate JSON structure and catalog consistency."""

        try:
            payload = json.loads(data)
            catalog = CISACatalog.model_validate(payload)

        except (
            ValueError,
            ValidationError,
            RecursionError,
        ) as exc:
            raise ResponseValidationError(
                "Invalid CISA KEV catalog structure."
            ) from exc

        if catalog.count != len(catalog.vulnerabilities):
            raise ResponseValidationError(
                "Catalog vulnerability count mismatch."
            )

        return catalog

    def collect(self) -> CISACatalog:
        """Retrieve and validate the CISA KEV catalog."""

        headers = {
            "User-Agent": "ThreatLens/0.1.0",
            "Accept": "application/json",
            "Accept-Encoding": "identity",
        }

        with httpx.Client(
            timeout=self.timeout,
            verify=True,
            follow_redirects=False,
            trust_env=False,
            headers=headers,
        ) as client:

            for attempt in range(self.max_retries + 1):

                try:
                    logger.info(
                        "Collecting CISA KEV intelligence "
                        "(attempt %s).",
                        attempt + 1,
                    )

                    data = self._download(client)
                    catalog = self._validate_catalog(data)

                    logger.info(
                        "Successfully collected %s vulnerabilities.",
                        catalog.count,
                    )

                    return catalog

                except httpx.HTTPStatusError as exc:
                    status = exc.response.status_code

                    retryable = (
                        status == 429
                        or 500 <= status <= 599
                    )

                    if not retryable:
                        raise CollectionError(
                            f"Unexpected HTTP status: {status}"
                        ) from exc

                except (
                    httpx.TimeoutException,
                    httpx.NetworkError,
                ):
                    logger.warning(
                        "Temporary network failure during collection."
                    )

                except httpx.RequestError as exc:
                    raise CollectionError(
                        "Unrecoverable HTTP request failure."
                    ) from exc

                if attempt < self.max_retries:
                    time.sleep(
                        self.retry_delay * (2 ** attempt)
                    )

        raise CollectionError(
            "CISA KEV collection failed after all attempts."
        )
