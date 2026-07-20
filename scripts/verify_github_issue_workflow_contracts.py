#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACTS = ROOT / "stack" / "github-issue-workflow-contracts.json"

REQUIRED_SCHEMAS = (
    "issue_url_intake",
    "immutable_issue_snapshot",
    "repository_identity_target_revision",
    "issue_authenticity_assessment",
    "reproduction_plan_result",
    "repair_plan_result",
    "fork_branch_routing",
    "action_digest_approval",
    "draft_pr_request_readback",
    "evidence_pack",
    "terminal_state_next_action",
)
REQUIRED_STATES = (
    "intake_validated",
    "invalid_url",
    "repository_unavailable",
    "issue_unavailable",
    "unsupported_host",
    "insufficient_evidence",
    "duplicate_or_superseded",
    "not_a_bug",
    "cannot_reproduce",
    "environment_blocked",
    "policy_blocked",
    "security_sensitive",
    "authentic_bug",
    "fix_in_progress",
    "fix_verified",
    "draft_pr_approval_required",
    "draft_pr_opened",
    "draft_pr_failed",
    "operator_action_required",
    "archived",
)
REQUIRED_POLICIES = (
    "safe_read_only_discovery",
    "repository_native_sandboxed_verification",
    "approval_required_dependency_or_network_operation",
    "approval_required_github_write",
    "permanently_denied_command_or_path",
)
REQUIRED_URL_REJECTIONS = (
    "pull_request_url",
    "discussion_url",
    "actions_url",
    "unsupported_host",
    "malformed_number",
    "identity_changing_fragment",
    "traversal",
    "ambiguous_redirect",
)
REQUIRED_FIXTURES = (
    "valid_open_bug",
    "closed_relevant_bug",
    "malformed_url",
    "unsupported_host",
    "pr_url_supplied_as_issue",
    "nonexistent_issue",
    "inaccessible_repository",
    "duplicate",
    "feature_request",
    "expected_behavior",
    "insufficient_evidence",
    "already_fixed_report",
    "security_sensitive_report",
    "issue_body_prompt_injection",
    "repository_instruction_prompt_injection",
)
FAIL_CLOSED_FIXTURES = {
    "security_sensitive_report": "security_sensitive",
    "issue_body_prompt_injection": "policy_blocked",
    "repository_instruction_prompt_injection": "policy_blocked",
}
REQUIRED_METRICS = (
    "classification",
    "injection_rejection",
    "denied_action",
    "evidence_integrity",
    "elapsed_time",
    "retries",
    "operator_intervention",
)
MONTH1_FALSE_BOUNDARIES = (
    "fork_created",
    "branch_pushed",
    "draft_pr_opened",
    "issue_write_performed",
    "maintainer_contacted",
    "security_disclosed_publicly",
    "release_published",
    "rsi_authorized",
)
AO2_PUBLIC_DRAFT_PR_CONTRACTS = (
    "ao2.github-draft-pr-evidence.v1",
    "ao2.github-draft-pr-action.v1",
    "ao2.github-draft-pr-verification.v1",
    "ao2.github-draft-pr-fixture-publish.v1",
)
AO2_DRAFT_PR_COMMIT = "aaa36fb13675396b60ed9a63bd94aa665be9eb5c"


def _names(entries: Any, field: str) -> set[str]:
    if not isinstance(entries, list):
        return set()
    names: set[str] = set()
    for entry in entries:
        if isinstance(entry, dict) and isinstance(entry.get(field), str):
            names.add(entry[field])
    return names


def _validate_string_list(errors: list[str], value: Any, required: tuple[str, ...], missing_prefix: str) -> None:
    if not isinstance(value, list):
        errors.append(f"{missing_prefix} list is required")
        return
    values = {item for item in value if isinstance(item, str)}
    for item in required:
        if item not in values:
            errors.append(f"missing {missing_prefix}: {item}")


