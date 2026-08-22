#!/usr/bin/env python3
"""Independently rehash hosted baseline and cleanup results."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any


class RehashError(ValueError):
    pass


def load_regular_json(path: Path) -> tuple[dict[str, Any], str, int]:
    if path.is_symlink() or not path.is_file():
        raise RehashError(f"unsafe input: {path.name}")
    body = path.read_bytes()
    if len(body) > 2 * 1024 * 1024:
        raise RehashError(f"oversized input: {path.name}")
    try:
        document = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RehashError(f"invalid input: {path.name}") from exc
    if not isinstance(document, dict):
        raise RehashError(f"input must be an object: {path.name}")
    return document, hashlib.sha256(body).hexdigest(), len(body)


def build_report(host_dir: Path, cleanup_dir: Path, source_commit: str) -> dict[str, Any]:
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise RehashError("source commit is invalid")
    host_paths = sorted(host_dir.glob("*.json"))
    cleanup_paths = sorted(cleanup_dir.glob("*.json"))
    if len(host_paths) != 2 or len(cleanup_paths) != 2:
        raise RehashError("expected two host and two cleanup results")
    identities: set[str] = set()
    hosts: list[dict[str, Any]] = []
    cleanups: list[dict[str, Any]] = []
    for path in host_paths:
        document, digest, size = load_regular_json(path)
        if document.get("controller_source_commit") != source_commit:
            raise RehashError("host source commit mismatch")
        if document.get("status") != "pass":
            raise RehashError("host result did not pass")
        if len(document.get("repositories", [])) != 14 or len(document.get("runtime_assets", [])) != 7:
            raise RehashError("host result count mismatch")
        if any(item.get("expected_sha256") != item.get("actual_sha256") for item in document["runtime_assets"]):
            raise RehashError("host runtime digest mismatch")
        if any(value is not False for value in document.get("authority", {}).values()):
            raise RehashError("host authority drift")
        identities.add(document.get("baseline_identity", ""))
        hosts.append({"name": path.name, "sha256": digest, "bytes": size})
    if len(identities) != 1:
        raise RehashError("host baseline identity mismatch")
    for path in cleanup_paths:
        document, digest, size = load_regular_json(path)
        if document.get("source_commit") != source_commit:
            raise RehashError("cleanup source commit mismatch")
        if document.get("cleanup_status") != "root_absent":
            raise RehashError("cleanup root is not absent")
        cleanups.append({"name": path.name, "sha256": digest, "bytes": size})
    return {
        "schema": "ao.architecture.development-baseline-rehash.v1",
        "source_commit": source_commit,
        "baseline_identity": identities.pop(),
        "hosts": hosts,
        "cleanups": cleanups,
        "missing": 0,
        "extra": 0,
        "size_mismatches": 0,
        "digest_mismatches": 0,
        "status": "pass",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host-dir", required=True, type=Path)
    parser.add_argument("--cleanup-dir", required=True, type=Path)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--result", required=True, type=Path)
    args = parser.parse_args()
    try:
        report = build_report(args.host_dir, args.cleanup_dir, args.source_commit)
        args.result.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    except (OSError, RehashError) as exc:
        print(f"error={exc}", file=sys.stderr)
        return 1
    print("errors=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
