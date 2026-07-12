from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CLASSIFICATION = ROOT / "stack" / "copied-schema-classification.json"
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
COUNT_FIELDS = (
    "schema_document_count_from_inventory",
    "stable_schema_document_count",
    "experimental_schema_document_count",
    "deprecated_schema_document_count",
)
ALLOWED_CLASSES = {"stable", "experimental", "deprecated"}
ALLOWED_STATUSES = {
    "stable_registry_authority",
    "experimental_pending_covenant_registry",
    "deprecated_retained_for_compatibility",
    "no_schema_documents",
}


def validate_document(document: dict[str, Any], expected_repositories: set[str] | None = None) -> list[str]:
    expected = expected_repositories or EXPECTED_REPOSITORIES
    errors: list[str] = []
    if document.get("schema") != "ao.architecture.copied-schema-classification.v0.1":
        errors.append("schema must be ao.architecture.copied-schema-classification.v0.1")
    if document.get("status") != "classified_pending_covenant_registry":
        errors.append("status must remain classified_pending_covenant_registry")
    if document.get("registry_authority") != "ao-covenant":
        errors.append("registry_authority must be ao-covenant")
    if document.get("inventory_snapshot") != "stack/contract-inventory.json":
        errors.append("inventory_snapshot must point to stack/contract-inventory.json")

    policy = document.get("classification_policy")
    if not isinstance(policy, dict):
        errors.append("classification_policy is required")
    else:
        allowed = policy.get("allowed_classes")
        if not isinstance(allowed, list) or set(allowed) != ALLOWED_CLASSES:
            errors.append("classification_policy.allowed_classes must be stable, experimental, and deprecated")
        for field in ("stable_rule", "experimental_rule", "deprecated_rule"):
            if not isinstance(policy.get(field), str) or not policy[field]:
                errors.append(f"classification_policy.{field} is required")

    repositories = document.get("repositories")
    if not isinstance(repositories, list) or not repositories:
        errors.append("repositories must be a non-empty array")
        repositories = []

    names: list[str] = []
    sums = {field: 0 for field in COUNT_FIELDS}
    for index, entry in enumerate(repositories):
        if not isinstance(entry, dict):
            errors.append(f"repositories[{index}] must be an object")
            continue
        name = entry.get("repository")
        if not isinstance(name, str) or not name:
            errors.append(f"repositories[{index}].repository is required")
        else:
            names.append(name)
            if name not in expected:
                errors.append(f"repositories[{index}].repository is not an active repository")
        if not isinstance(entry.get("owner"), str) or not entry["owner"]:
            errors.append(f"repositories[{index}].owner is required")
        status = entry.get("classification_status")
        if status not in ALLOWED_STATUSES:
            errors.append(f"repositories[{index}].classification_status is invalid")
        for field in COUNT_FIELDS:
            value = entry.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                errors.append(f"repositories[{index}].{field} must be a non-negative integer")
            else:
                sums[field] += value
        schema_count = entry.get("schema_document_count_from_inventory")
        classified_count = sum(entry.get(field, 0) for field in COUNT_FIELDS[1:])
        if isinstance(schema_count, int) and not isinstance(schema_count, bool) and classified_count != schema_count:
            errors.append(f"repositories[{index}] classified counts must equal schema_document_count_from_inventory")
        if name == "ao-covenant" and status != "stable_registry_authority":
            errors.append("ao-covenant classification_status must be stable_registry_authority")
        if name != "ao-covenant" and schema_count == 0 and status != "no_schema_documents":
            errors.append(f"repositories[{index}].classification_status must be no_schema_documents when count is zero")
        if name != "ao-covenant" and isinstance(schema_count, int) and schema_count > 0 and status == "stable_registry_authority":
            errors.append(f"repositories[{index}].classification_status cannot be stable_registry_authority outside ao-covenant")

    actual = set(names)
    if missing := sorted(expected - actual):
        errors.append("missing repository classifications: " + ", ".join(missing))
    if len(names) != len(actual):
        errors.append("repositories must not contain duplicate classifications")

    totals = document.get("totals")
    if not isinstance(totals, dict):
        errors.append("totals is required")
    else:
        for field in COUNT_FIELDS:
            if totals.get(field) != sums[field]:
                errors.append(f"totals.{field} must equal the repository sum")
        if totals.get("unclassified_schema_document_count") != 0:
            errors.append("totals.unclassified_schema_document_count must be zero")
        total_classified = sum(totals.get(field, 0) for field in COUNT_FIELDS[1:])
        if totals.get("schema_document_count_from_inventory") != total_classified:
            errors.append("totals classified counts must equal schema_document_count_from_inventory")

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
    parser = argparse.ArgumentParser(description="Validate copied AO schema stability classification")
    parser.add_argument("--classification", type=Path, default=DEFAULT_CLASSIFICATION)
    args = parser.parse_args()
    try:
        document = json.loads(args.classification.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"verify_copied_schema_classification.py: {exc}", file=sys.stderr)
        return 1
    errors = validate_document(document)
    if errors:
        for error in errors:
            print(f"verify_copied_schema_classification.py: {error}", file=sys.stderr)
        return 1
    print(f"verify_copied_schema_classification.py: validated {len(document['repositories'])} repository classifications")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
