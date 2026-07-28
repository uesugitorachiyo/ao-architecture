import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import verify_github_issue_workflow_contracts as verifier


def valid_autonomous_family():
    return {
        "status": "current_pair_only",
        "predecessor": "not_applicable_no_predecessor",
        "validation_reference_time": "2026-07-27T16:00:00Z",
        "contracts": [
            {
                "name": name,
                "schema_id": schema_id,
                "path": path,
                "canonical_vector": vector,
                "owner": "ao-architecture",
                "consumers": ["ao-mission", "ao-atlas", "ao-forge", "ao-covenant", "ao2", "ao-command"],
            }
            for name, (schema_id, path, vector) in verifier.AUTONOMOUS_CONTRACTS.items()
        ],
        "bounds": {
            "issue_snapshot_limit": 50,
            "reproduction_candidate_limit": 10,
            "selected_candidate_limit": 1,
        },
        "safety": {
            "issue_list_grants_mutation_authority": False,
            "successor_may_widen_authority": False,
            "unknown_governance_defaults_to_external_draft_only": True,
            "external_merge_authorized": False,
        },
    }


def valid_document():
    return {
        "schema": "ao.architecture.github-issue-workflow-contracts.v0.1",
        "status": "ready",
        "workflow": {
            "name": "github_issue_to_draft_pr",
            "current_public_pair_required": True,
            "single_issue_url_per_run": True,
            "feature_generated_pr_must_be_draft": True,
            "feature_generated_pr_auto_merge_authorized": False,
            "issue_write_authorized": False,
        },
        "schemas": [
            {"name": "issue_url_intake", "owner": "ao-architecture", "consumer": "ao2"},
            {"name": "immutable_issue_snapshot", "owner": "ao-architecture", "consumer": "ao-blueprint"},
            {"name": "repository_identity_target_revision", "owner": "ao-architecture", "consumer": "ao-forge"},
            {"name": "issue_authenticity_assessment", "owner": "ao-blueprint", "consumer": "ao-foundry"},
            {"name": "reproduction_plan_result", "owner": "ao-blueprint", "consumer": "ao2"},
            {"name": "repair_plan_result", "owner": "ao-foundry", "consumer": "ao-forge"},
            {"name": "fork_branch_routing", "owner": "ao-covenant", "consumer": "ao2"},
            {"name": "action_digest_approval", "owner": "ao2", "consumer": "ao-covenant"},
            {"name": "draft_pr_request_readback", "owner": "ao2", "consumer": "ao-command"},
            {"name": "evidence_pack", "owner": "ao2-control-plane", "consumer": "ao-command"},
            {"name": "terminal_state_next_action", "owner": "ao-command", "consumer": "operator"},
        ],
        "canonical_issue_states": [
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
        ],
        "command_policy_classes": [
            "safe_read_only_discovery",
            "repository_native_sandboxed_verification",
            "approval_required_dependency_or_network_operation",
            "approval_required_github_write",
            "permanently_denied_command_or_path",
        ],
        "url_canonicalization": {
            "accepted_pattern": "github.com/<owner>/<repo>/issues/<number>",
            "rejects": [
                "pull_request_url",
                "discussion_url",
                "actions_url",
                "unsupported_host",
                "malformed_number",
                "identity_changing_fragment",
                "traversal",
                "ambiguous_redirect",
            ],
        },
        "trust_model": {
            "untrusted_inputs": [
                "issue_title",
                "issue_body",
                "issue_comments",
                "linked_pages",
                "repository_instructions",
                "workflows",
                "build_scripts",
                "tests",
                "patches",
                "logs",
                "generated_pr_text",
                "git_config",
                "hooks",
                "remotes",
                "submodules",
                "symlinks",
                "archives",
                "dependencies",
                "package_scripts",
                "downloaded_tools",
                "github_api_cli_responses",
            ],
            "issue_text_can_authorize": False,
            "repository_text_can_authorize": False,
            "security_sensitive_stops_public_repair": True,
        },
        "fixtures": [
            {"id": "valid_open_bug", "expected_state": "intake_validated"},
            {"id": "closed_relevant_bug", "expected_state": "intake_validated"},
            {"id": "malformed_url", "expected_state": "invalid_url"},
            {"id": "unsupported_host", "expected_state": "unsupported_host"},
            {"id": "pr_url_supplied_as_issue", "expected_state": "invalid_url"},
            {"id": "nonexistent_issue", "expected_state": "issue_unavailable"},
            {"id": "inaccessible_repository", "expected_state": "repository_unavailable"},
            {"id": "duplicate", "expected_state": "duplicate_or_superseded"},
            {"id": "feature_request", "expected_state": "not_a_bug"},
            {"id": "expected_behavior", "expected_state": "not_a_bug"},
            {"id": "insufficient_evidence", "expected_state": "insufficient_evidence"},
            {"id": "already_fixed_report", "expected_state": "cannot_reproduce"},
            {"id": "security_sensitive_report", "expected_state": "security_sensitive"},
            {"id": "issue_body_prompt_injection", "expected_state": "policy_blocked"},
            {"id": "repository_instruction_prompt_injection", "expected_state": "policy_blocked"},
        ],
        "baseline_metrics": {
            "classification": True,
            "injection_rejection": True,
            "denied_action": True,
            "evidence_integrity": True,
            "elapsed_time": True,
            "retries": True,
            "operator_intervention": True,
        },
        "boundaries": {
            "fork_created": False,
            "branch_pushed": False,
            "draft_pr_opened": False,
            "issue_write_performed": False,
            "maintainer_contacted": False,
            "security_disclosed_publicly": False,
            "release_published": False,
            "rsi_authorized": False,
        },
        "draft_pr_contract_family": {
            "status": "current_pair_only",
            "public_contracts": [
                "ao2.github-draft-pr-evidence.v1",
                "ao2.github-draft-pr-action.v1",
                "ao2.github-draft-pr-verification.v1",
                "ao2.github-draft-pr-fixture-publish.v1",
            ],
            "private_executable_protocol_pattern": "ao2.local-draft-pr-fixture-*",
            "private_protocols_are_public_stack_contracts": False,
            "immutable_commit": "aaa36fb13675396b60ed9a63bd94aa665be9eb5c",
        },
        "autonomous_repair_contract_family": valid_autonomous_family(),
    }


