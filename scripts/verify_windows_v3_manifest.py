#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "stack" / "fixtures" / "windows-v3" / "source-manifest-current-public-pair.json"
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


def validate_manifest(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != "ao.architecture.windows-v3-source-manifest.v0.1":
        errors.append("schema must be ao.architecture.windows-v3-source-manifest.v0.1")
    if document.get("scope") != "ao-stack":
        errors.append("scope must be ao-stack")
    if document.get("source") != "repository_controlled_fixture_only":
        errors.append("source must be repository_controlled_fixture_only")
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

    actual = set(names)
    if "ao-mission" not in actual:
        errors.append("ao-stack manifests must include ao-mission")
    missing = sorted(EXPECTED_REPOSITORIES - actual)
    extra = sorted(actual - EXPECTED_REPOSITORIES)
    if missing:
        errors.append("missing repositories: " + ", ".join(missing))
    if extra:
        errors.append("unexpected repositories: " + ", ".join(extra))
    if len(names) != len(actual):
        errors.append("repositories must not contain duplicate names")

    boolean_requirements = {
        "windows_v3_instance_access_authorized": False,
        "windows_v3_manifest_mutation_authorized": False,
        "external_beta_launched": False,
        "promotion_granted": False,
        "rsi_remains_denied": True,
    }
    for field, expected in boolean_requirements.items():
        if document.get(field) is not expected:
            errors.append(f"{field} must remain {str(expected).lower()}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate repository-controlled Windows V3 source manifest fixture")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    try:
        document = json.loads(args.manifest.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"verify_windows_v3_manifest.py: {exc}", file=sys.stderr)
        return 1
    errors = validate_manifest(document)
    if errors:
        for error in errors:
            print(f"verify_windows_v3_manifest.py: {error}", file=sys.stderr)
        return 1
    print("verify_windows_v3_manifest.py: repository-controlled Windows V3 manifest fixture verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
