#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOCUMENT = ROOT / "stack" / "beta-operations-slo-draft.json"
REQUIRED_SLOS = {
    "mission_restart_recovery",
    "approval_digest_integrity",
    "rollback_receipt_latency",
    "evidence_freshness",
}
ALLOWED_OWNER_REPOS = {
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


def validate_document(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != "ao.architecture.beta-operations-slo-draft.v0.1":
        errors.append("schema must be ao.architecture.beta-operations-slo-draft.v0.1")
    if document.get("status") != "draft_planning_only":
        errors.append("status must be draft_planning_only")
    if document.get("scope") != "ao-stack-month6-beta-operations":
        errors.append("scope must be ao-stack-month6-beta-operations")
    if document.get("source_recommendation_rank") != 37:
        errors.append("source_recommendation_rank must be 37")
    if document.get("source_recommendation_task") != "Create beta operations SLO draft fixture":
        errors.append("source_recommendation_task must match rank 37")
    if document.get("safety_gate") != "planning_only_no_provider_no_release":
        errors.append("safety_gate must be planning_only_no_provider_no_release")

    slos = document.get("slos")
    if not isinstance(slos, list) or not slos:
        errors.append("slos must be a non-empty array")
        slos = []

    seen: set[str] = set()
    for index, slo in enumerate(slos):
        if not isinstance(slo, dict):
            errors.append(f"slos[{index}] must be an object")
            continue
        slo_id = slo.get("id")
        if not isinstance(slo_id, str) or not slo_id:
            errors.append(f"slos[{index}].id is required")
        elif slo_id in seen:
            errors.append(f"slos[{index}].id duplicates {slo_id}")
        else:
            seen.add(slo_id)

        owner_repo = slo.get("owner_repo")
        if owner_repo not in ALLOWED_OWNER_REPOS:
            errors.append(f"slos[{index}].owner_repo is unsupported")
        for field in ("objective", "target", "measurement"):
            if not isinstance(slo.get(field), str) or not slo[field].strip():
                errors.append(f"slos[{index}].{field} is required")
        if slo.get("blocks_beta") is not True:
            errors.append(f"slos[{index}].blocks_beta must be true")

    missing = sorted(REQUIRED_SLOS - seen)
    if missing:
        errors.append("missing required slos: " + ", ".join(missing))
    if document.get("slo_count") != len(slos):
        errors.append("slo_count must match slos length")

    safety = document.get("safety")
    if not isinstance(safety, dict):
        errors.append("safety is required")
    else:
        if safety.get("planning_only") is not True:
            errors.append("safety.planning_only must be true")
        for field in (
            "provider_calls",
            "credential_use",
            "release_or_publish",
            "promotion_granted",
            "direct_main_mutation",
            "hidden_instruction_change",
        ):
            if safety.get(field) is not False:
                errors.append(f"safety.{field} must be false")
        if safety.get("rsi_remains_denied") is not True:
            errors.append("safety.rsi_remains_denied must be true")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AO beta operations SLO draft")
    parser.add_argument("--document", type=Path, default=DEFAULT_DOCUMENT)
    args = parser.parse_args()
    try:
        document = json.loads(args.document.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"verify_beta_operations_slo_draft.py: {exc}", file=sys.stderr)
        return 1
    errors = validate_document(document)
    if errors:
        for error in errors:
            print(f"verify_beta_operations_slo_draft.py: {error}", file=sys.stderr)
        return 1
    print(f"verify_beta_operations_slo_draft.py: validated {len(document['slos'])} beta operations SLOs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
