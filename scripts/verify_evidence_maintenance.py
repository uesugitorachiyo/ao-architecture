#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from verify_evidence_freshness import (
    compare_release_component,
    tested_edges,
    validate_boundaries,
    validate_gate,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "stack" / "evidence-maintenance-report.json"
DEFAULT_MANIFEST = ROOT / "stack" / "current-release-manifest.json"
DEFAULT_MATRIX = ROOT / "stack" / "contract-compatibility-matrix.json"
DEFAULT_FRESHNESS = ROOT / "stack" / "evidence-freshness-readback.json"
CHECK_STATES = {"fresh", "stale", "blocked", "denied"}
REQUIRED_SOURCE_REPORTS = {
    "current_release_manifest": "stack/current-release-manifest.json",
    "compatibility_matrix": "stack/contract-compatibility-matrix.json",
    "evidence_freshness_readback": "stack/evidence-freshness-readback.json",
    "operator_adoption_drill": "docs/adoption-operator-drill.md",
}
REQUIRED_CHECKS = (
    "current_release_metadata_matches_manifest",
    "matrix_counts_match_edges",
    "tested_edges_have_canonical_vectors",
    "tested_edges_have_consumer_tests",
    "local_architecture_vectors_exist",
    "operator_workflow_readback_available",
    "denied_authority_boundaries_present",
)
REQUIRED_AUTOMATION_FIELDS = (
    "repeatable_report",
    "detects_stale_public_metadata",
    "detects_missing_vector",
    "detects_missing_consumer_test",
    "detects_count_mismatch",
    "detects_gate_activation_overclaim",
    "operator_readback_ready",
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def validate_source_reports(errors: list[str], source_reports: dict[str, Any] | None, existing_docs: set[str]) -> None:
    if not isinstance(source_reports, dict):
        errors.append("source_reports is required")
        return
    for field, expected in REQUIRED_SOURCE_REPORTS.items():
        if source_reports.get(field) != expected:
            errors.append(f"source_reports.{field} must be {expected}")
    if REQUIRED_SOURCE_REPORTS["operator_adoption_drill"] not in existing_docs:
        errors.append("operator adoption drill source is missing")


def validate_release_pair(
    errors: list[str],
    release_pair: dict[str, Any] | None,
    manifest: dict[str, Any],
    freshness: dict[str, Any],
) -> None:
    if not isinstance(release_pair, dict):
        errors.append("current_public_release_pair is required")
        return
    compare_release_component(errors, release_pair, manifest, "ao2", "ao2")
    compare_release_component(errors, release_pair, manifest, "control_plane", "control_plane")
    fresh_pair = freshness.get("current_public_release_pair")
    if not isinstance(fresh_pair, dict):
        errors.append("freshness current_public_release_pair is required")
        return
    for component in ("ao2", "control_plane"):
        if release_pair.get(component) != fresh_pair.get(component):
            errors.append(f"current_public_release_pair.{component} must match evidence freshness readback")


def validate_matrix_summary(
    errors: list[str],
    report_matrix: dict[str, Any] | None,
    matrix: dict[str, Any],
    freshness: dict[str, Any],
) -> None:
    if not isinstance(report_matrix, dict):
        errors.append("compatibility_matrix is required")
        return
    edges = matrix.get("edges") if isinstance(matrix.get("edges"), list) else []
    tested = tested_edges(matrix)
    proposed = len(edges) - len(tested)
    expected_counts = {
        "edge_count": len(edges),
        "tested_edge_count": len(tested),
        "canonical_vector_count": len(tested),
        "consumer_test_count": len(tested),
        "proposed_edge_count": proposed,
        "compatibility_gate_complete": False,
    }
    if report_matrix.get("matrix_status") != matrix.get("status"):
        errors.append("compatibility_matrix.matrix_status must match matrix status")
    for field, expected in expected_counts.items():
        if report_matrix.get(field) != expected:
            errors.append(f"compatibility_matrix.{field} must be {expected}")
    fresh_matrix = freshness.get("compatibility_matrix")
    if isinstance(fresh_matrix, dict) and report_matrix != fresh_matrix:
        errors.append("compatibility_matrix must match evidence freshness readback")


def validate_edge_proofs(errors: list[str], matrix: dict[str, Any], existing_paths: set[str]) -> None:
    for index, edge in enumerate(tested_edges(matrix)):
        vector = edge.get("canonical_vector")
        consumer_test = edge.get("consumer_test")
        if not isinstance(vector, dict) or not isinstance(vector.get("path"), str) or not vector.get("path"):
            errors.append(f"edges[{index}] tested edge must reference canonical vector path")
        elif vector.get("repository") == "ao-architecture" and vector["path"] not in existing_paths:
            errors.append(f"local architecture vector missing: {vector['path']}")
        if not isinstance(consumer_test, dict) or not isinstance(consumer_test.get("path"), str) or not consumer_test.get("path"):
            errors.append(f"edges[{index}] tested edge must reference consumer test path")


def validate_maintenance_checks(errors: list[str], checks: dict[str, Any] | None) -> None:
    if not isinstance(checks, dict):
        errors.append("maintenance_checks is required")
        return
    for field in REQUIRED_CHECKS:
        if checks.get(field) not in CHECK_STATES:
            errors.append(f"maintenance_checks.{field} must be fresh, stale, blocked, or denied")
        elif checks.get(field) != "fresh":
            errors.append(f"maintenance_checks.{field} must be fresh for the current readback")


def validate_automation_readiness(errors: list[str], readiness: dict[str, Any] | None) -> None:
    if not isinstance(readiness, dict):
        errors.append("automation_readiness is required")
        return
    for field in REQUIRED_AUTOMATION_FIELDS:
        if readiness.get(field) is not True:
            errors.append(f"automation_readiness.{field} must be true")


def validate_report(
    report: dict[str, Any],
    manifest: dict[str, Any],
    matrix: dict[str, Any],
    freshness: dict[str, Any],
    existing_paths: set[str] | None = None,
    existing_docs: set[str] | None = None,
) -> list[str]:
    errors: list[str] = []
    paths = existing_paths or set()
    docs = existing_docs or set()
    if report.get("schema") != "ao.architecture.evidence-maintenance-report.v0.1":
        errors.append("schema must be ao.architecture.evidence-maintenance-report.v0.1")
    if report.get("status") not in CHECK_STATES:
        errors.append("status must be fresh, stale, blocked, or denied")
    elif report.get("status") != "fresh":
        errors.append("status must be fresh for the current maintenance report")
    if not isinstance(report.get("generated_at_utc"), str) or not report.get("generated_at_utc"):
        errors.append("generated_at_utc is required")

    validate_source_reports(errors, report.get("source_reports"), docs)
    validate_release_pair(errors, report.get("current_public_release_pair"), manifest, freshness)
    validate_matrix_summary(errors, report.get("compatibility_matrix"), matrix, freshness)
    validate_edge_proofs(errors, matrix, paths)

    gate = report.get("compatibility_gate")
    validate_gate(errors, gate if isinstance(gate, dict) else None)
    if isinstance(gate, dict) and gate != freshness.get("compatibility_gate"):
        errors.append("compatibility_gate must match evidence freshness readback")

    validate_maintenance_checks(errors, report.get("maintenance_checks"))
    validate_automation_readiness(errors, report.get("automation_readiness"))
    validate_boundaries(errors, report.get("boundaries") if isinstance(report.get("boundaries"), dict) else None)
    if isinstance(report.get("boundaries"), dict) and report["boundaries"] != freshness.get("boundaries"):
        errors.append("boundaries must match evidence freshness readback")
    if not isinstance(report.get("next_action"), str) or not report["next_action"].strip():
        errors.append("next_action is required")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AO Architecture evidence maintenance report")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--freshness", type=Path, default=DEFAULT_FRESHNESS)
    args = parser.parse_args()
    try:
        report = read_json(args.report)
        manifest = read_json(args.manifest)
        matrix = read_json(args.matrix)
        freshness = read_json(args.freshness)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"verify_evidence_maintenance.py: {exc}", file=sys.stderr)
        return 1
    local_paths = {
        str(path.relative_to(ROOT))
        for path in (ROOT / "stack" / "fixtures" / "compatibility").glob("*.json")
    }
    docs = {
        str(path.relative_to(ROOT))
        for path in (ROOT / "docs").glob("*.md")
    }
    errors = validate_report(report, manifest, matrix, freshness, local_paths, docs)
    if errors:
        for error in errors:
            print(f"verify_evidence_maintenance.py: {error}", file=sys.stderr)
        return 1
    gate = report["compatibility_gate"]["state"]
    edge_count = report["compatibility_matrix"]["edge_count"]
    print(f"verify_evidence_maintenance.py: maintenance fresh; gate={gate}; edges={edge_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
