#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = ROOT / "stack" / "compact-evidence-contract.json"
DEFAULT_FIXTURE = ROOT / "stack" / "fixtures" / "compact-evidence" / "valid-manifest-v0.1.json"
EXPECTED_REQUIREMENTS = {
    "versioned_manifest",
    "ordered_bounded_chunks",
    "deterministic_canonical_serialization",
    "chunk_and_total_record_counts",
    "first_and_last_record_id_per_chunk",
    "sha256_digest_per_chunk",
    "aggregate_manifest_digest",
    "unique_record_ids",
    "stable_record_ordering",
    "streaming_verification",
    "deterministic_lookup",
    "no_absolute_machine_local_paths",
    "no_credentials_or_private_values",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def require_bool(errors: list[str], document: dict[str, Any], path: str, expected: bool) -> None:
    current: Any = document
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            errors.append(f"{path} must be {str(expected).lower()}")
            return
        current = current[part]
    if current is not expected:
        errors.append(f"{path} must be {str(expected).lower()}")


def is_safe_relative_path(path: Any) -> bool:
    if not isinstance(path, str) or not path:
        return False
    candidate = Path(path)
    if candidate.is_absolute():
        return False
    if "\\" in path:
        return False
    return ".." not in candidate.parts


def validate_contract_document(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != "ao.architecture.compact-evidence-contract.v0.1":
        errors.append("schema must be ao.architecture.compact-evidence-contract.v0.1")
    if document.get("status") != "proposed":
        errors.append("status must remain proposed until all consumers are compatible")
    if document.get("format_version") != "v0.1":
        errors.append("format_version must be v0.1")
    if document.get("owner") != "ao-architecture":
        errors.append("owner must be ao-architecture")

    requirements = document.get("requirements")
    if not isinstance(requirements, list):
        errors.append("requirements must be an array")
        requirements = []
    for requirement in sorted(EXPECTED_REQUIREMENTS - set(requirements)):
        errors.append(f"requirements missing {requirement}")
    for requirement in sorted(set(requirements) - EXPECTED_REQUIREMENTS):
        errors.append(f"requirements unexpected {requirement}")

    if document.get("standard_input_sizes") != [100, 1000, 10000]:
        errors.append("standard_input_sizes must be [100, 1000, 10000]")
    if not isinstance(document.get("high_cardinality_fixture_floor"), int) or document["high_cardinality_fixture_floor"] < 9000:
        errors.append("high_cardinality_fixture_floor must be at least 9000")
    chunk_max = document.get("bounded_chunk_max_records")
    if not isinstance(chunk_max, int) or chunk_max < 1 or chunk_max > 1000:
        errors.append("bounded_chunk_max_records must be between 1 and 1000")
    if document.get("record_ordering") != "stable_lexicographic_record_id":
        errors.append("record_ordering must be stable_lexicographic_record_id")
    if document.get("lookup") != "ordered_chunk_ranges":
        errors.append("lookup must be ordered_chunk_ranges")

    require_bool(errors, document, "compatibility.legacy_per_file_evidence_supported", True)
    require_bool(errors, document, "compatibility.compact_and_legacy_records_equivalent", True)
    require_bool(errors, document, "compatibility.generators_compact_only_after_consumers_compatible", True)
    require_bool(errors, document, "measurement.report_file_count_before_after", True)
    require_bool(errors, document, "measurement.report_byte_count_before_after", True)
    require_bool(errors, document, "measurement.report_verifier_memory_before_after", True)
    require_bool(errors, document, "measurement.report_verification_time_before_after", True)
    require_bool(errors, document, "measurement.generate_large_fixtures_in_excluded_evidence_directory", True)
    require_bool(errors, document, "safety.allow_absolute_machine_local_paths", False)
    require_bool(errors, document, "safety.allow_credentials_or_private_values", False)
    require_bool(errors, document, "safety.promotion_granted", False)
    require_bool(errors, document, "safety.rsi_remains_denied", True)
    require_bool(errors, document, "safety.release_claim_made_by_contract", False)
    return errors


def load_fixture_chunks(manifest_path: Path) -> dict[str, bytes]:
    manifest = json.loads(manifest_path.read_text())
    chunks: dict[str, bytes] = {}
    for chunk in manifest.get("chunks", []):
        path = chunk.get("path")
        if is_safe_relative_path(path):
            chunks[path] = (manifest_path.parent / path).read_bytes()
    return chunks


def parse_chunk_records(errors: list[str], path: str, body: bytes) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(body.splitlines(), start=1):
        if not raw_line.strip():
            continue
        try:
            record = json.loads(raw_line)
        except json.JSONDecodeError:
            errors.append(f"{path} line {line_number} malformed JSON")
            continue
        if not isinstance(record, dict):
            errors.append(f"{path} line {line_number} malformed record")
            continue
        record_id = record.get("record_id")
        if not isinstance(record_id, str) or not record_id:
            errors.append(f"{path} line {line_number} record_id is required")
            continue
        records.append(record)
    return records


def validate_compact_manifest(manifest: dict[str, Any], chunks: dict[str, bytes]) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema") != "ao.architecture.compact-evidence-manifest.v0.1":
        errors.append("schema must be ao.architecture.compact-evidence-manifest.v0.1")
    if manifest.get("format_version") != "v0.1":
        errors.append("format_version must be v0.1")

    chunk_entries = manifest.get("chunks")
    if not isinstance(chunk_entries, list) or not chunk_entries:
        errors.append("chunks must be a non-empty array")
        chunk_entries = []
    chunk_order = manifest.get("chunk_order")
    if not isinstance(chunk_order, list) or not all(isinstance(path, str) for path in chunk_order):
        errors.append("chunk_order must be an array of chunk paths")
        chunk_order = []
    declared_paths = [entry.get("path") for entry in chunk_entries if isinstance(entry, dict)]
    if chunk_order and declared_paths and chunk_order != declared_paths:
        errors.append("chunk_order must match manifest chunk order")

    declared_path_set = {path for path in declared_paths if isinstance(path, str)}
    for path in sorted(set(chunks) - declared_path_set):
        errors.append(f"{path} is not declared by manifest")

    all_record_ids: set[str] = set()
    previous_record_id = ""
    total_records = 0
    previous_error_count = len(errors)

    for index, entry in enumerate(chunk_entries):
        if not isinstance(entry, dict):
            errors.append(f"chunks[{index}] must be an object")
            continue
        path = entry.get("path")
        if not is_safe_relative_path(path):
            errors.append(f"chunks[{index}].path must be a safe relative path")
            continue
        if path not in chunks:
            errors.append(f"{path} is missing")
            continue
        body = chunks[path]
        expected_digest = entry.get("sha256")
        if not isinstance(expected_digest, str) or not SHA256_RE.fullmatch(expected_digest):
            errors.append(f"{path} sha256 must be a lowercase SHA-256 digest")
        elif hashlib.sha256(body).hexdigest() != expected_digest:
            errors.append(f"{path} sha256 mismatch")

        chunk_errors_before = len(errors)
        records = parse_chunk_records(errors, path, body)
        if len(errors) != chunk_errors_before:
            continue

        total_records += len(records)
        if entry.get("record_count") != len(records):
            errors.append(f"{path} record_count mismatch")
        first_record_id = records[0]["record_id"] if records else ""
        last_record_id = records[-1]["record_id"] if records else ""
        if entry.get("first_record_id") != first_record_id:
            errors.append(f"{path} first_record_id mismatch")
        if entry.get("last_record_id") != last_record_id:
            errors.append(f"{path} last_record_id mismatch")

        for record in records:
            record_id = record["record_id"]
            if record_id in all_record_ids:
                errors.append(f"duplicate record_id {record_id}")
            if previous_record_id and record_id <= previous_record_id:
                errors.append(f"record_id {record_id} is out of order")
            all_record_ids.add(record_id)
            previous_record_id = record_id

    if manifest.get("total_record_count") != total_records:
        errors.append("total_record_count mismatch")

    lookup = manifest.get("lookup")
    if not isinstance(lookup, dict) or lookup.get("strategy") != "ordered_chunk_ranges":
        errors.append("lookup.strategy must be ordered_chunk_ranges")
    else:
        ranges = lookup.get("ranges")
        if not isinstance(ranges, list):
            errors.append("lookup.ranges must be an array")
        elif len(ranges) != len(chunk_entries):
            errors.append("lookup.ranges must match chunk count")
        else:
            for index, (entry, lookup_range) in enumerate(zip(chunk_entries, ranges)):
                if not isinstance(entry, dict) or not isinstance(lookup_range, dict):
                    errors.append(f"lookup.ranges[{index}] must match chunk metadata")
                    continue
                if lookup_range.get("chunk") != entry.get("path"):
                    errors.append(f"lookup.ranges[{index}].chunk mismatch")
                if lookup_range.get("first_record_id") != entry.get("first_record_id"):
                    errors.append(f"lookup.ranges[{index}].first_record_id mismatch")
                if lookup_range.get("last_record_id") != entry.get("last_record_id"):
                    errors.append(f"lookup.ranges[{index}].last_record_id mismatch")

    manifest_digest = manifest.get("manifest_digest")
    if not isinstance(manifest_digest, str) or not SHA256_RE.fullmatch(manifest_digest):
        errors.append("manifest_digest must be a lowercase SHA-256 digest")
    else:
        digestable = dict(manifest)
        digestable["manifest_digest"] = ""
        if hashlib.sha256(canonical_json(digestable)).hexdigest() != manifest_digest:
            errors.append("manifest_digest mismatch")

    if previous_error_count == len(errors) and len(all_record_ids) != total_records:
        errors.append("record IDs must be unique")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the AO compact evidence contract and fixture manifest")
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_FIXTURE)
    args = parser.parse_args()
    try:
        contract = json.loads(args.contract.read_text())
        manifest = json.loads(args.manifest.read_text())
        chunks = load_fixture_chunks(args.manifest)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"verify_compact_evidence_contract.py: {exc}", file=sys.stderr)
        return 1

    errors = validate_contract_document(contract)
    errors.extend(validate_compact_manifest(manifest, chunks))
    if errors:
        for error in errors:
            print(f"verify_compact_evidence_contract.py: {error}", file=sys.stderr)
        return 1
    print("verify_compact_evidence_contract.py: compact evidence contract and fixture verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
