#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = ROOT / "stack" / "execution-observation-version-skew.json"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_IDS = ["predecessor_public_pair", "current_public_pair", "current_source_candidate"]
EXPECTED_PAIRS = {
    "predecessor_public_pair": ("v0.5.1", "80ec5321f42d4bab17d5e64fdae6aa099ba59d4a", "v0.1.16", "f4f5fea9fefa1081cebcbabac550b0e08b9f0e3d", "supported"),
    "current_public_pair": ("v0.5.10", "9f4f8a8cf596127a982627b4af25c90a9a842095", "v0.1.19", "5de3541e9007e12d95b125e7f911c02932e21479", "supported"),
    "current_source_candidate": ("v0.5.11", "8307795b3434af920f6cef088e56ca8fcc76775b", "v0.1.19", "4e41da173dc9f1ee37f4ae99b85791e5f05ea453", "supported_by_unchanged_bridge"),
}
EXPECTED_EVIDENCE = {
    "producer_path": "tests/fixtures/compatibility/ao2-execution-receipt-v0.5.10.json",
    "producer_merge_commit": "8307795b3434af920f6cef088e56ca8fcc76775b",
    "producer_sha256": "fd7260329ea3c436436cd1572cba5abda72f5a9959b1157d5e61f595ae91857e",
    "consumer_test_path": "crates/ao2-cp-server/tests/compatibility_vectors.rs",
    "consumer_merge_commit": "4e41da173dc9f1ee37f4ae99b85791e5f05ea453",
    "consumer_test_sha256": "d1c7fc2ada7634bb2e98eb4c885fab8d117c4f273793988a848ecba23860b365",
}
EXPECTED_GENERATED_AT = "2026-08-14T03:55:26Z"
EXPECTED_VALID_UNTIL = "2026-08-15T03:55:26Z"
EXPECTED_FIELDS = {
    "schema", "status", "generated_at", "valid_until", "contract", "evidence", "pairs", "boundaries"
}
PAIR_FIELDS = {
    "id", "ao2_version", "ao2_source_sha", "control_plane_version", "control_plane_source_sha", "status"
}
FALSE_BOUNDARIES = {
    "approves_execution", "permits_release", "mutates_repositories", "calls_providers",
    "creates_tags", "uploads_assets", "deploys"
}
MAX_CONTRACT_BYTES = 1_048_576


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result


def read_strict_json(path: Path) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise ValueError("contract must be a regular non-symlink file")
    raw = path.read_bytes()
    if len(raw) > MAX_CONTRACT_BYTES:
        raise ValueError("contract exceeds the 1048576-byte limit")
    value = json.loads(raw, object_pairs_hook=reject_duplicate_keys)
    if not isinstance(value, dict):
        raise ValueError("contract must be a JSON object")
    return value


def parse_timestamp(value: Any, label: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str) or not value.endswith("Z"):
        errors.append(f"{label} must be an RFC3339 UTC timestamp")
        return None
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        errors.append(f"{label} must be an RFC3339 UTC timestamp")
        return None


def validate_contract(contract: dict[str, Any], now: datetime) -> list[str]:
    errors: list[str] = []
    if set(contract) != EXPECTED_FIELDS:
        errors.append("top-level fields must exactly match the strict schema")
    if contract.get("schema") != "ao.architecture.execution-observation-version-skew.v1":
        errors.append("unsupported schema")
    if contract.get("status") != "current":
        errors.append("status must be current")

    generated = parse_timestamp(contract.get("generated_at"), "generated_at", errors)
    expires = parse_timestamp(contract.get("valid_until"), "valid_until", errors)
    if contract.get("generated_at") != EXPECTED_GENERATED_AT:
        errors.append("generated_at must match the bound compatibility vector")
    if contract.get("valid_until") != EXPECTED_VALID_UNTIL:
        errors.append("valid_until must match the bound compatibility vector")
    if generated and expires and not generated < expires:
        errors.append("valid_until must be after generated_at")
    if generated and generated > now:
        errors.append("generated_at cannot be in the future")
    if expires and now >= expires:
        errors.append("compatibility evidence is stale")

    schemas = contract.get("contract")
    if schemas != {
        "producer_schema": "ao2.execution-receipt.v1",
        "consumer_schema": "ao2-control-plane.evidence-event.v1",
        "change": "unchanged",
    }:
        errors.append("contract schemas and unchanged classification must match")

    evidence = contract.get("evidence")
    required_evidence = {
        "producer_path", "producer_merge_commit", "producer_sha256",
        "consumer_test_path", "consumer_merge_commit", "consumer_test_sha256"
    }
    if not isinstance(evidence, dict) or set(evidence) != required_evidence:
        errors.append("evidence fields must exactly match the strict schema")
    else:
        if evidence != EXPECTED_EVIDENCE:
            errors.append("evidence must match the exact current producer and consumer files")
        for field in ("producer_merge_commit", "consumer_merge_commit"):
            if not SHA_RE.fullmatch(str(evidence.get(field, ""))):
                errors.append(f"evidence.{field} must be a full source SHA")
        for field in ("producer_sha256", "consumer_test_sha256"):
            if not DIGEST_RE.fullmatch(str(evidence.get(field, ""))):
                errors.append(f"evidence.{field} must be a SHA-256 digest")

    pairs = contract.get("pairs")
    if not isinstance(pairs, list) or [pair.get("id") for pair in pairs if isinstance(pair, dict)] != EXPECTED_IDS:
        errors.append("pairs must cover predecessor, current public, and current source candidate in order")
    else:
        for index, pair in enumerate(pairs):
            if not isinstance(pair, dict) or set(pair) != PAIR_FIELDS:
                errors.append(f"pairs[{index}] fields must exactly match the strict schema")
                continue
            if pair.get("status") not in {"supported", "supported_by_unchanged_bridge"}:
                errors.append(f"pairs[{index}] has unsupported skew")
            expected = EXPECTED_PAIRS.get(str(pair.get("id")))
            actual = (
                pair.get("ao2_version"), pair.get("ao2_source_sha"),
                pair.get("control_plane_version"), pair.get("control_plane_source_sha"), pair.get("status")
            )
            if expected != actual:
                errors.append(f"pairs[{index}] does not match the verified version-skew binding")
            for field in ("ao2_source_sha", "control_plane_source_sha"):
                if not SHA_RE.fullmatch(str(pair.get(field, ""))):
                    errors.append(f"pairs[{index}].{field} must be a full source SHA")
            for field in ("ao2_version", "control_plane_version"):
                if not re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+", str(pair.get(field, ""))):
                    errors.append(f"pairs[{index}].{field} must be a release version")

    boundaries = contract.get("boundaries")
    if not isinstance(boundaries, dict) or set(boundaries) != FALSE_BOUNDARIES:
        errors.append("boundaries fields must exactly match the strict schema")
    elif any(boundaries.values()):
        errors.append("compatibility evidence cannot grant authority")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--now", help="RFC3339 UTC timestamp for deterministic verification")
    args = parser.parse_args()
    try:
        contract = read_strict_json(args.contract)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"verify_execution_observation_version_skew.py: {exc}")
        return 1
    now = datetime.now(timezone.utc)
    if args.now:
        parsed: list[str] = []
        value = parse_timestamp(args.now, "now", parsed)
        if parsed or value is None:
            print("verify_execution_observation_version_skew.py: now must be an RFC3339 UTC timestamp")
            return 1
        now = value
    errors = validate_contract(contract, now)
    for error in errors:
        print(f"verify_execution_observation_version_skew.py: {error}")
    if errors:
        return 1
    print("verify_execution_observation_version_skew.py: 3 supported pairs; evidence current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
