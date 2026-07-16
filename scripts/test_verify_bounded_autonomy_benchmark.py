import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from verify_bounded_autonomy_benchmark import validate_command_vector, validate_corpus, validate_results, validate_schema


def valid_corpus():
    return {
        "schema": "ao.architecture.bounded-autonomy-benchmark-corpus.v0.1",
        "benchmark_version": "bounded-autonomy-month1-v0.1",
        "current_public_pair": {
            "ao2_version": "v0.5.1",
            "ao2_tag_target": "80ec5321f42d4bab17d5e64fdae6aa099ba59d4a",
            "control_plane_version": "v0.1.16",
            "control_plane_tag_target": "f4f5fea9fefa1081cebcbabac550b0e08b9f0e3d",
        },
        "task_classes": [
            {"id": "documentation_correction", "fixture": "docs/support correction", "requires_pr": True},
            {"id": "single_repo_code_fix", "fixture": "deterministic code fix", "requires_pr": True},
            {"id": "cross_repo_contract_update", "fixture": "producer/consumer vector", "requires_pr": True},
            {"id": "approval_required_mutation", "fixture": "approval digest", "requires_pr": False},
            {"id": "rollback_required_mutation", "fixture": "rollback evidence", "requires_pr": False},
            {"id": "failed_ci_diagnosis_repair", "fixture": "failed CI repair", "requires_pr": False},
            {"id": "interrupted_mission_resume", "fixture": "checkpoint resume", "requires_pr": False},
        ],
        "failure_classes": [
            "product",
            "workflow",
            "environment",
            "policy",
            "provider",
            "operator",
            "evidence_integrity",
        ],
        "boundaries": {
            "rsi_remains_denied": True,
            "provider_pilot": False,
            "external_beta_launched": False,
            "promotion_requested": False,
            "release_or_upload": False,
        },
    }


def valid_schema():
    return {
        "schema": "ao.architecture.bounded-autonomy-benchmark-result-schema.v0.1",
        "benchmark_version": "bounded-autonomy-month1-v0.1",
        "required_metrics": [
            "completion_rate",
            "first_pass_verification_rate",
            "recovery_rate",
            "human_approvals",
            "human_interventions",
            "duplicate_work_count",
            "orphan_branch_count",
            "ready_node_count",
            "elapsed_seconds",
            "retry_count",
            "rollback_result",
            "evidence_integrity_result",
            "escaped_defect_count",
            "unsupported_claim_count",
        ],
        "required_failure_classes": valid_corpus()["failure_classes"],
    }


def valid_results():
    return {
        "schema": "ao.architecture.bounded-autonomy-baseline-results.v0.1",
        "benchmark_version": "bounded-autonomy-month1-v0.1",
        "status": "baseline_recorded",
        "metrics": {
            "completion_rate": 1.0,
            "first_pass_verification_rate": 1.0,
            "recovery_rate": 1.0,
            "human_approvals": 0,
            "human_interventions": 0,
            "duplicate_work_count": 0,
            "orphan_branch_count": 0,
            "ready_node_count": 0,
            "elapsed_seconds": 0,
            "retry_count": 1,
            "rollback_result": "passed",
            "evidence_integrity_result": "passed",
            "escaped_defect_count": 0,
            "unsupported_claim_count": 0,
        },
        "failure_classification": {
            "product": 0,
            "workflow": 0,
            "environment": 0,
            "policy": 0,
            "provider": 0,
            "operator": 0,
            "evidence_integrity": 0,
        },
        "boundaries": valid_corpus()["boundaries"],
    }


def valid_command_vector():
    return {
        "schema": "ao.architecture.bounded-autonomy-command-readback-vector.v0.1",
        "edge": "ao-architecture.bounded_autonomy_benchmark -> ao-command.operator_workflow_readback",
        "producer": {"repository": "ao-architecture"},
        "consumer": {"repository": "ao-command", "expected_test": "TestConsumesBoundedAutonomyBenchmarkCommandVector"},
        "source_baseline": {
            "benchmark_version": "bounded-autonomy-month1-v0.1",
            "status": "baseline_recorded",
            "task_classes": 7,
            "metrics": {
                "completion_rate": 1.0,
                "first_pass_verification_rate": 0.93,
                "recovery_rate": 1.0,
                "rollback_result": "passed",
                "unsupported_claim_count": 0,
            },
        },
        "expected_command_readback": {
            "schema": "ao.command.operator-workflow-readback.v0.1",
            "benchmark_version": "bounded-autonomy-month1-v0.1",
            "benchmark_status": "baseline_recorded",
            "benchmark_task_classes": 7,
            "completion_rate": 1.0,
            "first_pass_verification_rate": 0.93,
            "recovery_rate": 1.0,
            "rollback_result": "passed",
            "unsupported_claim_count": 0,
            "compatibility_gate_state": "ready",
            "compatibility_gate_activation_authorized": False,
            "operator_mode": "read_only",
            "safe_to_execute": False,
            "executes_work": False,
            "approves_work": False,
            "mutates_repositories": False,
            "calls_providers": False,
            "releases_or_deploys": False,
        },
        "boundaries": {
            "rsi_remains_denied": True,
            "provider_pilot": False,
            "external_beta_launched": False,
            "promotion_requested": False,
            "promotion_granted": False,
            "release_or_upload": False,
            "live_self_modification": False,
        },
    }


class VerifyBoundedAutonomyBenchmarkTest(unittest.TestCase):
    def test_accepts_complete_corpus_schema_and_results(self):
        self.assertEqual(validate_corpus(valid_corpus()), [])
        self.assertEqual(validate_schema(valid_schema()), [])
        self.assertEqual(validate_results(valid_results(), valid_schema()), [])

    def test_rejects_missing_required_task_class(self):
        corpus = valid_corpus()
        corpus["task_classes"] = corpus["task_classes"][:-1]
        errors = validate_corpus(corpus)
        self.assertIn("task_classes must include interrupted_mission_resume", errors)

    def test_rejects_missing_required_metric(self):
        schema = valid_schema()
        schema["required_metrics"].remove("unsupported_claim_count")
        errors = validate_schema(schema)
        self.assertIn("required_metrics must include unsupported_claim_count", errors)

    def test_rejects_result_without_required_metric_or_failure_class(self):
        results = valid_results()
        results["metrics"].pop("rollback_result")
        results["failure_classification"].pop("provider")
        errors = validate_results(results, valid_schema())
        self.assertIn("metrics.rollback_result is required", errors)
        self.assertIn("failure_classification.provider is required", errors)

    def test_rejects_authority_boundary_overclaim(self):
        corpus = valid_corpus()
        corpus["boundaries"] = copy.deepcopy(corpus["boundaries"])
        corpus["boundaries"]["rsi_remains_denied"] = False
        errors = validate_corpus(corpus)
        self.assertIn("boundaries.rsi_remains_denied must remain true", errors)

    def test_accepts_command_readback_vector(self):
        self.assertEqual(validate_command_vector(valid_command_vector()), [])

    def test_rejects_command_vector_without_expected_consumer_test(self):
        vector = valid_command_vector()
        vector["consumer"].pop("expected_test")
        errors = validate_command_vector(vector)
        self.assertIn("consumer.expected_test must be TestConsumesBoundedAutonomyBenchmarkCommandVector", errors)


if __name__ == "__main__":
    unittest.main()
