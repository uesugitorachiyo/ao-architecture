#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCK = ROOT / "stack" / "ao-stack.lock.json"
EXPECTED_REPOSITORIES = {
    "ao-architecture", "ao-mission", "ao-blueprint", "ao-atlas", "ao-foundry", "ao-forge",
    "ao-covenant", "ao2", "ao2-control-plane", "ao-command", "ao-arena", "ao-crucible",
    "ao-sentinel", "ao-promoter",
}
PROPOSED_BOUNDARIES = {"ao-control", "ao2", "ao-covenant", "ao2-control-plane", "ao-assurance"}
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


def validate_lock(lock: dict[str, Any], expected_repositories: set[str] | None = None) -> list[str]:
    expected = expected_repositories or EXPECTED_REPOSITORIES
    errors: list[str] = []
    if lock.get("schema") != "ao.architecture.stack-lock.v0.1":
        errors.append("schema must be ao.architecture.stack-lock.v0.1")
    if lock.get("status") != "current":
        errors.append("status must be current")
    repositories = lock.get("repositories")
    if not isinstance(repositories, list):
        errors.append("repositories must be an array")
        repositories = []
    if lock.get("repository_count") != len(repositories):
        errors.append("repository_count must match repositories length")
    names: list[str] = []
    commits: list[str] = []
    for index, entry in enumerate(repositories):
        if not isinstance(entry, dict):
            errors.append(f"repositories[{index}] must be an object")
            continue
        prefix = f"repositories[{index}]"
        name = entry.get("repository")
        commit = entry.get("commit")
        names.append(name if isinstance(name, str) else "")
        commits.append(commit if isinstance(commit, str) else "")
        for field in ("repository", "branch", "commit", "detected_version", "current_boundary", "proposed_boundary", "primary_authority"):
            if not isinstance(entry.get(field), str) or not entry[field]:
                errors.append(f"{prefix}.{field} is required")
        if isinstance(commit, str) and not COMMIT_RE.fullmatch(commit):
            errors.append(f"{prefix}.commit must be a 40-character lowercase hexadecimal commit")
        if entry.get("proposed_boundary") not in PROPOSED_BOUNDARIES:
            errors.append(f"{prefix}.proposed_boundary is unsupported")
        if entry.get("detected_version") == "":
            errors.append(f"{prefix}.detected_version must explicitly use unversioned when no tag exists")
    actual = set(names)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        errors.append("missing repositories: " + ", ".join(missing))
    if extra:
        errors.append("unexpected repositories: " + ", ".join(extra))
    if len(names) != len(actual):
        errors.append("repositories must not contain duplicate names")
    seen_commits: set[str] = set()
    for commit in commits:
        if commit and commit in seen_commits:
            errors.append(f"commit {commit} is duplicated")
        seen_commits.add(commit)
    safety = lock.get("safety")
    if not isinstance(safety, dict):
        errors.append("safety is required")
    else:
        if safety.get("promotion_granted") is not False:
            errors.append("promotion_granted must remain false")
        if safety.get("rsi_remains_denied") is not True:
            errors.append("rsi_remains_denied must remain true")
        if safety.get("migration_started") is not False:
            errors.append("migration_started must remain false")
        if safety.get("provider_calls") is not False:
            errors.append("provider_calls must remain false")
        if safety.get("release_or_publish") is not False:
            errors.append("release_or_publish must remain false")
        if safety.get("direct_main_mutation") is not False:
            errors.append("direct_main_mutation must remain false")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AO stack lockfile")
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    args = parser.parse_args()
    try:
        lock = json.loads(args.lock.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"verify_stack_lock.py: {exc}", file=sys.stderr)
        return 1
    errors = validate_lock(lock)
    if errors:
        for error in errors:
            print(f"verify_stack_lock.py: {error}", file=sys.stderr)
        return 1
    print(f"verify_stack_lock.py: validated {len(lock['repositories'])} repository lock entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
