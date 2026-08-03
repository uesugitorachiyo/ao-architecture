from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


PREFIX = b"AO_RUST_BUILD_PROVENANCE_V1\x00"
TERMINATOR = b"\x00"
MAX_BINARY_BYTES = 256 << 20
MAX_MARKER_BYTES = 4096
REQUIRED_FIELDS = {
    "build_profile",
    "cargo_lock_sha256",
    "repository",
    "source_sha",
    "source_modified",
    "target",
    "version",
}


class RustProvenanceError(ValueError):
    pass


def strict_object(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise RustProvenanceError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def normalize_rust_metadata(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != REQUIRED_FIELDS:
        raise RustProvenanceError("Rust binary provenance fields are invalid")
    string_fields = REQUIRED_FIELDS - {"source_modified"}
    if any(not isinstance(value[field], str) or not value[field] for field in string_fields):
        raise RustProvenanceError("Rust binary provenance values must be non-empty strings")
    if value["source_modified"] is not False:
        raise RustProvenanceError("Rust binary provenance requires a clean source")
    if value["build_profile"] != "release":
        raise RustProvenanceError("Rust binary build profile must be release")
    source_sha = value["source_sha"]
    if len(source_sha) != 40 or any(character not in "0123456789abcdef" for character in source_sha):
        raise RustProvenanceError("Rust binary source SHA must be lowercase Git SHA-1")
    lock_digest = value["cargo_lock_sha256"]
    if len(lock_digest) != 64 or any(character not in "0123456789abcdef" for character in lock_digest):
        raise RustProvenanceError("Rust binary Cargo.lock SHA-256 is invalid")
    for field in ("repository", "target", "version"):
        if len(value[field]) > 128 or not value[field].isascii():
            raise RustProvenanceError(f"Rust binary {field} must be bounded ASCII")
    return {field: value[field] for field in sorted(REQUIRED_FIELDS)}


def read_rust_binary_metadata(path: Path) -> dict[str, Any]:
    size = path.stat().st_size
    if size < len(PREFIX) + 2 or size > MAX_BINARY_BYTES:
        raise RustProvenanceError("Rust binary size is invalid")
    data = path.read_bytes()
    offsets: list[int] = []
    cursor = 0
    while True:
        offset = data.find(PREFIX, cursor)
        if offset < 0:
            break
        offsets.append(offset)
        cursor = offset + len(PREFIX)
    if len(offsets) != 1:
        raise RustProvenanceError("Rust binary must contain exactly one provenance marker")
    start = offsets[0] + len(PREFIX)
    end = data.find(TERMINATOR, start, start + MAX_MARKER_BYTES + 1)
    if end < 0:
        raise RustProvenanceError("Rust binary provenance marker is unterminated")
    try:
        value = json.loads(data[start:end].decode("ascii"), object_pairs_hook=strict_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RustProvenanceError(f"Rust binary provenance marker is malformed: {exc}") from exc
    return normalize_rust_metadata(value)


def validate_rust_provenance(
    metadata: dict[str, Any],
    repository: str,
    source_sha: str,
    version: str,
    target: str,
    cargo_lock_sha256: str | None = None,
) -> dict[str, Any]:
    normalized = normalize_rust_metadata(metadata)
    expected = {
        "build_profile": "release",
        "cargo_lock_sha256": cargo_lock_sha256 or normalized["cargo_lock_sha256"],
        "repository": repository,
        "source_sha": source_sha,
        "source_modified": False,
        "target": target,
        "version": version,
    }
    if normalized != expected:
        raise RustProvenanceError("Rust binary provenance does not match expected identity")
    return normalized
