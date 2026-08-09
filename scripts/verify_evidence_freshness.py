#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from verify_execution_observation_version_skew import (
    parse_timestamp,
    read_strict_json,
    validate_contract as validate_version_skew_contract,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_READBACK = ROOT / "stack" / "evidence-freshness-readback.json"
DEFAULT_MANIFEST = ROOT / "stack" / "current-release-manifest.json"
DEFAULT_MATRIX = ROOT / "stack" / "contract-compatibility-matrix.json"
DEFAULT_VERSION_SKEW = ROOT / "stack" / "execution-observation-version-skew.json"
GATE_STATES = {"false", "ready", "active", "blocked", "denied"}
AO2_COMPATIBILITY_EVIDENCE_VERSION = "v0.5.10"
AO2_COMPATIBILITY_EVIDENCE_PATH = "tests/fixtures/compatibility/ao2-execution-receipt-v0.5.10.json"
AO2_COMPATIBILITY_EVIDENCE_COMMIT = "214f0648ec2b15df0729f90b26a4da258882dba1"
AO2_UNCHANGED_CONTRACT_BRIDGE_RELEASES = {"v0.5.10"}
AO2_STALE_REASON_CODE = "AO2_COMPATIBILITY_EVIDENCE_VERSION_STALE"
AO2_CURRENT_REASON_CODE = "AO2_COMPATIBILITY_EVIDENCE_CURRENT"
AO2_EVIDENCE_VERSION_RE = re.compile(r"ao2-execution-receipt-(v[0-9]+\.[0-9]+\.[0-9]+)\.json$")
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


def validate_gate(
    errors: list[str],
    gate: dict[str, Any] | None,
    compatibility_gap: dict[str, str] | None = None,
) -> None:
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
    for field in ("compatibility_evidence_current", "all_tested_edges_fresh"):
        if criteria.get(field) not in (True, False):
            errors.append(f"readiness_criteria.{field} must be boolean")

    if compatibility_gap is not None:
        if state != "blocked":
            errors.append("compatibility_gate.state must be blocked while AO2 compatibility evidence is stale")
        if gate.get("reason_code") != AO2_STALE_REASON_CODE:
            errors.append(f"compatibility_gate.reason_code must be {AO2_STALE_REASON_CODE}")
        if gate.get("details") != compatibility_gap:
            errors.append("compatibility_gate.details must bind the stale AO2 compatibility evidence")
        if criteria.get("compatibility_evidence_current") is not False:
            errors.append("readiness_criteria.compatibility_evidence_current must be false")
        if criteria.get("all_tested_edges_fresh") is not False:
            errors.append("readiness_criteria.all_tested_edges_fresh must be false")
    else:
        if state != "ready":
            errors.append("compatibility_gate.state must be ready when all compatibility evidence is current")
        if gate.get("reason_code") != AO2_CURRENT_REASON_CODE:
            errors.append(f"compatibility_gate.reason_code must be {AO2_CURRENT_REASON_CODE}")
        if gate.get("details") != {}:
            errors.append("compatibility_gate.details must be empty when compatibility evidence is current")
        if criteria.get("compatibility_evidence_current") is not True:
            errors.append("readiness_criteria.compatibility_evidence_current must be true")
        if criteria.get("all_tested_edges_fresh") is not True:
            errors.append("readiness_criteria.all_tested_edges_fresh must be true")


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
    ao2_evidence_stale: bool,
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
        "fresh_edge_count": len(tested) - (1 if ao2_evidence_stale else 0),
        "stale_edge_count": 1 if ao2_evidence_stale else 0,
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


