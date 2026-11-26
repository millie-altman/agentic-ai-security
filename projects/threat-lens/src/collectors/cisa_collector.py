
"""
ThreatLens CISA KEV Collector

Retrieves and validates the CISA Known Exploited
Vulnerabilities catalog using controlled HTTP requests.

External intelligence is treated as untrusted data.
"""

import json
import logging
import re
import time

import httpx

from pydantic import ValidationError

from src.config_loader import (
    get_source,
    load_settings,
    validate_source_url,
    ConfigurationError,
)

from src.schemas.intelligence import CISACatalog


logger = logging.getLogger(__name__)


# Collection security limits

MAX_RETRY_DELAY_SECONDS = 60
MAX_RESPONSE_SIZE_BYTES = 50 * 1024 * 1024
STREAM_CHUNK_SIZE = 65536


class CollectionError(Exception):
    """Raised when intelligence collection fails."""


class ResponseValidationError(CollectionError):
    """Raised when an intelligence response is invalid."""


def reject_duplicate_keys(pairs: list[tuple]) -> dict:
    """Reject ambiguous JSON objects."""

    result = {}

    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key detected.")

        result[key] = value

    return result


def reject_invalid_constant(value: str):
    """Reject nonstandard JSON numeric constants."""

    raise ValueError("Invalid JSON numeric constant.")


class CISACollector:
    """Collect vulnerability intelligence from CISA KEV."""

    def __init__(self):

        self.source = get_source("cisa_kev")
        self.settings = load_settings()

        self.url = self.source["url"]

        collection = self.settings.get("collection")

        if not isinstance(collection, dict):
            raise ConfigurationError(
                "Invalid collection configuration."
            )

        self.timeout = collection.get(
            "request_timeout_seconds"
        )

        self.max_retries = collection.get(
            "max_retries"
        )

        self.retry_delay = collection.get(
            "retry_delay_seconds"
        )

        self.max_response_size = collection.get(
            "max_response_size_bytes"
        )

        self._validate_limits()

    def _validate_limits(self):
        """Validate resource consumption limits."""

        limits = {
            "timeout": (
                self.timeout,
                1,
                120,
            ),
            "max_retries": (
                self.max_retries,
                0,
                5,
            ),
            "retry_delay": (
                self.retry_delay,
                0,
                30,
            ),
            "max_response_size": (
                self.max_response_size,
                1,
                MAX_RESPONSE_SIZE_BYTES,
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

    def _validate_response_headers(
        self,
        response: httpx.Response,
    ) -> int | None:
        """Validate response metadata before reading content."""

        content_type = response.headers.get(
            "content-type",
            "",
        ).split(";")[0].strip().lower()

        if content_type != "application/json":
            raise ResponseValidationError(
                "Unexpected response content type."
            )

        content_encoding = response.headers.get(
            "content-encoding",
            "identity",
        ).strip().lower()

        if content_encoding != "identity":
            raise ResponseValidationError(
                "Compressed responses are prohibited."
            )

        content_length = response.headers.get(
            "content-length"
        )

        if content_length is None:
            return None

        if not re.fullmatch(
            r"[0-9]{1,20}",
            content_length,
        ):
            raise ResponseValidationError(
                "Invalid Content-Length header."
            )

        declared_size = int(content_length)

        if declared_size > self.max_response_size:
            raise ResponseValidationError(
                "Declared response size exceeds limits."
            )

        return declared_size

    def _download(self, client: httpx.Client) -> bytes:
        """Download a response while enforcing size limits."""

        with client.stream("GET", self.url) as response:

            response.raise_for_status()

            declared_size = (
                self._validate_response_headers(response)
            )

            data = bytearray()

            for chunk in response.iter_bytes(
                chunk_size=STREAM_CHUNK_SIZE
            ):

                if (
                    len(data) + len(chunk)
                    > self.max_response_size
                ):
                    raise ResponseValidationError(
                        "Response exceeded maximum allowed size."
                    )

                data.extend(chunk)

            if not data:
                raise ResponseValidationError(
                    "Empty intelligence response."
                )

            if (
                declared_size is not None
                and len(data) != declared_size
            ):
                raise ResponseValidationError(
                    "Response size does not match Content-Length."
                )

            return bytes(data)

    def _validate_catalog(
        self,
        data: bytes,
    ) -> CISACatalog:
        """Validate JSON structure and catalog consistency."""

        try:
            payload = json.loads(
                data,
                object_pairs_hook=reject_duplicate_keys,
                parse_constant=reject_invalid_constant,
            )

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

        cve_ids = [
            vulnerability.cveID
            for vulnerability in catalog.vulnerabilities
        ]

        if len(cve_ids) != len(set(cve_ids)):
            raise ResponseValidationError(
                "Duplicate CVE identifiers detected."
            )

        return catalog

    def _calculate_retry_delay(
        self,
        attempt: int,
    ) -> int:
        """Calculate bounded exponential backoff."""

        return min(
            self.retry_delay * (2 ** attempt),
            MAX_RETRY_DELAY_SECONDS,
        )

    def collect(self) -> CISACatalog:
        """Retrieve and validate the CISA KEV catalog."""

        self._validate_limits()

        validate_source_url(
            self.url,
            self.source.get("allowed_hosts", []),
        )

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

                    logger.warning(
                        "Retryable HTTP status received: %s",
                        status,
                    )

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

                    delay = self._calculate_retry_delay(
                        attempt
                    )

                    time.sleep(delay)

        raise CollectionError(
            "CISA KEV collection failed after all attempts."
        )