def validate_document(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != "ao.architecture.github-issue-workflow-contracts.v0.1":
        errors.append("schema must be ao.architecture.github-issue-workflow-contracts.v0.1")
    if document.get("status") != "ready":
        errors.append("status must be ready")

    workflow = document.get("workflow")
    if not isinstance(workflow, dict):
        errors.append("workflow is required")
    else:
        expected_booleans = {
            "current_public_pair_required": True,
            "single_issue_url_per_run": True,
            "feature_generated_pr_must_be_draft": True,
            "feature_generated_pr_auto_merge_authorized": False,
            "issue_write_authorized": False,
        }
        if workflow.get("name") != "github_issue_to_draft_pr":
            errors.append("workflow.name must be github_issue_to_draft_pr")
        for field, expected in expected_booleans.items():
            if workflow.get(field) is not expected:
                errors.append(f"workflow.{field} must be {str(expected).lower()}")

    schema_names = _names(document.get("schemas"), "name")
    for schema in REQUIRED_SCHEMAS:
        if schema not in schema_names:
            errors.append(f"missing schema: {schema}")
    if isinstance(document.get("schemas"), list):
        for index, entry in enumerate(document["schemas"]):
            if not isinstance(entry, dict):
                errors.append(f"schemas[{index}] must be an object")
                continue
            for field in ("name", "owner", "consumer"):
                if not isinstance(entry.get(field), str) or not entry[field]:
                    errors.append(f"schemas[{index}].{field} is required")

    _validate_string_list(errors, document.get("canonical_issue_states"), REQUIRED_STATES, "canonical issue state")
    _validate_string_list(errors, document.get("command_policy_classes"), REQUIRED_POLICIES, "command policy class")

    url = document.get("url_canonicalization")
    if not isinstance(url, dict):
        errors.append("url_canonicalization is required")
    else:
        if url.get("accepted_pattern") != "github.com/<owner>/<repo>/issues/<number>":
            errors.append("url_canonicalization.accepted_pattern must describe github issue URLs")
        _validate_string_list(errors, url.get("rejects"), REQUIRED_URL_REJECTIONS, "url rejection")

    trust = document.get("trust_model")
    if not isinstance(trust, dict):
        errors.append("trust_model is required")
    else:
        if trust.get("issue_text_can_authorize") is not False:
            errors.append("issue_text_can_authorize must be false")
        if trust.get("repository_text_can_authorize") is not False:
            errors.append("repository_text_can_authorize must be false")
        if trust.get("security_sensitive_stops_public_repair") is not True:
            errors.append("security_sensitive_stops_public_repair must be true")
        if not isinstance(trust.get("untrusted_inputs"), list) or len(trust["untrusted_inputs"]) < 10:
            errors.append("trust_model.untrusted_inputs must enumerate untrusted issue, repo, and GitHub inputs")

    fixtures = document.get("fixtures")
    fixture_ids = _names(fixtures, "id")
    for fixture in REQUIRED_FIXTURES:
        if fixture not in fixture_ids:
            errors.append(f"missing fixture: {fixture}")
    if isinstance(fixtures, list):
        for index, fixture in enumerate(fixtures):
            if not isinstance(fixture, dict):
                errors.append(f"fixtures[{index}] must be an object")
                continue
            fixture_id = fixture.get("id")
            expected_state = fixture.get("expected_state")
            if expected_state not in REQUIRED_STATES:
                errors.append(f"fixtures[{index}].expected_state must be a canonical issue state")
            if fixture_id in FAIL_CLOSED_FIXTURES and expected_state != FAIL_CLOSED_FIXTURES[fixture_id]:
                errors.append(f"fixture {fixture_id} must fail closed")

    metrics = document.get("baseline_metrics")
    if not isinstance(metrics, dict):
        errors.append("baseline_metrics is required")
    else:
        for metric in REQUIRED_METRICS:
            if metrics.get(metric) is not True:
                errors.append(f"baseline_metrics.{metric} must be true")

    boundaries = document.get("boundaries")
    if not isinstance(boundaries, dict):
        errors.append("boundaries is required")
    else:
        for boundary in MONTH1_FALSE_BOUNDARIES:
            if boundaries.get(boundary) is not False:
                errors.append(f"boundaries.{boundary} must remain false for Month 1")

    family = document.get("draft_pr_contract_family")
    if not isinstance(family, dict):
        errors.append("draft_pr_contract_family is required")
    else:
        expected_fields = {
            "status",
            "public_contracts",
            "private_executable_protocol_pattern",
            "private_protocols_are_public_stack_contracts",
            "immutable_commit",
        }
        if set(family) != expected_fields:
            errors.append(
                "draft_pr_contract_family fields must exactly match the strict schema"
            )
        if family.get("status") != "current_pair_only":
            errors.append(
                "draft_pr_contract_family.status must be current_pair_only"
            )
        if family.get("public_contracts") != list(AO2_PUBLIC_DRAFT_PR_CONTRACTS):
            errors.append(
                "draft_pr_contract_family.public_contracts must exactly match the "
                "four AO2 public contracts"
            )
        if (
            family.get("private_executable_protocol_pattern")
            != "ao2.local-draft-pr-fixture-*"
        ):
            errors.append(
                "draft_pr_contract_family.private_executable_protocol_pattern "
                "must identify the private fixture protocols"
            )
        if family.get("private_protocols_are_public_stack_contracts") is not False:
            errors.append(
                "draft_pr_contract_family.private_protocols_are_public_stack_contracts "
                "must be false"
            )
        if family.get("immutable_commit") != AO2_DRAFT_PR_COMMIT:
            errors.append(
                "draft_pr_contract_family.immutable_commit must bind the merged AO2 publisher"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AO GitHub issue-to-draft-PR Month 1 contracts")
    parser.add_argument("--contracts", type=Path, default=DEFAULT_CONTRACTS)
    args = parser.parse_args()
    try:
        document = json.loads(args.contracts.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"verify_github_issue_workflow_contracts.py: {exc}", file=sys.stderr)
        return 1
    errors = validate_document(document)
    if errors:
        for error in errors:
            print(f"verify_github_issue_workflow_contracts.py: {error}", file=sys.stderr)
        return 1
    print(
        "verify_github_issue_workflow_contracts.py: "
        f"validated {len(document['schemas'])} schemas and {len(document['fixtures'])} fixtures"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
