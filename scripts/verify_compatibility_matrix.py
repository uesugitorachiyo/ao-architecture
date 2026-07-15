from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MATRIX = ROOT / "stack" / "contract-compatibility-matrix.json"
ACTIVE_REPOSITORIES = {
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
COMPATIBILITY_STATUSES = {"pending_canonical_vectors", "tested_current_release_pair"}
COMMIT_RE = r"^[0-9a-f]{40}$"


def validate_proof_block(
    errors: list[str],
    edge: dict[str, Any],
    edge_index: int,
    field: str,
    expected_repository: str,
) -> bool:
    proof = edge.get(field)
    if not isinstance(proof, dict):
        errors.append(f"edges[{edge_index}].{field} is required for tested edges")
        return False
    ok = True
    if proof.get("repository") != expected_repository:
        errors.append(f"edges[{edge_index}].{field}.repository must be {expected_repository}")
        ok = False
    path = proof.get("path")
    if not isinstance(path, str) or not path:
        errors.append(f"edges[{edge_index}].{field}.path is required")
        ok = False
    elif path.startswith("/") or ".." in path.split("/"):
        errors.append(f"edges[{edge_index}].{field}.path must be repository-relative")
        ok = False
    pr = proof.get("pr")
    if not isinstance(pr, str) or not pr.startswith("https://github.com/uesugitorachiyo/"):
        errors.append(f"edges[{edge_index}].{field}.pr must point to a public GitHub PR")
        ok = False
    merge_commit = proof.get("merge_commit")
    if not isinstance(merge_commit, str) or not re.fullmatch(COMMIT_RE, merge_commit):
        errors.append(f"edges[{edge_index}].{field}.merge_commit must be a 40-character commit")
        ok = False
    return ok


def validate_document(document: dict[str, Any], expected_repositories: set[str] | None = None) -> list[str]:
    expected = expected_repositories or ACTIVE_REPOSITORIES
    errors: list[str] = []
    if document.get("schema") != "ao.architecture.contract-compatibility-matrix.v0.1":
        errors.append("schema must be ao.architecture.contract-compatibility-matrix.v0.1")
    if document.get("status") != "proposed":
        errors.append("status must remain proposed until compatibility gates pass")
    if document.get("registry_owner") != "ao-covenant":
        errors.append("registry_owner must be ao-covenant")
    if document.get("owner_registry") != "stack/contract-owner-registry.json":
        errors.append("owner_registry must point to stack/contract-owner-registry.json")

    edges = document.get("edges")
    if not isinstance(edges, list) or not edges:
        errors.append("edges must be a non-empty array")
        edges = []
    pairs: set[tuple[str, str, str]] = set()
    tested_edge_count = 0
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            errors.append(f"edges[{index}] must be an object")
            continue
        for field in ("producer", "consumer", "contract_family", "producer_contract", "consumer_contract"):
            if not isinstance(edge.get(field), str) or not edge[field]:
                errors.append(f"edges[{index}].{field} is required")
        producer = edge.get("producer")
        consumer = edge.get("consumer")
        if producer not in expected:
            errors.append(f"edges[{index}].producer is not an active repository")
        if consumer not in expected:
            errors.append(f"edges[{index}].consumer is not an active repository")
        if producer == consumer:
            errors.append(f"edges[{index}] producer and consumer must differ")
        compatibility_status = edge.get("compatibility_status")
        if compatibility_status not in COMPATIBILITY_STATUSES:
            errors.append(
                f"edges[{index}].compatibility_status must be pending_canonical_vectors or tested_current_release_pair"
            )
        if compatibility_status == "tested_current_release_pair":
            tested_edge_count += 1
            validate_proof_block(errors, edge, index, "canonical_vector", str(producer))
            validate_proof_block(errors, edge, index, "consumer_test", str(consumer))
        elif "canonical_vector" in edge or "consumer_test" in edge:
            errors.append(f"edges[{index}] pending edges must not carry tested evidence blocks")
        key = (str(producer), str(consumer), str(edge.get("contract_family")))
        if key in pairs:
            errors.append(f"edges[{index}] duplicates a producer/consumer contract family")
        pairs.add(key)

    coverage = document.get("coverage")
    if not isinstance(coverage, dict):
        errors.append("coverage is required")
    else:
        if coverage.get("edge_count") != len(edges):
            errors.append("coverage.edge_count must equal the edge count")
        if coverage.get("uncovered_owner_pairs") != 0:
            errors.append("coverage.uncovered_owner_pairs must be zero")
        if coverage.get("compatibility_gate_complete") is not False:
            errors.append("coverage.compatibility_gate_complete must remain false")
        if coverage.get("canonical_vector_count") != tested_edge_count:
            errors.append("coverage.canonical_vector_count must equal tested edge count")
        if coverage.get("consumer_test_count") != tested_edge_count:
            errors.append("coverage.consumer_test_count must equal tested edge count")

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
    parser = argparse.ArgumentParser(description="Validate the proposed AO producer/consumer compatibility matrix")
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    args = parser.parse_args()
    try:
        document = json.loads(args.matrix.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"verify_compatibility_matrix.py: {exc}", file=sys.stderr)
        return 1
    errors = validate_document(document)
    if errors:
        for error in errors:
            print(f"verify_compatibility_matrix.py: {error}", file=sys.stderr)
        return 1
    print(
        "verify_compatibility_matrix.py: validated "
        f"{len(document['edges'])} producer/consumer edges; "
        f"{document['coverage']['canonical_vector_count']} tested"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
