#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "stack" / "component-release-classification.json"

EXPECTED_REPOSITORIES = {
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
    "ao-architecture",
}

TIER_1 = {"ao2", "ao2-control-plane", "ao-mission", "ao-command"}
TIER_2 = {"ao-blueprint", "ao-atlas", "ao-forge", "ao-covenant"}
TIER_3 = {"ao-foundry", "ao-arena", "ao-crucible", "ao-sentinel", "ao-promoter"}
ARCHITECTURE = {"ao-architecture"}
EXECUTABLE_REPOSITORIES = EXPECTED_REPOSITORIES - ARCHITECTURE
SUPPORTED_PLATFORMS = ["linux", "macos", "windows"]


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema") != "ao.architecture.component-release-classification.v0.1":
        errors.append("manifest schema must be ao.architecture.component-release-classification.v0.1")
    if manifest.get("status") != "active":
        errors.append("manifest status must be active")
    repositories = manifest.get("repositories")
    if not isinstance(repositories, list):
        return errors + ["manifest repositories must be a list"]
    if len(repositories) != 14:
        errors.append("manifest must classify 14 repositories")

    seen: set[str] = set()
    for entry in repositories:
        if not isinstance(entry, dict):
            errors.append("repository entry must be an object")
            continue
        repo = entry.get("repository")
        if repo in seen:
            errors.append(f"duplicate repository classification: {repo}")
        if repo:
            seen.add(repo)
        if repo not in EXPECTED_REPOSITORIES:
            errors.append(f"unexpected repository classification: {repo}")
            continue

        expected_tier = 1 if repo in TIER_1 else 2 if repo in TIER_2 else 3 if repo in TIER_3 else 0
        if entry.get("tier") != expected_tier:
            errors.append(f"{repo} tier must be {expected_tier}")

        entry_points = entry.get("entry_points")
        if repo in EXECUTABLE_REPOSITORIES:
            if not isinstance(entry_points, list) or not entry_points:
                errors.append(f"{repo} must declare executable entry points")
            if entry.get("binary_free") is True:
                errors.append(f"{repo} must not be binary_free")
            if entry.get("supported_platforms") != SUPPORTED_PLATFORMS:
                errors.append(f"{repo} must support linux, macos, and windows")
            artifact_names = entry.get("artifact_names")
            if not isinstance(artifact_names, list) or not artifact_names:
                errors.append(f"{repo} must declare artifact names")
        else:
            if entry_points != []:
                errors.append("ao-architecture entry_points must be empty")
            if entry.get("binary_free") is not True:
                errors.append("ao-architecture must be binary_free")
            if entry.get("publication_allowed") is not False:
                errors.append("ao-architecture publication_allowed must be false")

        if repo in TIER_1 and entry.get("publication_allowed") is not True:
            errors.append(f"{repo} Tier 1 publication_allowed must be true")
        if repo in TIER_2 and entry.get("publication_allowed") != "conditional":
            errors.append(f"{repo} Tier 2 publication_allowed must be conditional")
        if repo in TIER_3:
            if entry.get("publication_allowed") is not False:
                errors.append(f"{repo} Tier 3 publication_allowed must be false")
            if entry.get("artifact_only") is not True:
                errors.append(f"{repo} Tier 3 artifact_only must be true")

        for field in ("version_source", "release_owner", "install_promise"):
            if not entry.get(field):
                errors.append(f"{repo} must declare {field}")

    missing = EXPECTED_REPOSITORIES - seen
    if missing:
        errors.append(f"missing repository classifications: {sorted(missing)}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AO component release classification manifest")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"verify_component_release_classification.py: {exc}", file=sys.stderr)
        return 1
    errors = validate_manifest(manifest)
    if errors:
        for error in errors:
            print(f"verify_component_release_classification.py: {error}", file=sys.stderr)
        return 1
    print("verify_component_release_classification.py: component release classification verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
