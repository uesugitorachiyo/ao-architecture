#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS = ROOT / "stack" / "contract-migration-and-rollback-results.json"
DEFAULT_CROSS_VERSION_RESULTS = (
    ROOT / "stack" / "contract-cross-version-fixture-results.json"
)
DIRECTIONS = (
    "old_producer_to_new_consumer",
    "new_producer_to_old_consumer",
    "current_producer_to_current_consumer",
    "rollback_to_previous_supported_contract",
)
MISSION_CHANGE_ID = "mission-lifecycle-correlation-additive-b02666e"
MISSION_CONTRACT_ID = "mission-objective-workflow-contract-v0.1-introduction"
AO2_CHANGE_ID = "ao2-github-draft-pr-v1-introduction"
MISSION_CHAIN_ID = "mission-correlation-chain-v0.1-introduction"
MISSION_STATE_ID = "mission-correlation-state-additive-7e7de94"
COMMAND_STATUS_ID = "command-mission-status-correlation-additive-7cda85e"
MISSION_OLD = "d10bc1986fe1ea5d9ac58454db4fffc08ab76bdd"
MISSION_CURRENT = "b02666e7df36ea1d8f325dacedcc22d2a95099e4"
SOURCE_SHA = "0ae9490e5243163ac7ef238e0b88528677e14e731492002b98f984476a0f57c7"
EVIDENCE_FIELDS = {
    "status",
    "evidence_type",
    "source_repository",
    "source_commit",
    "source_path",
    "source_sha256",
    "test_selector",
}
AO2_CONTRACTS = [
    "ao2.github-draft-pr-evidence.v1",
    "ao2.github-draft-pr-action.v1",
    "ao2.github-draft-pr-verification.v1",
    "ao2.github-draft-pr-fixture-publish.v1",
]
RESULT_IDS = (
    MISSION_CHANGE_ID,
    MISSION_CONTRACT_ID,
    AO2_CHANGE_ID,
    MISSION_CHAIN_ID,
    MISSION_STATE_ID,
    COMMAND_STATUS_ID,
)
ADDITIVE_RESULT_FIELDS = {
    "id",
    "repository",
    "old_commit",
    "current_commit",
    "status",
    "failed_direction_count",
    "unproven_direction_count",
    "directional_evidence",
    "cross_version_fixture_ids",
    "fixture_bindings",
}
EXPECTED_CROSS_VERSION_FIXTURE_IDS = {
    MISSION_CHANGE_ID: [
        "mission-lifecycle-d10bc19-to-b02666e",
        "mission-lifecycle-b02666e-to-d10bc19",
    ],
    MISSION_STATE_ID: [
        "mission-correlation-state-7e7de94-to-b02666e",
        "mission-correlation-state-b02666e-to-7e7de94",
    ],
    COMMAND_STATUS_ID: [
        "command-correlation-status-7cda85e-to-822345d",
    ],
}
TRUSTED_CROSS_VERSION_RESULTS_DIGEST = (
    "579a647e242a818483595d586c9abdb032847e6621a3cfa3a58c989aa69e25a5"
)
CROSS_VERSION_FIXTURE_FIELDS = {
    "id",
    "direction",
    "producer_repository",
    "producer_commit",
    "consumer_repository",
    "consumer_commit",
    "exit_code",
    "result",
    "fixture_path",
    "fixture_sha256",
    "readback_path",
    "readback_sha256",
}
ADDITIVE_EVIDENCE_FIELDS = {
    "status",
    "source_commit",
    "source_path",
    "source_sha256",
    "test_selector",
}


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


# These digests pin the complete result records, including immutable external
# source paths and hashes. Update them only after reviewing new merged evidence.
TRUSTED_RESULT_DIGESTS = {
    MISSION_CHANGE_ID: (
        "3f7c00a6f1763416a5af575af02940b14bef988a1ec7a3782ed614428c87de74"
    ),
    MISSION_CONTRACT_ID: (
        "ffcedf5b54376d2a006f1d4cd5f131fcb93ad02e8caef0cb82e8e0b4f3337a37"
    ),
    AO2_CHANGE_ID: (
        "7b0e32b71b42b604538fe65f76a570e6f680312cfa552e6773a56acb46fd8850"
    ),
    MISSION_CHAIN_ID: (
        "a55c433fbb32c3ea72a00c6705ade0b380479f2647608040afee7c2a42a070c2"
    ),
    MISSION_STATE_ID: (
        "a2d08bc68e993049b0fb29cc9742a31ba56727717542f247bfa3cafec50e7142"
    ),
    COMMAND_STATUS_ID: (
        "6e480e9d42bebea90e2c6daaf1b455d40b7f943fe753e18f297f72893663cb67"
    ),
}


