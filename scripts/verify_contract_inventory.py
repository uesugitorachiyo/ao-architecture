from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INVENTORY = ROOT / "stack" / "contract-inventory.json"
EXPECTED_REPOSITORIES = {
    "ao-architecture",
    "ao-mission",
    "ao-blueprint",
    "ao-atlas",
    "ao-foundry",
    "ao-forge",
    "ao-covenant",
    "ao2",
    "ao2-control-plane",
    "ao-command",
    "ao-arena",
    "ao-crucible",
    "ao-sentinel",
    "ao-promoter",
}
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def validate_document(document: dict[str, Any], expected_repositories: set[str] | None = None) -> list[str]:
    expected = expected_repositories or EXPECTED_REPOSITORIES
    errors: list[str] = []
    if document.get("schema") != "ao.architecture.contract-inventory.v0.1":
        errors.append("schema must be ao.architecture.contract-inventory.v0.1")
    if document.get("status") != "baseline":
        errors.append("status must be baseline")
    if document.get("snapshot_source") != "checked_out_repositories":
        errors.append("snapshot_source must be checked_out_repositories")

    repositories = document.get("repositories")
    if not isinstance(repositories, list) or not repositories:
        errors.append("repositories must be a non-empty array")
        repositories = []
    names: list[str] = []
    sums = {"schema_document_count": 0, "schema_version_literal_count": 0}
    for index, entry in enumerate(repositories):
        if not isinstance(entry, dict):
            errors.append(f"repositories[{index}] must be an object")
            continue
        name = entry.get("repository")
        if not isinstance(name, str) or not name:
            errors.append(f"repositories[{index}].repository is required")
        else:
            names.append(name)
        commit = entry.get("snapshot_commit")
        if not isinstance(commit, str) or not COMMIT_PATTERN.fullmatch(commit):
            errors.append(f"repositories[{index}].snapshot_commit must be a 40-character commit")
        if not isinstance(entry.get("branch"), str) or not entry["branch"]:
            errors.append(f"repositories[{index}].branch is required")
        for field in ("schema_document_count", "schema_version_literal_count", "distinct_schema_version_count"):
            value = entry.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                errors.append(f"repositories[{index}].{field} must be a non-negative integer")
            elif field != "distinct_schema_version_count":
                sums[field] += value
        if entry.get("contract_owner_status") != "pending_owner_assignment":
            errors.append(f"repositories[{index}].contract_owner_status must remain pending_owner_assignment")
        if entry.get("proposed_registry_owner") != "ao-covenant":
            errors.append(f"repositories[{index}].proposed_registry_owner must be ao-covenant")

    actual = set(names)
    if missing := sorted(expected - actual):
        errors.append("missing repositories: " + ", ".join(missing))
    if extra := sorted(actual - expected):
        errors.append("unexpected repositories: " + ", ".join(extra))
    if len(names) != len(actual):
        errors.append("repositories must not contain duplicates")

    totals = document.get("totals")
    if not isinstance(totals, dict):
        errors.append("totals is required")
    else:
        for field in ("schema_document_count", "schema_version_literal_count", "distinct_schema_version_count"):
            if not isinstance(totals.get(field), int) or isinstance(totals[field], bool) or totals[field] < 0:
                errors.append(f"totals.{field} must be a non-negative integer")
        for field in sums:
            if totals.get(field) != sums[field]:
                errors.append(f"totals.{field} must equal the repository sum")
        if totals.get("distinct_schema_version_count", 0) <= 0:
            errors.append("totals.distinct_schema_version_count must be positive")

    safety = document.get("safety")
    if not isinstance(safety, dict):
        errors.append("safety is required")
    else:
        if safety.get("promotion_granted") is not False:
            errors.append("promotion_granted must remain false")
        if safety.get("rsi_remains_denied") is not True:
            errors.append("rsi_remains_denied must remain true")
        if safety.get("migration_started") is not False:
            errors.append("migration_started must remain false")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the AO stack contract inventory baseline")
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    args = parser.parse_args()
    try:
        document = json.loads(args.inventory.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"verify_contract_inventory.py: {exc}", file=sys.stderr)
        return 1
    errors = validate_document(document)
    if errors:
        for error in errors:
            print(f"verify_contract_inventory.py: {error}", file=sys.stderr)
        return 1
    print(f"verify_contract_inventory.py: validated {len(document['repositories'])} repository contract baselines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
