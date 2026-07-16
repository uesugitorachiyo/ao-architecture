#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_READBACK = ROOT / "stack" / "evidence-freshness-readback.json"
DEFAULT_MANIFEST = ROOT / "stack" / "current-release-manifest.json"
DEFAULT_MATRIX = ROOT / "stack" / "contract-compatibility-matrix.json"
GATE_STATES = {"false", "ready", "active", "blocked", "denied"}
FALSE_BOUNDARIES = (
    "external_beta_launched",
    "promotion_requested",
    "promotion_granted",
    "provider_pilot",
    "release_or_publish",
    "tag_or_upload",
    "deployment",
    "live_self_modification",
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def tested_edges(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    edges = matrix.get("edges")
    if not isinstance(edges, list):
        return []
    return [
        edge
        for edge in edges
        if isinstance(edge, dict) and edge.get("compatibility_status") == "tested_current_release_pair"
    ]


def compare_release_component(
    errors: list[str],
    readback: dict[str, Any],
    manifest: dict[str, Any],
    readback_key: str,
    manifest_key: str,
) -> None:
    readback_entry = readback.get(readback_key)
    manifest_entry = manifest.get(manifest_key)
    if not isinstance(readback_entry, dict):
        errors.append(f"{readback_key} readback is required")
        return
    if not isinstance(manifest_entry, dict):
        errors.append(f"{manifest_key} manifest entry is required")
        return
    for field in ("version", "release_url", "tag_target", "is_draft", "is_prerelease", "asset_count"):
        if readback_entry.get(field) != manifest_entry.get(field):
            errors.append(f"{readback_key}.{field} must match current release manifest")


def validate_gate(errors: list[str], gate: dict[str, Any] | None) -> None:
    if not isinstance(gate, dict):
        errors.append("compatibility_gate is required")
        return
    state = gate.get("state")
    if state not in GATE_STATES:
        errors.append("compatibility_gate.state must be false, ready, active, blocked, or denied")
    allowed_states = gate.get("allowed_states")
    if allowed_states != ["false", "ready", "active", "blocked", "denied"]:
        errors.append("compatibility_gate.allowed_states must list false, ready, active, blocked, denied")
    reason = gate.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        errors.append("compatibility_gate.reason is required")
    if state == "active":
        if gate.get("activation_authorized") is not True:
            errors.append("compatibility_gate active requires activation_authorized=true")
        if not isinstance(gate.get("activation_evidence"), str) or not gate.get("activation_evidence"):
            errors.append("compatibility_gate active requires activation_evidence")
    else:
        if gate.get("activation_authorized") is not False:
            errors.append("compatibility_gate activation_authorized must remain false unless active")

    criteria = gate.get("readiness_criteria")
    if not isinstance(criteria, dict):
        errors.append("compatibility_gate.readiness_criteria is required")
        return
    true_criteria = (
        "release_metadata_matches_manifest",
        "matrix_counts_match",
        "tested_edges_have_vectors",
        "tested_edges_have_consumer_tests",
        "local_architecture_vectors_exist",
        "rsi_remains_denied",
    )
    false_criteria = (
        "external_beta_launched",
        "promotion_requested",
        "promotion_granted",
        "provider_pilot",
        "release_or_publish",
    )
    for field in true_criteria:
        if criteria.get(field) is not True:
            errors.append(f"readiness_criteria.{field} must be true")
    for field in false_criteria:
        if criteria.get(field) is not False:
            errors.append(f"readiness_criteria.{field} must be false")


def validate_boundaries(errors: list[str], boundaries: dict[str, Any] | None) -> None:
    if not isinstance(boundaries, dict):
        errors.append("boundaries is required")
        return
    for field in FALSE_BOUNDARIES:
        if boundaries.get(field) is not False:
            errors.append(f"{field} must remain false")
    if boundaries.get("rsi_remains_denied") is not True:
        errors.append("rsi_remains_denied must remain true")


def validate_matrix_readback(
    errors: list[str],
    readback_matrix: dict[str, Any] | None,
    matrix: dict[str, Any],
    existing_paths: set[str],
) -> None:
    if not isinstance(readback_matrix, dict):
        errors.append("compatibility_matrix readback is required")
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
    if readback_matrix.get("matrix_status") != matrix.get("status"):
        errors.append("compatibility_matrix.matrix_status must match matrix status")
    for field, expected in expected_counts.items():
        if readback_matrix.get(field) != expected:
            if field in ("canonical_vector_count", "consumer_test_count"):
                errors.append(f"compatibility_matrix.{field} must equal tested edge count")
            else:
                errors.append(f"compatibility_matrix.{field} must be {expected}")

    for index, edge in enumerate(tested):
        vector = edge.get("canonical_vector")
        consumer_test = edge.get("consumer_test")
        if not isinstance(vector, dict) or not isinstance(vector.get("path"), str) or not vector.get("path"):
            errors.append(f"edges[{index}] tested edge must reference canonical vector path")
            continue
        if not isinstance(consumer_test, dict) or not isinstance(consumer_test.get("path"), str) or not consumer_test.get("path"):
            errors.append(f"edges[{index}] tested edge must reference consumer test path")
        if vector.get("repository") == "ao-architecture":
            path = vector["path"]
            if path not in existing_paths:
                errors.append(f"local architecture vector missing: {path}")


def validate_readback(
    readback: dict[str, Any],
    manifest: dict[str, Any],
    matrix: dict[str, Any],
    existing_paths: set[str] | None = None,
) -> list[str]:
    errors: list[str] = []
    paths = existing_paths or set()
    if readback.get("schema") != "ao.architecture.evidence-freshness-readback.v0.1":
        errors.append("schema must be ao.architecture.evidence-freshness-readback.v0.1")
    if readback.get("status") not in {"fresh", "blocked", "stale"}:
        errors.append("status must be fresh, blocked, or stale")

    current_pair = readback.get("current_public_release_pair")
    if not isinstance(current_pair, dict):
        errors.append("current_public_release_pair is required")
    else:
        compare_release_component(errors, current_pair, manifest, "ao2", "ao2")
        compare_release_component(errors, current_pair, manifest, "control_plane", "control_plane")

    validate_matrix_readback(errors, readback.get("compatibility_matrix"), matrix, paths)
    validate_gate(errors, readback.get("compatibility_gate"))
    validate_boundaries(errors, readback.get("boundaries"))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AO Architecture evidence freshness and gate readiness")
    parser.add_argument("--readback", type=Path, default=DEFAULT_READBACK)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    args = parser.parse_args()
    try:
        readback = read_json(args.readback)
        manifest = read_json(args.manifest)
        matrix = read_json(args.matrix)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"verify_evidence_freshness.py: {exc}", file=sys.stderr)
        return 1
    local_paths = {
        str(path.relative_to(ROOT))
        for path in (ROOT / "stack" / "fixtures" / "compatibility").glob("*.json")
    }
    errors = validate_readback(readback, manifest, matrix, local_paths)
    if errors:
        for error in errors:
            print(f"verify_evidence_freshness.py: {error}", file=sys.stderr)
        return 1
    gate = readback["compatibility_gate"]["state"]
    edge_count = readback["compatibility_matrix"]["edge_count"]
    print(f"verify_evidence_freshness.py: evidence fresh; gate={gate}; edges={edge_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
