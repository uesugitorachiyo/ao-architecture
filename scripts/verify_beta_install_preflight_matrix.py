#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MATRIX = ROOT / "stack" / "beta-install-preflight-matrix.json"
REQUIRED_PLATFORMS = {"macos", "linux", "windows"}
REQUIRED_CHECKS = {
    "stack_lock_present",
    "native_tests_available",
    "contract_registry_available",
    "operator_cli_available",
    "evidence_store_writable",
}


def validate_matrix(matrix: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if matrix.get("schema") != "ao.architecture.beta-install-preflight-matrix.v0.1":
        errors.append("schema must be ao.architecture.beta-install-preflight-matrix.v0.1")
    if matrix.get("status") != "planning_only":
        errors.append("status must be planning_only")
    if matrix.get("scope") != "ao-stack":
        errors.append("scope must be ao-stack")

    platforms = matrix.get("platforms")
    if not isinstance(platforms, list) or not platforms:
        errors.append("platforms must be a non-empty array")
        platforms = []
    seen_platforms: set[str] = set()
    for index, entry in enumerate(platforms):
        if not isinstance(entry, dict):
            errors.append(f"platforms[{index}] must be an object")
            continue
        name = entry.get("platform")
        if not isinstance(name, str) or not name:
            errors.append(f"platforms[{index}].platform is required")
            continue
        if name in seen_platforms:
            errors.append(f"platforms[{index}].platform duplicates {name}")
        seen_platforms.add(name)
        if name not in REQUIRED_PLATFORMS:
            errors.append(f"platforms[{index}].platform is unsupported")
        checks = entry.get("required_checks")
        if not isinstance(checks, list):
            errors.append(f"platforms[{index}].required_checks must be an array")
            checks = []
        missing_checks = sorted(REQUIRED_CHECKS - {check for check in checks if isinstance(check, str)})
        if missing_checks:
            errors.append(f"platforms[{index}].required_checks missing: {', '.join(missing_checks)}")
        if entry.get("blocks_beta_install") is not True:
            errors.append(f"platforms[{index}].blocks_beta_install must be true")
        if entry.get("executes_install") is not False:
            errors.append(f"platforms[{index}].executes_install must be false")

    missing_platforms = sorted(REQUIRED_PLATFORMS - seen_platforms)
    if missing_platforms:
        errors.append("missing platforms: " + ", ".join(missing_platforms))

    safety = matrix.get("safety")
    if not isinstance(safety, dict):
        errors.append("safety is required")
    else:
        if safety.get("planning_only") is not True:
            errors.append("safety.planning_only must be true")
        if safety.get("provider_calls") is not False:
            errors.append("safety.provider_calls must be false")
        if safety.get("release_or_publish") is not False:
            errors.append("safety.release_or_publish must be false")
        if safety.get("credential_use") is not False:
            errors.append("safety.credential_use must be false")
        if safety.get("promotion_granted") is not False:
            errors.append("safety.promotion_granted must be false")
        if safety.get("rsi_remains_denied") is not True:
            errors.append("safety.rsi_remains_denied must be true")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AO beta install preflight matrix")
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    args = parser.parse_args()
    try:
        matrix = json.loads(args.matrix.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"verify_beta_install_preflight_matrix.py: {exc}", file=sys.stderr)
        return 1
    errors = validate_matrix(matrix)
    if errors:
        for error in errors:
            print(f"verify_beta_install_preflight_matrix.py: {error}", file=sys.stderr)
        return 1
    print(f"verify_beta_install_preflight_matrix.py: validated {len(matrix['platforms'])} platform preflight entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
