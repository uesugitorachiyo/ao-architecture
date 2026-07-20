#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WINDOW = ROOT / "stack" / "contract-compatibility-window.json"
DIRECTIONS = (
    "old_producer_to_new_consumer",
    "new_producer_to_old_consumer",
    "current_producer_to_current_consumer",
    "rollback_to_previous_supported_contract",
)
CHANGE_IDS = (
    "mission-lifecycle-correlation-additive-b02666e",
    "mission-objective-workflow-contract-v0.1-introduction",
    "ao2-github-draft-pr-v1-introduction",
    "mission-correlation-chain-v0.1-introduction",
    "mission-correlation-state-additive-7e7de94",
    "command-mission-status-correlation-additive-7cda85e",
)
ADDITIVE_IDS = {CHANGE_IDS[0], CHANGE_IDS[4], CHANGE_IDS[5]}
NO_PREDECESSOR_IDS = {CHANGE_IDS[1], CHANGE_IDS[2], CHANGE_IDS[3]}
TRUSTED_CHANGE_SET_DIGESTS = {
    CHANGE_IDS[0]: "2354db75f94e419b8ebe70e0bf2a3942b2f831e0ca37ec9c39bf62d396fa2582",
    CHANGE_IDS[1]: "11fe66ca8e85e9f11d96b2611489d6476f76a808698762fb38f1d09ad6dba0ca",
    CHANGE_IDS[2]: "6a7d03a74b047e3967bd1eb1eecc5a5bd53f60f7b3d2a86b42907ee83a7596f6",
    CHANGE_IDS[3]: "cb33e50d4bfbeb98fca52e15df9ae57c702ab2274e2366d11c6f15d25a2c8406",
    CHANGE_IDS[4]: "9de3cb6b7e5f987be1d313ccb4c805355c63b3e41b9d9caac4ada58e5d0ef284",
    CHANGE_IDS[5]: "69266053696b7465f394de3fcf6f6ddf86ed752d876e91a7820b68d0c1315581",
}
TOP_FIELDS = {
    "schema",
    "status",
    "policy",
    "minimum_supported_releases",
    "retirement_scheduled",
    "change_sets",
    "safety",
}
CHANGE_FIELDS = {
    "id",
    "kind",
    "status",
    "directions",
    "removal_policy",
}
DIRECTION_FIELDS = {"status", "meaning"}
REMOVAL_POLICY = (
    "later_version_deprecation_notice_two_release_window_and_executable_"
    "migration_evidence"
)


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_document(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if set(document) != TOP_FIELDS:
        errors.append("document fields must exactly match the strict schema")
    if document.get("schema") != "ao.architecture.contract-compatibility-window.v1":
        errors.append(
            "schema must be ao.architecture.contract-compatibility-window.v1"
        )
    if document.get("status") != "enforced":
        errors.append("status must be enforced")
    if document.get("policy") != "stack/contract-evolution-policy.json":
        errors.append("policy must identify the contract evolution policy")
    if document.get("minimum_supported_releases") != 2:
        errors.append("minimum_supported_releases must equal 2")
    if document.get("retirement_scheduled") is not False:
        errors.append("retirement_scheduled must be false")

    change_sets = document.get("change_sets")
    if not isinstance(change_sets, list):
        errors.append("change_sets is required")
        change_sets = []
    ids = [
        record.get("id")
        for record in change_sets
        if isinstance(record, dict)
    ]
    if ids != list(CHANGE_IDS):
        errors.append("change_sets must exactly list the six Month 3 records")
    for index, record in enumerate(change_sets):
        if not isinstance(record, dict):
            errors.append(f"change_sets[{index}] must be an object")
            continue
        if set(record) != CHANGE_FIELDS:
            errors.append(
                f"change_sets[{index}] fields must exactly match the strict schema"
            )
        record_id = str(record.get("id", f"change_sets[{index}]"))
        directions = record.get("directions")
        if not isinstance(directions, dict) or set(directions) != set(DIRECTIONS):
            errors.append(
                f"{record_id} directions must exactly match the four required directions"
            )
            directions = directions if isinstance(directions, dict) else {}
        for direction, result in directions.items():
            if not isinstance(result, dict) or set(result) != DIRECTION_FIELDS:
                errors.append(
                    f"{record_id} {direction} fields must exactly match the strict schema"
                )
                continue
            if not isinstance(result.get("meaning"), str) or not result["meaning"]:
                errors.append(f"{record_id} {direction} meaning is required")
        if record.get("removal_policy") != REMOVAL_POLICY:
            errors.append(f"{record_id} removal_policy must preserve the two-release window")
        if TRUSTED_CHANGE_SET_DIGESTS.get(record_id) != _digest(record):
            errors.append(f"{record_id} must match the trusted compatibility statement")

        if record_id in ADDITIVE_IDS:
            if record.get("kind") != "additive_optional_same_version":
                errors.append(f"{record_id} kind must be additive_optional_same_version")
            if record.get("status") != "directional_evidence_incomplete":
                errors.append(f"{record_id} status must be directional_evidence_incomplete")
            for direction in DIRECTIONS:
                expected = (
                    "not_demonstrated"
                    if direction == "new_producer_to_old_consumer"
                    or (
                        direction == "old_producer_to_new_consumer"
                        and record_id != CHANGE_IDS[5]
                    )
                    else "passed"
                )
                if directions.get(direction, {}).get("status") != expected:
                    errors.append(f"{record_id} {direction} must be {expected}")
        elif record_id in NO_PREDECESSOR_IDS:
            expected_kind = (
                "new_contract_no_predecessor"
                if record_id == CHANGE_IDS[1]
                else "new_contract_family_no_predecessor"
            )
            if record.get("kind") != expected_kind:
                errors.append(f"{record_id} kind must be {expected_kind}")
            if record.get("status") != "current_pair_only":
                errors.append(f"{record_id} status must be current_pair_only")
            for direction in (
                "old_producer_to_new_consumer",
                "new_producer_to_old_consumer",
                "rollback_to_previous_supported_contract",
            ):
                if (
                    directions.get(direction, {}).get("status")
                    != "not_applicable_no_predecessor"
                ):
                    errors.append(
                        f"{record_id} {direction} must be "
                        "not_applicable_no_predecessor"
                    )
            if (
                directions.get("current_producer_to_current_consumer", {}).get(
                    "status"
                )
                != "passed"
            ):
                errors.append(f"{record_id} current pair must be passed")

    safety = document.get("safety")
    expected_safety = {
        "activates_compatibility_gate": False,
        "grants_release_authority": False,
        "invents_predecessors": False,
    }
    if safety != expected_safety:
        errors.append("safety must preserve the bounded Month 3 authority")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the AO contract compatibility window"
    )
    parser.add_argument("--window", type=Path, default=DEFAULT_WINDOW)
    args = parser.parse_args()
    try:
        document = json.loads(args.window.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"verify_contract_compatibility_window.py: {error}", file=sys.stderr)
        return 1
    errors = validate_document(document)
    if errors:
        for error in errors:
            print(f"verify_contract_compatibility_window.py: {error}", file=sys.stderr)
        return 1
    print(
        "verify_contract_compatibility_window.py: validated 6 Month 3 change sets"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
