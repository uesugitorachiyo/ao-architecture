from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "stack" / "contract-owner-registry.json"
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


def validate_document(document: dict[str, Any], expected_repositories: set[str] | None = None) -> list[str]:
    expected = expected_repositories or EXPECTED_REPOSITORIES
    errors: list[str] = []
    if document.get("schema") != "ao.architecture.contract-owner-registry.v0.1":
        errors.append("schema must be ao.architecture.contract-owner-registry.v0.1")
    if document.get("status") != "proposed":
        errors.append("status must remain proposed until compatibility gates pass")
    if document.get("registry_authority") != "ao-covenant":
        errors.append("registry_authority must be ao-covenant")
    if document.get("inventory_snapshot") != "stack/contract-inventory.json":
        errors.append("inventory_snapshot must point to stack/contract-inventory.json")

    assignments = document.get("assignments")
    if not isinstance(assignments, list) or not assignments:
        errors.append("assignments must be a non-empty array")
        assignments = []
    names: list[str] = []
    for index, entry in enumerate(assignments):
        if not isinstance(entry, dict):
            errors.append(f"assignments[{index}] must be an object")
            continue
        for field in ("repository", "contract_domain", "owner", "consumer_boundary"):
            if not isinstance(entry.get(field), str) or not entry[field]:
                errors.append(f"assignments[{index}].{field} is required")
        name = entry.get("repository")
        if isinstance(name, str) and name:
            names.append(name)
            if name not in expected:
                errors.append(f"assignments[{index}].repository is not an active repository")
        if entry.get("assignment_status") != "recorded_pending_compatibility_gate":
            errors.append(f"assignments[{index}].assignment_status must remain recorded_pending_compatibility_gate")

    actual = set(names)
    if missing := sorted(expected - actual):
        errors.append("missing repository assignments: " + ", ".join(missing))
    if len(names) != len(actual):
        errors.append("assignments must not contain duplicate repositories")

    coverage = document.get("coverage")
    if not isinstance(coverage, dict):
        errors.append("coverage is required")
    else:
        if coverage.get("repository_count") != len(expected):
            errors.append("coverage.repository_count must equal the expected repository count")
        if coverage.get("unclassified_repository_count") != 0:
            errors.append("coverage.unclassified_repository_count must be zero")
        if coverage.get("unclassified_schema_document_count") != 0:
            errors.append("coverage.unclassified_schema_document_count must be zero")

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
    parser = argparse.ArgumentParser(description="Validate proposed AO contract owner assignments")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    args = parser.parse_args()
    try:
        document = json.loads(args.registry.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"verify_contract_owner_registry.py: {exc}", file=sys.stderr)
        return 1
    errors = validate_document(document)
    if errors:
        for error in errors:
            print(f"verify_contract_owner_registry.py: {error}", file=sys.stderr)
        return 1
    print(f"verify_contract_owner_registry.py: validated {len(document['assignments'])} proposed repository owner assignments")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