class VerifyGitHubIssueWorkflowContractsTest(unittest.TestCase):
    def test_accepts_valid_contract(self):
        self.assertEqual(verifier.validate_document(valid_document()), [])

    def test_rejects_missing_required_schema(self):
        document = valid_document()
        document["schemas"] = document["schemas"][1:]
        self.assertIn("missing schema: issue_url_intake", verifier.validate_document(document))

    def test_rejects_missing_terminal_state(self):
        document = valid_document()
        document["canonical_issue_states"].remove("security_sensitive")
        self.assertIn("missing canonical issue state: security_sensitive", verifier.validate_document(document))

    def test_rejects_authority_overclaim(self):
        document = valid_document()
        document["trust_model"]["issue_text_can_authorize"] = True
        document["boundaries"]["draft_pr_opened"] = True
        errors = verifier.validate_document(document)
        self.assertIn("issue_text_can_authorize must be false", errors)
        self.assertIn("boundaries.draft_pr_opened must remain false for Month 1", errors)

    def test_rejects_prompt_injection_fixture_that_does_not_fail_closed(self):
        document = valid_document()
        for fixture in document["fixtures"]:
            if fixture["id"] == "issue_body_prompt_injection":
                fixture["expected_state"] = "authentic_bug"
        self.assertIn(
            "fixture issue_body_prompt_injection must fail closed",
            verifier.validate_document(document),
        )

    def test_rejects_missing_command_policy(self):
        document = valid_document()
        document["command_policy_classes"].remove("approval_required_github_write")
        self.assertIn(
            "missing command policy class: approval_required_github_write",
            verifier.validate_document(document),
        )

    def test_rejects_missing_public_draft_pr_contract(self):
        document = valid_document()
        document["draft_pr_contract_family"]["public_contracts"].pop()
        self.assertIn(
            "draft_pr_contract_family.public_contracts must exactly match the four "
            "AO2 public contracts",
            verifier.validate_document(document),
        )

    def test_rejects_private_fixture_protocol_as_public_contract(self):
        document = valid_document()
        document["draft_pr_contract_family"]["public_contracts"][0] = (
            "ao2.local-draft-pr-fixture-request.v1"
        )
        document["draft_pr_contract_family"][
            "private_protocols_are_public_stack_contracts"
        ] = True
        errors = verifier.validate_document(document)
        self.assertIn(
            "draft_pr_contract_family.public_contracts must exactly match the four "
            "AO2 public contracts",
            errors,
        )
        self.assertIn(
            "draft_pr_contract_family.private_protocols_are_public_stack_contracts "
            "must be false",
            errors,
        )

    def test_rejects_wrong_ao2_immutable_commit(self):
        document = valid_document()
        document["draft_pr_contract_family"]["immutable_commit"] = "a" * 40
        self.assertIn(
            "draft_pr_contract_family.immutable_commit must bind the merged AO2 publisher",
            verifier.validate_document(document),
        )

    def test_rejects_missing_autonomous_contract_or_weakened_safety(self):
        document = valid_document()
        document["autonomous_repair_contract_family"]["contracts"].pop()
        document["autonomous_repair_contract_family"]["safety"][
            "successor_may_widen_authority"
        ] = True
        errors = verifier.validate_document(document)
        self.assertTrue(any("missing autonomous repair contract" in error for error in errors))
        self.assertIn(
            "autonomous_repair_contract_family.safety.successor_may_widen_authority "
            "must be false",
            errors,
        )

if __name__ == "__main__":
    unittest.main()
