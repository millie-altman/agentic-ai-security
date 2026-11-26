
"""
ThreatLens JSON Storage

Persists validated intelligence snapshots using atomic
file replacement and SHA-256 integrity checksums.
"""

import hashlib
import json
import logging
import os
import tempfile

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from pydantic import TypeAdapter, ValidationError

from src.config_loader import PROJECT_ROOT

from src.schemas.intelligence import (
    CISACatalog,
    IntelligenceRecord,
)


logger = logging.getLogger(__name__)


class StorageError(Exception):
    """Raised when intelligence storage operations fail."""


class JSONStorage:
    """Manage local intelligence snapshots."""

    def __init__(self, data_directory: Path | None = None):

        self.data_directory = (
            Path(data_directory)
            if data_directory is not None
            else PROJECT_ROOT / "data"
        ).resolve()

        self.raw_directory = self.data_directory / "raw"
        self.processed_directory = (
            self.data_directory / "processed"
        )

        try:
            self.raw_directory.mkdir(
                parents=True,
                exist_ok=True,
            )

            self.processed_directory.mkdir(
                parents=True,
                exist_ok=True,
            )

        except OSError as exc:
            raise StorageError(
                "Unable to initialize storage directories."
            ) from exc

    def _validate_path(self, path: Path) -> Path:
        """Prevent storage operations outside the data directory."""

        resolved = path.resolve()

        if not resolved.is_relative_to(self.data_directory):
            raise StorageError(
                "Storage path is outside the approved directory."
            )

        return resolved

    def _generate_filename(self, prefix: str) -> str:
        """Generate a unique timestamped snapshot filename."""

        timestamp = datetime.now(timezone.utc).strftime(
            "%Y%m%dT%H%M%S%fZ"
        )

        return (
            f"{prefix}_{timestamp}_{uuid4().hex}.json"
        )

    def _atomic_write(
        self,
        path: Path,
        content: bytes,
    ) -> None:
        """Write a file without exposing partially written content."""

        path = self._validate_path(path)

        temporary_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=path.parent,
                delete=False,
            ) as temporary_file:

                temporary_path = Path(
                    temporary_file.name
                )

                temporary_file.write(content)
                temporary_file.flush()

                os.fsync(temporary_file.fileno())

            os.replace(temporary_path, path)

        except OSError as exc:
            raise StorageError(
                "Unable to write intelligence snapshot."
            ) from exc

        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    def _save_json(
        self,
        path: Path,
        payload: dict | list,
    ) -> Path:
        """Serialize and save intelligence with a checksum."""

        path = self._validate_path(path)

        content = json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")

        checksum = hashlib.sha256(content).hexdigest()

        checksum_path = path.with_suffix(".sha256")

        self._atomic_write(path, content)

        self._atomic_write(
            checksum_path,
            checksum.encode("ascii"),
        )

        logger.info(
            "Intelligence snapshot saved: %s",
            path.name,
        )

        return path

    def _load_json(self, path: Path) -> dict | list:
        """Load intelligence after verifying its checksum."""

        path = self._validate_path(Path(path))

        checksum_path = self._validate_path(
            path.with_suffix(".sha256")
        )

        try:
            content = path.read_bytes()

            expected_checksum = (
                checksum_path.read_text(
                    encoding="ascii"
                ).strip()
            )

        except (OSError, UnicodeError) as exc:
            raise StorageError(
                "Unable to read intelligence snapshot."
            ) from exc

        actual_checksum = hashlib.sha256(
            content
        ).hexdigest()

        if actual_checksum != expected_checksum:
            raise StorageError(
                "Intelligence snapshot integrity check failed."
            )

        try:
            return json.loads(content)

        except (ValueError, RecursionError) as exc:
            raise StorageError(
                "Invalid stored intelligence JSON."
            ) from exc

    def save_cisa_catalog(
        self,
        catalog: CISACatalog,
    ) -> Path:
        """Save a validated CISA source snapshot."""

        path = self.raw_directory / (
            self._generate_filename("cisa_kev")
        )

        return self._save_json(
            path,
            catalog.model_dump(mode="json"),
        )

    def save_intelligence(
        self,
        records: list[IntelligenceRecord],
    ) -> Path:
        """Save standardized intelligence records."""

        path = self.processed_directory / (
            self._generate_filename("intelligence")
        )

        payload = [
            record.model_dump(mode="json")
            for record in records
        ]

        return self._save_json(path, payload)

    def load_cisa_catalog(
        self,
        path: Path,
    ) -> CISACatalog:
        """Reload and validate a saved CISA catalog."""

        payload = self._load_json(path)

        try:
            catalog = CISACatalog.model_validate(payload)

        except ValidationError as exc:
            raise StorageError(
                "Stored CISA catalog failed validation."
            ) from exc

        if catalog.count != len(catalog.vulnerabilities):
            raise StorageError(
                "Stored catalog count mismatch."
            )

        return catalog

    def load_intelligence(
        self,
        path: Path,
    ) -> list[IntelligenceRecord]:
        """Reload and validate standardized intelligence."""

        payload = self._load_json(path)

        adapter = TypeAdapter(
            list[IntelligenceRecord]
        )

        try:
            return adapter.validate_python(payload)

        except ValidationError as exc:
            raise StorageError(
                "Stored intelligence failed validation."
            ) from exc