def validate_ao2_compatibility_binding(
    errors: list[str],
    matrix: dict[str, Any],
    manifest: dict[str, Any],
) -> tuple[bool, dict[str, str] | None]:
    edges = matrix.get("edges") if isinstance(matrix.get("edges"), list) else []
    matches = [
        edge
        for edge in edges
        if isinstance(edge, dict)
        and edge.get("producer") == "ao2"
        and edge.get("consumer") == "ao2-control-plane"
        and edge.get("contract_family") == "execution_to_observation"
    ]
    if len(matches) != 1:
        errors.append("matrix must contain exactly one AO2 execution-to-observation compatibility edge")
        return True, None

    vector = matches[0].get("canonical_vector")
    if not isinstance(vector, dict):
        errors.append("AO2 compatibility canonical vector is required")
        return True, None

    path = vector.get("path")
    merge_commit = vector.get("merge_commit")
    if path != AO2_COMPATIBILITY_EVIDENCE_PATH:
        errors.append("AO2 compatibility canonical vector path is not the verified evidence path")
    if merge_commit != AO2_COMPATIBILITY_EVIDENCE_COMMIT:
        errors.append("AO2 compatibility canonical vector merge commit is not the verified evidence commit")

    match = AO2_EVIDENCE_VERSION_RE.search(path) if isinstance(path, str) else None
    if match is None:
        errors.append("AO2 compatibility canonical vector path must bind an evidence version")
        evidence_version = ""
    else:
        evidence_version = match.group(1)
    if evidence_version and evidence_version != AO2_COMPATIBILITY_EVIDENCE_VERSION:
        errors.append("AO2 compatibility evidence version is not the verified historical version")

    ao2_manifest = manifest.get("ao2")
    current_version = ao2_manifest.get("version") if isinstance(ao2_manifest, dict) else ""
    stale = (
        evidence_version != AO2_COMPATIBILITY_EVIDENCE_VERSION
        or not current_version
        or current_version not in AO2_UNCHANGED_CONTRACT_BRIDGE_RELEASES
    )
    if not stale:
        return False, None

    return True, {
        "edge": "ao2->ao2-control-plane:execution_to_observation",
        "current_ao2_version": current_version,
        "compatibility_evidence_version": evidence_version,
        "canonical_vector_path": path if isinstance(path, str) else "",
        "canonical_vector_merge_commit": merge_commit if isinstance(merge_commit, str) else "",
        "required_resolution": "separately_verified_unchanged_contract_bridge_or_refreshed_fixture",
    }


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

    ao2_evidence_stale, compatibility_gap = validate_ao2_compatibility_binding(errors, matrix, manifest)
    validate_matrix_readback(
        errors,
        readback.get("compatibility_matrix"),
        matrix,
        paths,
        ao2_evidence_stale,
    )
    if compatibility_gap is not None and readback.get("status") != "stale":
        errors.append(
            f"AO2 compatibility evidence {compatibility_gap['compatibility_evidence_version']} "
            f"is stale for current release {compatibility_gap['current_ao2_version']}; "
            "readback must be stale and gate blocked"
        )
    if compatibility_gap is None and readback.get("status") != "fresh":
        errors.append("readback status must be fresh when all compatibility evidence is current")
    validate_gate(errors, readback.get("compatibility_gate"), compatibility_gap)
    validate_boundaries(errors, readback.get("boundaries"))
    return errors


def validate_live_readback(
    readback: dict[str, Any],
    manifest: dict[str, Any],
    matrix: dict[str, Any],
    version_skew: dict[str, Any],
    now: datetime,
    existing_paths: set[str] | None = None,
) -> list[str]:
    errors = validate_readback(readback, manifest, matrix, existing_paths)
    skew_errors = validate_version_skew_contract(version_skew, now)
    errors.extend(f"version_skew: {error}" for error in skew_errors)
    if skew_errors and readback.get("status") == "fresh":
        errors.append("fresh readback requires current version-skew evidence")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AO Architecture evidence freshness and gate readiness")
    parser.add_argument("--readback", type=Path, default=DEFAULT_READBACK)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--version-skew", type=Path, default=DEFAULT_VERSION_SKEW)
    parser.add_argument("--now", help="RFC3339 UTC timestamp for deterministic verification")
    args = parser.parse_args()
    try:
        readback = read_json(args.readback)
        manifest = read_json(args.manifest)
        matrix = read_json(args.matrix)
        version_skew = read_strict_json(args.version_skew)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"verify_evidence_freshness.py: {exc}", file=sys.stderr)
        return 1
    now = datetime.now(timezone.utc)
    if args.now:
        timestamp_errors: list[str] = []
        parsed = parse_timestamp(args.now, "now", timestamp_errors)
        if timestamp_errors or parsed is None:
            print("verify_evidence_freshness.py: now must be an RFC3339 UTC timestamp", file=sys.stderr)
            return 1
        now = parsed
    local_paths = {
        str(path.relative_to(ROOT))
        for path in (ROOT / "stack" / "fixtures" / "compatibility").glob("*.json")
    }
    errors = validate_live_readback(readback, manifest, matrix, version_skew, now, local_paths)
    if errors:
        for error in errors:
            print(f"verify_evidence_freshness.py: {error}", file=sys.stderr)
        return 1
    gate = readback["compatibility_gate"]["state"]
    edge_count = readback["compatibility_matrix"]["edge_count"]
    status = readback["status"]
    print(f"verify_evidence_freshness.py: evidence {status}; gate={gate}; edges={edge_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
