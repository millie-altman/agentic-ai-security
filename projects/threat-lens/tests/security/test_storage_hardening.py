
"""Security regression tests for intelligence storage."""

import hashlib
import json
from pathlib import Path

import pytest

from src.storage import json_storage

from src.storage.json_storage import (
    JSONStorage,
    StorageError,
)


@pytest.fixture
def storage(tmp_path):
    return JSONStorage(tmp_path / "data")


def write_snapshot(storage, content):
    """Create a synthetic snapshot with a valid checksum."""

    path = storage.processed_directory / "test.json"

    path.write_bytes(content)

    path.with_suffix(".sha256").write_text(
        hashlib.sha256(content).hexdigest(),
        encoding="ascii",
    )

    return path


def test_oversized_snapshot_read_rejected(
    storage,
    monkeypatch,
):
    path = write_snapshot(storage, b" " * 200)

    monkeypatch.setattr(
        json_storage,
        "MAX_SNAPSHOT_SIZE_BYTES",
        100,
    )

    with pytest.raises(StorageError, match="size"):
        storage.load_intelligence(path)


def test_oversized_snapshot_write_rejected(
    storage,
    monkeypatch,
):
    monkeypatch.setattr(
        json_storage,
        "MAX_SNAPSHOT_SIZE_BYTES",
        1,
    )

    with pytest.raises(StorageError, match="size"):
        storage.save_intelligence([])

    assert not list(storage.processed_directory.iterdir())


def test_oversized_checksum_rejected(storage):

    path = storage.save_intelligence([])

    path.with_suffix(".sha256").write_bytes(
        b"a" * 129
    )

    with pytest.raises(StorageError, match="size"):
        storage.load_intelligence(path)


@pytest.mark.parametrize(
    "checksum",
    [
        "",
        "abc",
        "g" * 64,
        "a" * 65,
    ],
)
def test_invalid_checksum_format_rejected(
    storage,
    checksum,
):
    path = storage.save_intelligence([])

    path.with_suffix(".sha256").write_text(
        checksum,
        encoding="ascii",
    )

    with pytest.raises(
        StorageError,
        match="checksum format",
    ):
        storage.load_intelligence(path)


def test_invalid_checksum_encoding_rejected(storage):

    path = storage.save_intelligence([])

    path.with_suffix(".sha256").write_bytes(
        b"\xff\xfe"
    )

    with pytest.raises(
        StorageError,
        match="checksum encoding",
    ):
        storage.load_intelligence(path)


def test_invalid_json_with_valid_checksum(storage):

    path = write_snapshot(
        storage,
        b"{invalid json",
    )

    with pytest.raises(StorageError, match="JSON"):
        storage.load_intelligence(path)


def test_duplicate_json_keys_rejected(storage):

    path = write_snapshot(
        storage,
        b'[{"human_reviewed": false, '
        b'"human_reviewed": true}]',
    )

    with pytest.raises(StorageError, match="JSON"):
        storage.load_intelligence(path)


@pytest.mark.parametrize(
    "constant",
    [
        "NaN",
        "Infinity",
        "-Infinity",
    ],
)
def test_invalid_json_constants_rejected(
    storage,
    constant,
):
    content = (
        f'[{{"value": {constant}}}]'
    ).encode("utf-8")

    path = write_snapshot(storage, content)

    with pytest.raises(StorageError, match="JSON"):
        storage.load_intelligence(path)


@pytest.mark.parametrize(
    "content",
    [
        b"null",
        b"true",
        b"123",
        b'"invalid"',
    ],
)
def test_invalid_json_root_rejected(
    storage,
    content,
):
    path = write_snapshot(storage, content)

    with pytest.raises(
        StorageError,
        match="structure",
    ):
        storage.load_intelligence(path)


def test_storage_initialization_failure(tmp_path):

    blocked_path = tmp_path / "blocked"

    blocked_path.write_text("not a directory")

    with pytest.raises(
        StorageError,
        match="initialize",
    ):
        JSONStorage(blocked_path)


def test_atomic_write_failure(
    storage,
    monkeypatch,
):
    def fail_replace(*args, **kwargs):
        raise PermissionError("Synthetic failure.")

    monkeypatch.setattr(
        json_storage.os,
        "replace",
        fail_replace,
    )

    with pytest.raises(StorageError, match="write"):
        storage.save_intelligence([])

    assert not list(storage.processed_directory.iterdir())


def test_checksum_write_failure_cleanup(
    storage,
    monkeypatch,
):
    original_write = storage._atomic_write

    def fail_checksum(path, content):

        if path.suffix == ".sha256":
            raise StorageError(
                "Synthetic checksum write failure."
            )

        return original_write(path, content)

    monkeypatch.setattr(
        storage,
        "_atomic_write",
        fail_checksum,
    )

    with pytest.raises(
        StorageError,
        match="checksum",
    ):
        storage.save_intelligence([])

    assert not list(storage.processed_directory.iterdir())


def test_invalid_stored_catalog_schema(storage):

    path = write_snapshot(
        storage,
        b'{"unexpected": "invalid catalog"}',
    )

    with pytest.raises(
        StorageError,
        match="validation",
    ):
        storage.load_cisa_catalog(path)


def test_stored_catalog_count_mismatch(storage):

    payload = {
        "title": "Synthetic Catalog",
        "catalogVersion": "2026.11.25",
        "dateReleased": "2026-11-25T12:00:00Z",
        "count": 1,
        "vulnerabilities": [],
    }

    path = write_snapshot(
        storage,
        json.dumps(payload).encode("utf-8"),
    )

    with pytest.raises(
        StorageError,
        match="count mismatch",
    ):
        storage.load_cisa_catalog(path)


def test_existing_snapshot_not_overwritten(
    storage,
    monkeypatch,
):
    path = storage.save_intelligence([])

    original_content = path.read_bytes()

    monkeypatch.setattr(
        storage,
        "_generate_filename",
        lambda prefix: path.name,
    )

    with pytest.raises(
        StorageError,
        match="already exists",
    ):
        storage.save_intelligence([])

    assert path.read_bytes() == original_content


def test_unserializable_payload_rejected(storage):

    path = storage.processed_directory / "invalid.json"

    with pytest.raises(
        StorageError,
        match="serialize",
    ):
        storage._save_json(
            path,
            {"invalid": object()},
        )

    assert not path.exists()


def test_snapshot_size_boundary(
    storage,
    monkeypatch,
):
    content = b"[]"

    path = write_snapshot(storage, content)

    monkeypatch.setattr(
        json_storage,
        "MAX_SNAPSHOT_SIZE_BYTES",
        len(content),
    )

    assert storage.load_intelligence(path) == []
