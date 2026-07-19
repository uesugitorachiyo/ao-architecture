from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = ROOT / "stack" / "windows-qualification-coverage-ownership.json"
SCHEMA = "ao.architecture.windows-qualification-coverage-ownership.v0.1"
PROFILE_VERSION = "ao2.windows-stack-qualification.profiles.v1"
ALLOWED_OWNERS = {"hosted_native_windows", "physical_windows", "both"}
REQUIRED_INVARIANT_FIELDS = (
    "id",
    "description",
    "producing_repository",
    "canonical_owner",
    "required_inputs",
    "exact_head_bindings",
    "command_profile_shard_id",
    "failure_semantics",
    "downstream_consumer",
    "gate_status",
)


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_document(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA}")
    if document.get("status") != "active":
        errors.append("status must be active")
    if document.get("profile_version") != PROFILE_VERSION:
        errors.append(f"profile_version must be {PROFILE_VERSION}")
    if document.get("profile_digest") != document.get("expected_profile_digest"):
        errors.append("profile_digest must match expected_profile_digest")

    known_commands = document.get("known_commands")
    if not isinstance(known_commands, list) or not known_commands:
        errors.append("known_commands must be a non-empty array")
        known_command_set: set[str] = set()
    else:
        known_command_set = {command for command in known_commands if isinstance(command, str)}
        if len(known_command_set) != len(known_commands):
            errors.append("known_commands must contain unique string values")

    invariants = document.get("invariants")
    if not isinstance(invariants, list) or not invariants:
        errors.append("invariants must be a non-empty array")
        return errors

    seen_ids: set[str] = set()
    for index, invariant in enumerate(invariants):
        if not isinstance(invariant, dict):
            errors.append(f"invariants[{index}] must be an object")
            continue
        invariant_id = invariant.get("id")
        if non_empty_string(invariant_id):
            if invariant_id in seen_ids:
                errors.append(f"invariants[{index}].id must be unique")
            seen_ids.add(invariant_id)

        for field in REQUIRED_INVARIANT_FIELDS:
            if field == "canonical_owner":
                continue
            if field not in invariant:
                errors.append(f"invariants[{index}].{field} is required")

        owner = invariant.get("canonical_owner")
        if owner not in ALLOWED_OWNERS:
            errors.append(
                f"invariants[{index}].canonical_owner must be hosted_native_windows, physical_windows, or both"
            )
        elif owner == "both" and not non_empty_string(invariant.get("non_duplicate_reason")):
            errors.append(f"invariants[{index}].non_duplicate_reason is required when canonical_owner is both")

        command = invariant.get("command_profile_shard_id")
        if command not in known_command_set:
            errors.append(f"invariants[{index}].command_profile_shard_id must reference known_commands")

        if invariant.get("gate_status") != "required":
            errors.append(f"invariants[{index}].gate_status must be required")

        required_inputs = invariant.get("required_inputs")
        if not isinstance(required_inputs, list) or not required_inputs:
            errors.append(f"invariants[{index}].required_inputs must be a non-empty array")
        exact_heads = invariant.get("exact_head_bindings")
        if not isinstance(exact_heads, dict) or not exact_heads:
            errors.append(f"invariants[{index}].exact_head_bindings must be a non-empty object")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Windows qualification coverage ownership")
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    args = parser.parse_args()
    try:
        document = json.loads(args.contract.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"verify_windows_qualification_coverage_ownership.py: {exc}", file=sys.stderr)
        return 1
    errors = validate_document(document)
    if errors:
        for error in errors:
            print(f"verify_windows_qualification_coverage_ownership.py: {error}", file=sys.stderr)
        return 1
    print("verify_windows_qualification_coverage_ownership.py: contract verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
