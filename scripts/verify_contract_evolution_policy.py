from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "stack" / "contract-evolution-policy.json"
DEFAULT_MATRIX = ROOT / "stack" / "contract-compatibility-matrix.json"
EDGE_FIELDS = (
    "producer",
    "consumer",
    "contract_family",
    "producer_contract",
    "consumer_contract",
)
MATRIX_PROOF_FIELDS = ("repository", "path", "pr", "merge_commit")
REQUIRED_DIRECTIONS = (
    "old_producer_to_new_consumer",
    "new_producer_to_old_consumer",
    "current_producer_to_current_consumer",
    "rollback_to_previous_supported_contract",
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SCHEMA_RE = re.compile(r"^ao\.[a-z0-9.-]+\.v[1-9][0-9]*$")
VERSION_RE = re.compile(r"^v[0-9]+(?:\.[0-9]+){0,2}$")
TOP_LEVEL_FIELDS = {
    "schema",
    "status",
    "policy_owner",
    "registry_authority",
    "compatibility_matrix",
    "evidence_semantics",
    "rules",
    "non_edge_change_sets",
    "edges",
    "coverage",
    "safety",
}
EVIDENCE_SEMANTIC_FIELDS = {
    "current_pair_status",
    "two_version_status",
    "missing_predecessor",
    "digest_scope",
}
EXPECTED_EVIDENCE_SEMANTICS = {
    "current_pair_status": "tested_current_release_pair proves only the recorded producer and consumer pair",
    "two_version_status": "requires executable evidence for every required direction and an explicit predecessor",
    "missing_predecessor": "must remain current_pair_only and must not be represented by an invented version",
    "digest_scope": "sha256 and byte_length bind canonical-vector bytes at the matrix-recorded merge commit",
}
RULE_FIELDS = {
    "minimum_supported_releases_after_version_change",
    "breaking_change_requires_new_major",
    "additive_optional_unknown_fields_may_be_ignored",
    "unknown_required_fields_fail_with_bounded_error",
    "removal_requires_deprecation_notice",
    "removal_requires_migration_and_rollback_evidence",
    "declared_change_required_directions",
}
EDGE_RECORD_FIELDS = {
    *EDGE_FIELDS,
    "canonical_vector",
    "consumer_test",
    "evolution",
}
CANONICAL_VECTOR_FIELDS = {
    *MATRIX_PROOF_FIELDS,
    "schema_identifier",
    "sha256",
    "byte_length",
}
CONSUMER_TEST_FIELDS = {
    *MATRIX_PROOF_FIELDS,
    "test_selector",
    "sha256",
    "byte_length",
}
UNCHANGED_EVOLUTION_FIELDS = {
    "declared_change",
    "documented_predecessors",
    "status",
    "directional_evidence",
}
DECLARED_EVOLUTION_FIELDS = {
    *UNCHANGED_EVOLUTION_FIELDS,
    "current_version",
}
TRUSTED_EDGE_EVIDENCE_DIGESTS = {
    "ao-architecture|ao-mission|authority_and_topology": "000ba79860b20a00f7a72916f4b4e1ab3ff1523e2ca6094269b909514771734b",
    "ao-architecture|ao-blueprint|authority_and_topology": "0b574e921e43829378ef92a949773bef33672e3129fedd3eca2fece88259ab29",
    "ao-blueprint|ao-atlas|requirements_to_workgraph": "4c7ac3ae243613fb3fffd3f6fefd12d4290e456bc24a3bf6b757aa3391763893",
    "ao-atlas|ao-foundry|workgraph_to_schedule": "4d4491f4ae104f68d42329056cb3e2f3d916716ac6c9f6e57a415ed3ccd71424",
    "ao-foundry|ao-forge|schedule_to_goal_run": "d70238919b4a0239d05fca0575f6b8387b59db67affd0516fdd69c45e4cb1467",
    "ao-forge|ao-covenant|goal_run_to_policy_gate": "4f6a20f2fb0eb609a63808a3e7819c2c4ae878377e1b93f59874e619131b73cd",
    "ao-covenant|ao2|approval_to_execution": "277994cd40806bfef6ded2f8b9e340199a9efa299bad4071b57d10a0cdd75b0b",
    "ao2|ao2-control-plane|execution_to_observation": "c3dabdf36bddb506163d466e5e59f30068a30775d410241358aeaef08a71ba3b",
    "ao-mission|ao-command|mission_to_operator_readback": "15055ee470a2a39b14b1ce647f58b83e9f58b77393dc7553fcc10c8dc7842707",
    "ao2-control-plane|ao-command|observer_to_operator_readback": "1e6d0db64cd24ad2a0395c10486cf6ed0335680b40d97eb31b47a796b5f219d8",
    "ao-arena|ao-promoter|benchmark_to_promotion": "151d674dc9965231c82254e0b27999c46a2bf06a8c407b4c3c5221d33b46a012",
    "ao-crucible|ao-promoter|adversarial_probe_to_promotion": "546499e6f5250e0c41cdb84a436a41a947bb91f597e013feac80ff61beb8ef33",
    "ao-sentinel|ao-promoter|safety_verdict_to_promotion": "dff738ce31fed8fefdfe35f858911a9a2d7b91128b23d28afd4756f8c917a1d3",
    "ao-promoter|ao-command|promotion_to_operator_readback": "34fca958b55702af9ea37031bee6f0d079b0c55707b3ee15c92fe2391eb48409",
    "ao-covenant|ao-command|policy_to_operator_explanation": "7c755ebb6d27706892ba3293a32ad532fa250ed08c93007d851d505fddec2e53",
    "ao-forge|ao-command|goal_run_to_operator_readback": "f4353abc127049be4f9baa46e7b26a9a5828ec4b39676f7590ce0d8e9209c746",
}
# A declared change remains fail-closed until review pins its complete proof record here.
TRUSTED_CHANGE_EVIDENCE_DIGESTS: dict[str, str] = {}
NON_EDGE_CHANGE_SET_FIELDS = {
    "id",
    "repository",
    "change_kind",
    "old_commit",
    "current_commit",
    "status",
    "predecessor",
    "contracts",
    "evidence_document",
}
TRUSTED_NON_EDGE_CHANGE_SET_DIGESTS = {
    "mission-lifecycle-correlation-additive-b02666e": (
        "f72b4f83a23fd385fda20d6e846e325bcb60397a7c172b143099f8f8d08c5d0a"
    ),
    "mission-objective-workflow-contract-v0.1-introduction": (
        "eee3264ccfc3d8b580298afc463c60fa8b9a5724332ec5a7a0e2c058d8431710"
    ),
    "ao2-github-draft-pr-v1-introduction": (
        "fcb0faa309c22f5fa6bf95ce2202d66ae85909c7f8405f19c9d1eb2c2135f507"
    ),
    "mission-correlation-chain-v0.1-introduction": (
        "1a4cff9933c9aa683ae91ce2b33d5ee703245361b22b4e4fb69b1cd61215e4e1"
    ),
    "mission-correlation-state-additive-7e7de94": (
        "3d73003f6230ff92b369d57856181bb73a40afd7cea1ddbec9f6cffb7ef3de67"
    ),
    "command-mission-status-correlation-additive-7cda85e": (
        "4b0dfa853144d3110e3bab95dceb632039d8d3023d9cb8bebe154d6f2a5f76f2"
    ),
}
COVERAGE_FIELDS = {
    "tracked_edge_count",
    "current_pair_evidence_count",
    "declared_change_count",
    "two_version_evidence_count",
    "invented_predecessor_count",
    "compatibility_activation_complete",
}
SAFETY_FIELDS = {
    "read_only_policy",
    "mutates_repositories",
    "promotion_granted",
    "rsi_remains_denied",
}


def _edge_key(edge: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(edge.get(field) for field in EDGE_FIELDS[:3])


def _edge_id(edge: dict[str, Any]) -> str:
    return "|".join(str(value) for value in _edge_key(edge))


def _canonical_digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _require_exact_fields(
    errors: list[str], label: str, value: dict[str, Any], expected: set[str]
) -> None:
    if set(value) != expected:
        errors.append(f"{label} fields must exactly match the strict schema")


def _require_object(
    errors: list[str], owner: dict[str, Any], label: str
) -> dict[str, Any] | None:
    value = owner.get(label.rsplit(".", 1)[-1])
    if not isinstance(value, dict):
        errors.append(f"{label} is required")
        return None
    return value


def _validate_matrix_proof(
    errors: list[str],
    label: str,
    proof: dict[str, Any],
    matrix_proof: dict[str, Any],
) -> None:
    for field in MATRIX_PROOF_FIELDS:
        if proof.get(field) != matrix_proof.get(field):
            errors.append(f"{label}.{field} must exactly match compatibility matrix")
    if not COMMIT_RE.fullmatch(str(proof.get("merge_commit", ""))):
        errors.append(f"{label}.merge_commit must be a full commit SHA")


def _validate_directional_proof(errors: list[str], label: str, proof: Any) -> None:
    if not isinstance(proof, dict):
        errors.append(f"{label} is required")
        return
    if proof.get("evidence_type") != "executable_test_at_merge_commit":
        errors.append(f"{label}.evidence_type must be executable_test_at_merge_commit")
    for field in ("repository", "path", "test_selector"):
        if not isinstance(proof.get(field), str) or not proof[field].strip():
            errors.append(f"{label}.{field} is required")
    if not COMMIT_RE.fullmatch(str(proof.get("merge_commit", ""))):
        errors.append(f"{label}.merge_commit must be a full commit SHA")
    if not SHA256_RE.fullmatch(str(proof.get("fixture_sha256", ""))):
        errors.append(f"{label}.fixture_sha256 must be a lowercase SHA-256")


def validate_policy(policy: dict[str, Any], matrix: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    _require_exact_fields(errors, "policy", policy, TOP_LEVEL_FIELDS)
    if policy.get("schema") != "ao.architecture.contract-evolution-policy.v1":
        errors.append("schema must be ao.architecture.contract-evolution-policy.v1")
    if policy.get("status") != "enforced":
        errors.append("status must be enforced")
    if policy.get("policy_owner") != "ao-architecture":
        errors.append("policy_owner must be ao-architecture")
    if policy.get("registry_authority") != "ao-covenant":
        errors.append("registry_authority must be ao-covenant")
    if policy.get("compatibility_matrix") != "stack/contract-compatibility-matrix.json":
        errors.append("compatibility_matrix must identify the Architecture matrix")

    semantics = policy.get("evidence_semantics")
    if not isinstance(semantics, dict):
        errors.append("evidence_semantics is required")
    else:
        _require_exact_fields(
            errors, "evidence_semantics", semantics, EVIDENCE_SEMANTIC_FIELDS
        )
        for field, expected in EXPECTED_EVIDENCE_SEMANTICS.items():
            if semantics.get(field) != expected:
                errors.append(f"evidence_semantics.{field} must match the trusted meaning")

    rules = policy.get("rules")
    if not isinstance(rules, dict):
        errors.append("rules is required")
        rules = {}
    else:
        _require_exact_fields(errors, "rules", rules, RULE_FIELDS)
    if rules.get("minimum_supported_releases_after_version_change") != 2:
        errors.append("rules.minimum_supported_releases_after_version_change must equal 2")
    if rules.get("declared_change_required_directions") != list(REQUIRED_DIRECTIONS):
        errors.append("rules.declared_change_required_directions must list all four directions")
    for field in (
        "breaking_change_requires_new_major",
        "additive_optional_unknown_fields_may_be_ignored",
        "unknown_required_fields_fail_with_bounded_error",
        "removal_requires_deprecation_notice",
        "removal_requires_migration_and_rollback_evidence",
    ):
        if rules.get(field) is not True:
            errors.append(f"rules.{field} must be true")

    change_sets = policy.get("non_edge_change_sets")
    if not isinstance(change_sets, list):
        errors.append("non_edge_change_sets is required")
        change_sets = []
    change_set_ids: list[str] = []
    for index, record in enumerate(change_sets):
        if not isinstance(record, dict):
            errors.append(f"non_edge_change_sets[{index}] must be an object")
            continue
        _require_exact_fields(
            errors,
            f"non_edge_change_sets[{index}]",
            record,
            NON_EDGE_CHANGE_SET_FIELDS,
        )
        record_id = record.get("id")
        if isinstance(record_id, str):
            change_set_ids.append(record_id)
        if record.get("evidence_document") != (
            "stack/contract-migration-and-rollback-results.json"
        ):
            errors.append(
                f"non_edge_change_sets[{index}].evidence_document must identify "
                "the governed migration results"
            )
        contracts = record.get("contracts")
        if (
            not isinstance(contracts, list)
            or not contracts
            or any(not isinstance(contract, str) or not contract for contract in contracts)
        ):
            errors.append(f"non_edge_change_sets[{index}].contracts must be nonempty")
        if (
            not isinstance(record_id, str)
            or TRUSTED_NON_EDGE_CHANGE_SET_DIGESTS.get(record_id)
            != _canonical_digest(record)
        ):
            errors.append(
                f"non_edge_change_sets {record_id} must match the trusted record"
            )
    if change_set_ids != list(TRUSTED_NON_EDGE_CHANGE_SET_DIGESTS):
        errors.append(
            "non_edge_change_sets must exactly list the six Month 3 records in order"
        )

    matrix_edges = matrix.get("edges") if isinstance(matrix.get("edges"), list) else []
    policy_edges = policy.get("edges") if isinstance(policy.get("edges"), list) else []
    if [_edge_key(edge) for edge in policy_edges] != [_edge_key(edge) for edge in matrix_edges]:
        errors.append("policy edges must exactly match compatibility matrix edges in order")

    declared_change_count = 0
    two_version_count = 0
    for index, edge in enumerate(policy_edges):
        if not isinstance(edge, dict):
            errors.append(f"edges[{index}] must be an object")
            continue
        matrix_edge = matrix_edges[index] if index < len(matrix_edges) else {}
        _require_exact_fields(errors, f"edges[{index}]", edge, EDGE_RECORD_FIELDS)
        for field in EDGE_FIELDS:
            if edge.get(field) != matrix_edge.get(field):
                errors.append(f"edges[{index}].{field} must match compatibility matrix")

        vector = _require_object(errors, edge, f"edges[{index}].canonical_vector")
        matrix_vector = matrix_edge.get("canonical_vector", {})
        if vector is not None:
            _require_exact_fields(
                errors,
                f"edges[{index}].canonical_vector",
                vector,
                CANONICAL_VECTOR_FIELDS,
            )
            _validate_matrix_proof(errors, f"edges[{index}].canonical_vector", vector, matrix_vector)
            if not SCHEMA_RE.fullmatch(str(vector.get("schema_identifier", ""))):
                errors.append(f"edges[{index}].canonical_vector.schema_identifier must be versioned")
            if not SHA256_RE.fullmatch(str(vector.get("sha256", ""))):
                errors.append(f"edges[{index}].canonical_vector.sha256 must be a lowercase SHA-256")
            length = vector.get("byte_length")
            if not isinstance(length, int) or isinstance(length, bool) or length <= 0:
                errors.append(f"edges[{index}].canonical_vector.byte_length must be positive")

        consumer_test = _require_object(errors, edge, f"edges[{index}].consumer_test")
        matrix_test = matrix_edge.get("consumer_test", {})
        if consumer_test is not None:
            _require_exact_fields(
                errors,
                f"edges[{index}].consumer_test",
                consumer_test,
                CONSUMER_TEST_FIELDS,
            )
            _validate_matrix_proof(
                errors, f"edges[{index}].consumer_test", consumer_test, matrix_test
            )
            if not isinstance(consumer_test.get("test_selector"), str) or not consumer_test[
                "test_selector"
            ].strip():
                errors.append(f"edges[{index}].consumer_test.test_selector is required")
            if not SHA256_RE.fullmatch(str(consumer_test.get("sha256", ""))):
                errors.append(
                    f"edges[{index}].consumer_test.sha256 must be a lowercase SHA-256"
                )
            length = consumer_test.get("byte_length")
            if not isinstance(length, int) or isinstance(length, bool) or length <= 0:
                errors.append(f"edges[{index}].consumer_test.byte_length must be positive")

        evidence_digest = _canonical_digest(
            {"canonical_vector": vector, "consumer_test": consumer_test}
        )
        if TRUSTED_EDGE_EVIDENCE_DIGESTS.get(_edge_id(edge)) != evidence_digest:
            errors.append(
                f"edges[{index}] vector and consumer evidence must match the trusted digest"
            )

        evolution = _require_object(errors, edge, f"edges[{index}].evolution")
        if evolution is None:
            continue
        if evolution.get("declared_change") is False:
            _require_exact_fields(
                errors,
                f"edges[{index}].evolution",
                evolution,
                UNCHANGED_EVOLUTION_FIELDS,
            )
        declared = evolution.get("declared_change")
        predecessors = evolution.get("documented_predecessors")
        evidence = evolution.get("directional_evidence")
        if not isinstance(predecessors, list):
            errors.append(f"edges[{index}].evolution.documented_predecessors must be a list")
            predecessors = []
        if not isinstance(evidence, dict):
            errors.append(f"edges[{index}].evolution.directional_evidence must be an object")
            evidence = {}

        if declared is False:
            if predecessors:
                errors.append(
                    f"edges[{index}].evolution must not invent predecessors without a declared change"
                )
            if evolution.get("status") != "current_pair_only":
                errors.append(f"edges[{index}].evolution.status must be current_pair_only")
            if evidence:
                errors.append(
                    f"edges[{index}].evolution.directional_evidence must be empty without a declared change"
                )
            continue
        if declared is not True:
            errors.append(f"edges[{index}].evolution.declared_change must be boolean")
            continue

        declared_change_count += 1
        _require_exact_fields(
            errors,
            f"edges[{index}].evolution",
            evolution,
            DECLARED_EVOLUTION_FIELDS,
        )
        current = evolution.get("current_version")
        if not VERSION_RE.fullmatch(str(current or "")):
            errors.append(f"edges[{index}].evolution.current_version must be a documented version")
        if len(predecessors) != 1 or not VERSION_RE.fullmatch(str(predecessors[0] if predecessors else "")):
            errors.append(
                f"edges[{index}].evolution must document exactly one predecessor version"
            )
        if predecessors and predecessors[0] == current:
            errors.append(f"edges[{index}].evolution predecessor must differ from current_version")
        if (
            predecessors
            and VERSION_RE.fullmatch(str(predecessors[0]))
            and VERSION_RE.fullmatch(str(current or ""))
        ):
            parse_version = lambda value: tuple(
                int(part) for part in value.removeprefix("v").split(".")
            )
            previous_parts = parse_version(predecessors[0])
            current_parts = parse_version(current)
            width = max(len(previous_parts), len(current_parts))
            if previous_parts + (0,) * (width - len(previous_parts)) >= current_parts + (
                0,
            ) * (width - len(current_parts)):
                errors.append(
                    f"edges[{index}].evolution predecessor must be older than current_version"
                )
        if evolution.get("status") != "two_version_evidence_complete":
            errors.append(f"edges[{index}].evolution.status must be two_version_evidence_complete")
        for direction in REQUIRED_DIRECTIONS:
            _validate_directional_proof(
                errors,
                f"edges[{index}].evolution.directional_evidence.{direction}",
                evidence.get(direction),
            )
        if set(evidence) == set(REQUIRED_DIRECTIONS):
            two_version_count += 1
        if TRUSTED_CHANGE_EVIDENCE_DIGESTS.get(_edge_id(edge)) != _canonical_digest(
            evolution
        ):
            errors.append(
                f"edges[{index}].evolution declared change lacks trusted executable evidence"
            )

    coverage = policy.get("coverage")
    if not isinstance(coverage, dict):
        errors.append("coverage is required")
    else:
        _require_exact_fields(errors, "coverage", coverage, COVERAGE_FIELDS)
        expected = {
            "tracked_edge_count": len(matrix_edges),
            "current_pair_evidence_count": len(matrix_edges),
            "declared_change_count": declared_change_count,
            "two_version_evidence_count": two_version_count,
            "invented_predecessor_count": 0,
            "compatibility_activation_complete": declared_change_count > 0
            and declared_change_count == two_version_count,
        }
        for field, value in expected.items():
            if coverage.get(field) != value:
                errors.append(f"coverage.{field} must equal {value!r}")

    safety = policy.get("safety")
    if not isinstance(safety, dict):
        errors.append("safety is required")
    else:
        _require_exact_fields(errors, "safety", safety, SAFETY_FIELDS)
        expected_safety = {
            "read_only_policy": True,
            "mutates_repositories": False,
            "promotion_granted": False,
            "rsi_remains_denied": True,
        }
        for field, value in expected_safety.items():
            if safety.get(field) is not value:
                errors.append(f"safety.{field} must be {str(value).lower()}")
    return errors


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the AO contract evolution policy")
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    args = parser.parse_args()
    try:
        policy = _read_json(args.policy)
        matrix = _read_json(args.matrix)
    except (OSError, json.JSONDecodeError) as error:
        print(f"verify_contract_evolution_policy.py: {error}", file=sys.stderr)
        return 1
    errors = validate_policy(policy, matrix)
    if errors:
        for error in errors:
            print(f"verify_contract_evolution_policy.py: {error}", file=sys.stderr)
        return 1
    print(
        "verify_contract_evolution_policy.py: "
        f"bound {len(policy['edges'])} current-pair edges; "
        f"two-version changes={policy['coverage']['two_version_evidence_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
