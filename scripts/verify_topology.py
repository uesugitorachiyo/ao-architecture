#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INVENTORY = ROOT / "stack" / "authority-inventory.json"
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
PROPOSED_BOUNDARIES = {"ao-control", "ao2", "ao-covenant", "ao2-control-plane", "ao-assurance"}


def validate_document(document: dict[str, Any], expected_repositories: set[str] | None = None) -> list[str]:
    expected = expected_repositories or EXPECTED_REPOSITORIES
    errors: list[str] = []
    if document.get("schema") != "ao.architecture.authority-inventory.v0.1":
        errors.append("schema must be ao.architecture.authority-inventory.v0.1")
    if document.get("status") != "current":
        errors.append("status must be current")

    repositories = document.get("repositories")
    if not isinstance(repositories, list):
        errors.append("repositories must be an array")
        repositories = []
    names: list[str] = []
    for index, entry in enumerate(repositories):
        if not isinstance(entry, dict):
            errors.append(f"repositories[{index}] must be an object")
            continue
        name = entry.get("repository")
        if not isinstance(name, str) or not name:
            errors.append(f"repositories[{index}].repository is required")
            continue
        names.append(name)
        for field in ("current_boundary", "proposed_boundary", "primary_authority", "migration_status"):
            if not isinstance(entry.get(field), str) or not entry[field]:
                errors.append(f"repositories[{index}].{field} is required")
        if entry.get("proposed_boundary") not in PROPOSED_BOUNDARIES:
            errors.append(f"repositories[{index}].proposed_boundary is unsupported")
        if entry.get("migration_status") != "not_started":
            errors.append(f"repositories[{index}] must remain not_started during the foundation wave")
        if not isinstance(entry.get("non_authority"), list) or not entry["non_authority"]:
            errors.append(f"repositories[{index}].non_authority must name denied responsibilities")

    actual = set(names)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        errors.append("missing repositories: " + ", ".join(missing))
    if extra:
        errors.append("unexpected repositories: " + ", ".join(extra))
    if len(names) != len(actual):
        errors.append("repositories must not contain duplicates")

    domains = document.get("authority_domains")
    if not isinstance(domains, list) or not domains:
        errors.append("authority_domains must be a non-empty array")
        domains = []
    seen_domains: set[str] = set()
    seen_owners: set[str] = set()
    for index, entry in enumerate(domains):
        if not isinstance(entry, dict):
            errors.append(f"authority_domains[{index}] must be an object")
            continue
        domain = entry.get("domain")
        owner = entry.get("owner")
        if not isinstance(domain, str) or not domain:
            errors.append(f"authority_domains[{index}].domain is required")
        elif domain in seen_domains:
            errors.append(f"authority domain {domain} is duplicated")
        else:
            seen_domains.add(domain)
        if not isinstance(owner, str) or not owner:
            errors.append(f"authority_domains[{index}].owner is required")
        elif owner in seen_owners:
            errors.append(f"authority domain owner {owner} is duplicated")
        else:
            seen_owners.add(owner)
        if isinstance(owner, str) and owner not in expected:
            errors.append(f"authority_domains[{index}].owner is not an active repository")

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
    parser = argparse.ArgumentParser(description="Validate AO Architecture authority inventory")
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    args = parser.parse_args()
    try:
        document = json.loads(args.inventory.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"verify_topology.py: {exc}", file=sys.stderr)
        return 1
    errors = validate_document(document)
    if errors:
        for error in errors:
            print(f"verify_topology.py: {error}", file=sys.stderr)
        return 1
    print(f"verify_topology.py: validated {len(document['repositories'])} repositories and {len(document['authority_domains'])} authority domains")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
