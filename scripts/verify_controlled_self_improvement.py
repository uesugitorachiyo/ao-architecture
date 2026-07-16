#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "stack" / "controlled-self-improvement-dry-run.json"
REQUIRED_GATES = {
    "proposal",
    "policy_classification",
    "human_approval",
    "fixture_dry_run",
    "evidence_capture",
    "rollback_proof",
    "observation",
    "operator_readback",
    "sentinel_wording_check",
    "promoter_no_rsi_verdict",
}
REQUIRED_EVIDENCE = {
    "proposal",
    "policy_classification",
    "human_approval",
    "dry_run_trace",
    "evidence_pack",
    "rollback_proof",
    "control_plane_observation",
    "operator_readback",
    "sentinel_wording",
    "promoter_no_rsi_verdict",
}


def validate_manifest(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != "ao.architecture.controlled-self-improvement-dry-run.v0.1":
        errors.append("schema must be ao.architecture.controlled-self-improvement-dry-run.v0.1")
    if document.get("status") != "dry_run_only":
        errors.append("status must be dry_run_only")

    false_fields = (
        "rsi_authorized",
        "live_self_modification_authorized",
        "provider_execution_authorized",
        "promotion_requested",
        "promotion_granted",
        "external_beta_launched",
        "release_authorized",
        "tag_authorized",
        "upload_authorized",
        "deployment_authorized",
    )
    for field in false_fields:
        if document.get(field) is not False:
            errors.append(f"{field} must be false")

    required_gates = document.get("required_gates")
    if not isinstance(required_gates, list):
        errors.append("required_gates must be an array")
        required_gates = []
    gate_set = set(required_gates)
    for gate in sorted(REQUIRED_GATES):
        if gate not in gate_set:
            errors.append(f"required_gates must include {gate}")

    evidence = document.get("evidence_requirements")
    if not isinstance(evidence, dict):
        errors.append("evidence_requirements must be an object")
        evidence = {}
    for field in sorted(REQUIRED_EVIDENCE):
        if evidence.get(field) is not True:
            errors.append(f"evidence_requirements.{field} must be true")

    boundaries = document.get("workspace_boundaries")
    if not isinstance(boundaries, dict):
        errors.append("workspace_boundaries must be an object")
    else:
        if boundaries.get("fixture_workspace_only") is not True:
            errors.append("workspace_boundaries.fixture_workspace_only must be true")
        if boundaries.get("live_repository_mutation") is not False:
            errors.append("workspace_boundaries.live_repository_mutation must be false")
        if boundaries.get("temporary_or_evidence_scoped") is not True:
            errors.append("workspace_boundaries.temporary_or_evidence_scoped must be true")

    next_state = document.get("next_state")
    if not isinstance(next_state, dict):
        errors.append("next_state must be an object")
    else:
        if next_state.get("month5_recommendation") != "multi_repo_product_coordination_and_operator_workflow_hardening":
            errors.append("next_state.month5_recommendation must be multi_repo_product_coordination_and_operator_workflow_hardening")
        if next_state.get("rsi_remains_denied") is not True:
            errors.append("next_state.rsi_remains_denied must be true")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate controlled self-improvement dry-run source of truth")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    try:
        document = json.loads(args.manifest.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"verify_controlled_self_improvement.py: {exc}", file=sys.stderr)
        return 1
    errors = validate_manifest(document)
    if errors:
        for error in errors:
            print(f"verify_controlled_self_improvement.py: {error}", file=sys.stderr)
        return 1
    print("verify_controlled_self_improvement.py: dry-run-only self-improvement design verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
