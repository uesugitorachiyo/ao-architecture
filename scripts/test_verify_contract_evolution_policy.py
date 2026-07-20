import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "verify_contract_evolution_policy.py"
POLICY_PATH = ROOT / "stack" / "contract-evolution-policy.json"
MATRIX_PATH = ROOT / "stack" / "contract-compatibility-matrix.json"


def load_module():
    spec = importlib.util.spec_from_file_location("verify_contract_evolution_policy", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class VerifyContractEvolutionPolicyTest(unittest.TestCase):
    def setUp(self):
        self.module = load_module()
        self.policy = json.loads(POLICY_PATH.read_text())
        self.matrix = json.loads(MATRIX_PATH.read_text())

    def validate(self, policy=None):
        return self.module.validate_policy(
            self.policy if policy is None else policy, self.matrix
        )

    def test_accepts_honest_current_pair_catalog(self):
        self.assertEqual(self.validate(), [])
        self.assertEqual(len(self.policy["edges"]), len(self.matrix["edges"]))
        self.assertEqual(self.policy["coverage"]["two_version_evidence_count"], 0)
        self.assertEqual(len(self.policy["non_edge_change_sets"]), 6)

    def test_binds_month3_non_edge_change_sets_without_changing_edges(self):
        change_sets = {
            record["id"]: record for record in self.policy["non_edge_change_sets"]
        }
        mission = change_sets["mission-lifecycle-correlation-additive-b02666e"]
        self.assertEqual(
            mission["old_commit"],
            "d10bc1986fe1ea5d9ac58454db4fffc08ab76bdd",
        )
        self.assertEqual(
            mission["current_commit"],
            "b02666e7df36ea1d8f325dacedcc22d2a95099e4",
        )
        self.assertEqual(mission["status"], "directional_evidence_incomplete")
        self.assertEqual(
            change_sets["mission-objective-workflow-contract-v0.1-introduction"][
                "predecessor"
            ],
            "not_applicable_no_predecessor",
        )
        ao2 = change_sets["ao2-github-draft-pr-v1-introduction"]
        self.assertEqual(ao2["status"], "current_pair_only")
        self.assertEqual(
            ao2["current_commit"],
            "aaa36fb13675396b60ed9a63bd94aa665be9eb5c",
        )
        self.assertEqual(
            change_sets["mission-correlation-chain-v0.1-introduction"][
                "current_commit"
            ],
            "7e7de94af5f2f463fb18a7d2fdf829e66787167f",
        )
        self.assertEqual(
            change_sets["command-mission-status-correlation-additive-7cda85e"][
                "status"
            ],
            "directional_evidence_incomplete",
        )

    def test_rejects_mutated_month3_commit_or_fictional_predecessor(self):
        policy = copy.deepcopy(self.policy)
        policy["non_edge_change_sets"][0]["current_commit"] = "a" * 40
        policy["non_edge_change_sets"][1]["predecessor"] = "v0"
        errors = self.validate(policy)
        self.assertIn(
            "non_edge_change_sets mission-lifecycle-correlation-additive-b02666e "
            "must match the trusted record",
            errors,
        )
        self.assertIn(
            "non_edge_change_sets mission-objective-workflow-contract-v0.1-introduction "
            "must match the trusted record",
            errors,
        )

    def test_rejects_ao2_commit_or_private_protocol_drift(self):
        policy = copy.deepcopy(self.policy)
        ao2 = policy["non_edge_change_sets"][2]
        ao2["current_commit"] = "b" * 40
        ao2["contracts"][0] = "ao2.local-draft-pr-fixture-request.v1"
        errors = self.validate(policy)
        self.assertIn(
            "non_edge_change_sets ao2-github-draft-pr-v1-introduction "
            "must match the trusted record",
            errors,
        )

    def test_rejects_matrix_identity_and_evidence_drift(self):
        policy = copy.deepcopy(self.policy)
        policy["edges"][0]["consumer"] = "ao-command"
        policy["edges"][1]["canonical_vector"]["merge_commit"] = "c" * 40
        policy["edges"][2]["consumer_test"]["path"] = "invented_test.go"
        errors = self.validate(policy)
        self.assertTrue(any("must exactly match compatibility matrix edges" in error for error in errors))
        self.assertIn(
            "edges[1].canonical_vector.merge_commit must exactly match compatibility matrix",
            errors,
        )
        self.assertIn(
            "edges[2].consumer_test.path must exactly match compatibility matrix", errors
        )

    def test_rejects_valid_looking_vector_metadata_substitution(self):
        policy = copy.deepcopy(self.policy)
        policy["edges"][0]["canonical_vector"]["sha256"] = "f" * 64
        policy["edges"][1]["canonical_vector"][
            "schema_identifier"
        ] = "ao.compatibility.invented-vector.v9"
        policy["edges"][2]["canonical_vector"]["byte_length"] += 1
        errors = self.validate(policy)
        for index in range(3):
            self.assertIn(
                f"edges[{index}] vector and consumer evidence must match the trusted digest",
                errors,
            )

    def test_rejects_consumer_test_selector_digest_or_length_substitution(self):
        policy = copy.deepcopy(self.policy)
        policy["edges"][0]["consumer_test"]["test_selector"] = "TestInvented"
        policy["edges"][1]["consumer_test"]["sha256"] = "e" * 64
        policy["edges"][2]["consumer_test"]["byte_length"] += 1
        errors = self.validate(policy)
        for index in range(3):
            self.assertIn(
                f"edges[{index}] vector and consumer evidence must match the trusted digest",
                errors,
            )

    def test_rejects_fabricated_predecessor_on_unchanged_edge(self):
        policy = copy.deepcopy(self.policy)
        policy["edges"][0]["evolution"]["documented_predecessors"] = ["v0"]
        errors = self.validate(policy)
        self.assertIn(
            "edges[0].evolution must not invent predecessors without a declared change",
            errors,
        )

    def test_rejects_untrusted_declared_change_even_with_well_formed_proofs(self):
        policy = copy.deepcopy(self.policy)
        proof = {
            "evidence_type": "executable_test_at_merge_commit",
            "repository": "ao-consumer",
            "path": "tests/compatibility.json",
            "test_selector": "test_contract_compatibility",
            "merge_commit": "a" * 40,
            "fixture_sha256": "b" * 64,
        }
        evolution = policy["edges"][0]["evolution"]
        evolution.update(
            {
                "declared_change": True,
                "current_version": "v2",
                "documented_predecessors": ["v1"],
                "status": "two_version_evidence_complete",
                "directional_evidence": {
                    direction: copy.deepcopy(proof)
                    for direction in self.module.REQUIRED_DIRECTIONS
                },
            }
        )
        policy["coverage"].update(
            {
                "declared_change_count": 1,
                "two_version_evidence_count": 1,
                "compatibility_activation_complete": True,
            }
        )
        errors = self.validate(policy)
        self.assertIn(
            "edges[0].evolution declared change lacks trusted executable evidence",
            errors,
        )

    def test_rejects_newer_predecessor_and_self_asserted_proof(self):
        policy = copy.deepcopy(self.policy)
        evolution = policy["edges"][0]["evolution"]
        evolution.update(
            {
                "declared_change": True,
                "current_version": "v1",
                "documented_predecessors": ["v2"],
                "status": "two_version_evidence_complete",
                "directional_evidence": {
                    direction: {} for direction in self.module.REQUIRED_DIRECTIONS
                },
            }
        )
        errors = self.validate(policy)
        self.assertIn(
            "edges[0].evolution predecessor must be older than current_version", errors
        )
        self.assertTrue(any("evidence_type" in error for error in errors))

    def test_rejects_unknown_fields_pointer_and_malformed_semantics(self):
        policy = copy.deepcopy(self.policy)
        policy["unexpected"] = True
        policy["compatibility_matrix"] = "other.json"
        policy["evidence_semantics"]["digest_scope"] = "invented but nonempty meaning"
        policy["edges"][0]["canonical_vector"]["unexpected"] = "field"
        errors = self.validate(policy)
        self.assertIn("policy fields must exactly match the strict schema", errors)
        self.assertIn(
            "compatibility_matrix must identify the Architecture matrix", errors
        )
        self.assertIn(
            "evidence_semantics.digest_scope must match the trusted meaning", errors
        )
        self.assertIn(
            "edges[0].canonical_vector fields must exactly match the strict schema",
            errors,
        )

    def test_rejects_false_coverage_or_authority(self):
        policy = copy.deepcopy(self.policy)
        policy["coverage"]["two_version_evidence_count"] = 16
        policy["coverage"]["compatibility_activation_complete"] = True
        policy["safety"]["promotion_granted"] = True
        errors = self.validate(policy)
        self.assertIn("coverage.two_version_evidence_count must equal 0", errors)
        self.assertIn("coverage.compatibility_activation_complete must equal False", errors)
        self.assertIn("safety.promotion_granted must be false", errors)

    def test_ci_enforces_policy_and_unit_tests(self):
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
        commands = (
            "python3 scripts/verify_contract_evolution_policy.py",
            "python3 -m unittest scripts/test_verify_contract_evolution_policy.py",
            "python3 scripts/verify_contract_compatibility_window.py",
            "python3 -m unittest scripts/test_verify_contract_compatibility_window.py",
            "python3 scripts/verify_contract_migration_and_rollback_results.py",
            "python3 -m unittest "
            "scripts/test_verify_contract_migration_and_rollback_results.py",
            "python3 scripts/verify_github_issue_workflow_contracts.py",
            "python3 -m unittest scripts/test_verify_github_issue_workflow_contracts.py",
        )
        for command in commands:
            self.assertIn(command, workflow)


if __name__ == "__main__":
    unittest.main()