def validate_document(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if set(document) != {"schema", "status", "policy", "results", "safety"}:
        errors.append("document fields must exactly match the strict schema")
    if (
        document.get("schema")
        != "ao.architecture.contract-migration-and-rollback-results.v1"
    ):
        errors.append(
            "schema must be ao.architecture.contract-migration-and-rollback-results.v1"
        )
    if document.get("status") != "current":
        errors.append("status must be current")
    if document.get("policy") != "stack/contract-evolution-policy.json":
        errors.append("policy must identify the contract evolution policy")
    results = document.get("results")
    if not isinstance(results, list):
        errors.append("results is required")
        results = []
    ids = [
        result.get("id")
        for result in results
        if isinstance(result, dict)
    ]
    if ids != list(RESULT_IDS):
        errors.append("results must exactly list the six Month 3 change sets")

    for result in results:
        if not isinstance(result, dict):
            errors.append("each result must be an object")
            continue
        result_id = result.get("id")
        if result_id == MISSION_CHANGE_ID:
            expected_fields = {
                "id",
                "repository",
                "old_commit",
                "current_commit",
                "status",
                "failed_direction_count",
                "unproven_direction_count",
                "directional_evidence",
                "cross_version_fixture_ids",
                "supplementary_current_pair_selectors",
                "fixture_bindings",
            }
            if set(result) != expected_fields:
                errors.append(f"{result_id} fields must exactly match the strict schema")
            evidence = result.get("directional_evidence")
            if not isinstance(evidence, dict) or set(evidence) != set(DIRECTIONS):
                errors.append(
                    f"{result_id} directional_evidence must contain all four directions"
                )
                evidence = evidence if isinstance(evidence, dict) else {}
            for direction in DIRECTIONS:
                proof = evidence.get(direction)
                if not isinstance(proof, dict) or set(proof) != EVIDENCE_FIELDS:
                    errors.append(
                        f"{direction} evidence fields must exactly match the strict schema"
                    )
            if (
                result.get("repository") != "ao-mission"
                or result.get("old_commit") != MISSION_OLD
                or result.get("current_commit") != MISSION_CURRENT
                or result.get("status") != "passed"
                or result.get("failed_direction_count") != 0
                or result.get("unproven_direction_count") != 0
                or result.get("cross_version_fixture_ids")
                != EXPECTED_CROSS_VERSION_FIXTURE_IDS[MISSION_CHANGE_ID]
                or TRUSTED_RESULT_DIGESTS[result_id] != _digest(result)
            ):
                errors.append(
                    f"{result_id} evidence must match trusted immutable bindings"
                )
        elif result_id == MISSION_CONTRACT_ID:
            expected_fields = {
                "id",
                "repository",
                "current_commit",
                "status",
                "contract",
                "current_pair_evidence",
                "predecessor_results",
            }
            if set(result) != expected_fields:
                errors.append(f"{result_id} fields must exactly match the strict schema")
            predecessor = result.get("predecessor_results")
            expected_predecessor = {
                "old_producer_to_new_consumer": "not_applicable_no_predecessor",
                "new_producer_to_old_consumer": "not_applicable_no_predecessor",
                "rollback_to_previous_supported_contract": (
                    "not_applicable_no_predecessor"
                ),
            }
            if predecessor != expected_predecessor:
                errors.append(f"{result_id} must not invent predecessor results")
            if TRUSTED_RESULT_DIGESTS[result_id] != _digest(result):
                errors.append(
                    f"{result_id} evidence must match trusted immutable bindings"
                )
        elif result_id == AO2_CHANGE_ID:
            expected_fields = {
                "id",
                "repository",
                "status",
                "current_commit",
                "contracts",
                "private_protocol_pattern",
                "predecessor_results",
                "current_pair_evidence",
            }
            if set(result) != expected_fields:
                errors.append(f"{result_id} fields must exactly match the strict schema")
            if (
                result.get("status") != "current_pair_only"
                or result.get("current_commit")
                != "aaa36fb13675396b60ed9a63bd94aa665be9eb5c"
                or result.get("current_pair_evidence", {}).get("status") != "passed"
            ):
                errors.append(f"{result_id} must bind the merged passing current pair")
            if result.get("contracts") != AO2_CONTRACTS:
                errors.append(f"{result_id} must list exactly the four public contracts")
            if result.get("private_protocol_pattern") != "ao2.local-draft-pr-fixture-*":
                errors.append(f"{result_id} must classify the private fixture protocols")
            if TRUSTED_RESULT_DIGESTS[result_id] != _digest(result):
                errors.append(
                    f"{result_id} evidence must match trusted immutable bindings"
                )
        elif result_id == MISSION_CHAIN_ID:
            expected_fields = {
                "id",
                "repository",
                "status",
                "current_commit",
                "contracts",
                "predecessor_results",
                "current_pair_evidence",
            }
            if set(result) != expected_fields:
                errors.append(f"{result_id} fields must exactly match the strict schema")
            if (
                result.get("repository") != "ao-mission"
                or result.get("status") != "current_pair_only"
                or result.get("current_commit")
                != "7e7de94af5f2f463fb18a7d2fdf829e66787167f"
                or result.get("current_pair_evidence", {}).get("status") != "passed"
            ):
                errors.append(f"{result_id} must bind the merged passing current pair")
            expected_predecessor = {
                "old_producer_to_new_consumer": "not_applicable_no_predecessor",
                "new_producer_to_old_consumer": "not_applicable_no_predecessor",
                "rollback_to_previous_supported_contract": (
                    "not_applicable_no_predecessor"
                ),
            }
            if result.get("predecessor_results") != expected_predecessor:
                errors.append(f"{result_id} must not invent predecessor results")
            if TRUSTED_RESULT_DIGESTS[result_id] != _digest(result):
                errors.append(
                    f"{result_id} evidence must match trusted immutable bindings"
                )
        elif result_id in {MISSION_STATE_ID, COMMAND_STATUS_ID}:
            expected_fields = set(ADDITIVE_RESULT_FIELDS)
            if result_id == COMMAND_STATUS_ID:
                expected_fields.add("current_pair_rejection_selectors")
            if set(result) != expected_fields:
                errors.append(f"{result_id} fields must exactly match the strict schema")
            evidence = result.get("directional_evidence")
            if not isinstance(evidence, dict) or set(evidence) != set(DIRECTIONS):
                errors.append(
                    f"{result_id} directional_evidence must contain all four directions"
                )
                evidence = evidence if isinstance(evidence, dict) else {}
            for direction in DIRECTIONS:
                proof = evidence.get(direction)
                if not isinstance(proof, dict) or set(proof) != ADDITIVE_EVIDENCE_FIELDS:
                    errors.append(
                        f"{result_id} {direction} evidence fields must exactly "
                        "match the strict schema"
                    )
                elif (
                    proof.get("status")
                    != "passed"
                    or not re.fullmatch(r"[0-9a-f]{40}", str(proof.get("source_commit", "")))
                    or not re.fullmatch(r"[0-9a-f]{64}", str(proof.get("source_sha256", "")))
                ):
                    errors.append(
                        f"{result_id} {direction} evidence must match its honest "
                        "immutable status"
                    )
            if (
                result.get("status") != "passed"
                or result.get("failed_direction_count") != 0
                or result.get("unproven_direction_count") != 0
                or result.get("cross_version_fixture_ids")
                != EXPECTED_CROSS_VERSION_FIXTURE_IDS[result_id]
            ):
                errors.append(f"{result_id} must pass all four bound directions")
            if TRUSTED_RESULT_DIGESTS[result_id] != _digest(result):
                errors.append(
                    f"{result_id} evidence must match trusted immutable bindings"
                )
        else:
            errors.append(f"unexpected result id: {result_id}")

    expected_safety = {
        "claims_unrun_tests": False,
        "invents_predecessors": False,
        "activates_compatibility_gate": False,
        "grants_release_authority": False,
    }
    if document.get("safety") != expected_safety:
        errors.append("safety must preserve the bounded Month 3 authority")
    return errors


def validate_cross_version_document(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != (
        "ao.architecture.contract-cross-version-fixture-results.v1"
    ):
        errors.append("cross-version fixture schema must match")
    if document.get("status") != "passed" or document.get("credential_free") is not True:
        errors.append("cross-version fixtures must be passed and credential-free")
    fixtures = document.get("fixtures")
    fixture_ids = [
        fixture.get("id") for fixture in fixtures if isinstance(fixture, dict)
    ] if isinstance(fixtures, list) else []
    expected_ids = [
        fixture_id
        for result_id in (MISSION_CHANGE_ID, MISSION_STATE_ID, COMMAND_STATUS_ID)
        for fixture_id in EXPECTED_CROSS_VERSION_FIXTURE_IDS[result_id]
    ]
    if fixture_ids != expected_ids:
        errors.append("cross-version fixtures must exactly match the trusted order")
    if isinstance(fixtures, list):
        for fixture in fixtures:
            if not isinstance(fixture, dict):
                errors.append("cross-version fixture rows must be objects")
                continue
            fixture_id = fixture.get("id")
            if set(fixture) != CROSS_VERSION_FIXTURE_FIELDS:
                errors.append(f"{fixture_id} fields must match the strict schema")
                continue
            for role in ("producer", "consumer"):
                if not re.fullmatch(
                    r"[0-9a-f]{40}", str(fixture.get(f"{role}_commit", ""))
                ):
                    errors.append(f"{fixture_id} {role}_commit must be immutable")
            if fixture.get("exit_code") != 0:
                errors.append(f"{fixture_id} exit_code must be zero")
            for path_field, digest_field in (
                ("fixture_path", "fixture_sha256"),
                ("readback_path", "readback_sha256"),
            ):
                relative = fixture.get(path_field)
                if (
                    not isinstance(relative, str)
                    or not relative.startswith(
                        "stack/fixtures/contract-cross-version/"
                    )
                    or Path(relative).is_absolute()
                    or ".." in Path(relative).parts
                ):
                    errors.append(f"{fixture_id} {path_field} must be bounded")
                    continue
                path = ROOT / relative
                try:
                    actual = hashlib.sha256(path.read_bytes()).hexdigest()
                except OSError as error:
                    errors.append(f"{fixture_id} {path_field}: {error}")
                    continue
                if actual != fixture.get(digest_field):
                    errors.append(f"{fixture_id} {digest_field} must match bytes")
    boundaries = document.get("boundaries")
    if boundaries != {
        "network_used": False,
        "credentials_used": False,
        "source_repository_content_mutation_performed": False,
        "temporary_worktree_metadata_used": True,
        "public_write_performed": False,
        "release_or_publication_performed": False,
    }:
        errors.append("cross-version fixture boundaries must remain bounded")
    runner = document.get("runner")
    if runner != {
        "path": "scripts/run_contract_cross_version_fixtures.py",
        "sha256": "8057718104e5a35f2fe92fa427e418206f32748735e989796529884a6721142f",
        "local_status": "passed",
        "hosted_ci_required": True,
    }:
        errors.append("cross-version fixture runner must match the trusted binding")
    else:
        runner_path = ROOT / runner["path"]
        try:
            runner_digest = hashlib.sha256(runner_path.read_bytes()).hexdigest()
        except OSError as error:
            errors.append(f"cross-version fixture runner: {error}")
        else:
            if runner_digest != runner["sha256"]:
                errors.append("cross-version fixture runner digest must match bytes")
    if _digest(document) != TRUSTED_CROSS_VERSION_RESULTS_DIGEST:
        errors.append("cross-version fixture results must match the trusted digest")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate AO contract migration and rollback results"
    )
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument(
        "--cross-version-results",
        type=Path,
        default=DEFAULT_CROSS_VERSION_RESULTS,
    )
    args = parser.parse_args()
    try:
        document = json.loads(args.results.read_text(encoding="utf-8"))
        cross_version_document = json.loads(
            args.cross_version_results.read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as error:
        print(
            f"verify_contract_migration_and_rollback_results.py: {error}",
            file=sys.stderr,
        )
        return 1
    errors = validate_document(document)
    errors.extend(validate_cross_version_document(cross_version_document))
    if errors:
        for error in errors:
            print(
                f"verify_contract_migration_and_rollback_results.py: {error}",
                file=sys.stderr,
            )
        return 1
    print(
        "verify_contract_migration_and_rollback_results.py: "
        "validated six immutable Month 3 migration and rollback results"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
