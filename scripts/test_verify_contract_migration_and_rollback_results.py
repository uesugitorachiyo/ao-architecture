import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "verify_contract_migration_and_rollback_results.py"
RESULTS_PATH = ROOT / "stack" / "contract-migration-and-rollback-results.json"
CROSS_VERSION_PATH = ROOT / "stack" / "contract-cross-version-fixture-results.json"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "verify_contract_migration_and_rollback_results", MODULE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class VerifyContractMigrationAndRollbackResultsTest(unittest.TestCase):
    def setUp(self):
        self.module = load_module()
        self.document = json.loads(RESULTS_PATH.read_text())
        self.cross_version = json.loads(CROSS_VERSION_PATH.read_text())

    def validate(self, document=None):
        return self.module.validate_document(
            self.document if document is None else document
        )

    def test_accepts_bound_month3_results(self):
        self.assertEqual(self.validate(), [])
        mission = self.document["results"][0]
        self.assertEqual(mission["failed_direction_count"], 0)
        self.assertEqual(mission["unproven_direction_count"], 0)
        self.assertEqual(len(mission["directional_evidence"]), 4)
        self.assertEqual(
            mission["directional_evidence"]["new_producer_to_old_consumer"][
                "status"
            ],
            "passed",
        )
        self.assertEqual(
            mission["directional_evidence"]["old_producer_to_new_consumer"][
                "status"
            ],
            "passed",
        )

    def test_accepts_bound_cross_version_fixture_results(self):
        self.assertEqual(
            self.module.validate_cross_version_document(self.cross_version),
            [],
        )

    def test_rejects_cross_version_fixture_digest_drift(self):
        document = copy.deepcopy(self.cross_version)
        document["fixtures"][0]["readback_sha256"] = "a" * 64
        self.assertIn(
            "cross-version fixture results must match the trusted digest",
            self.module.validate_cross_version_document(document),
        )

    def test_rejects_altered_external_source_digest(self):
        document = copy.deepcopy(self.document)
        document["results"][0]["directional_evidence"][
            "old_producer_to_new_consumer"
        ]["source_sha256"] = "a" * 64
        self.assertIn(
            "mission-lifecycle-correlation-additive-b02666e evidence must match "
            "trusted immutable bindings",
            self.validate(document),
        )

    def test_rejects_wrong_mission_commit(self):
        document = copy.deepcopy(self.document)
        document["results"][0]["current_commit"] = "b" * 40
        self.assertIn(
            "mission-lifecycle-correlation-additive-b02666e evidence must match "
            "trusted immutable bindings",
            self.validate(document),
        )

    def test_rejects_claimed_predecessor_for_new_contract(self):
        document = copy.deepcopy(self.document)
        document["results"][1]["predecessor_results"][
            "old_producer_to_new_consumer"
        ] = "passed"
        self.assertIn(
            "mission-objective-workflow-contract-v0.1-introduction must not "
            "invent predecessor results",
            self.validate(document),
        )

    def test_rejects_ao2_immutable_commit_drift(self):
        document = copy.deepcopy(self.document)
        document["results"][2]["current_commit"] = "a" * 40
        self.assertIn(
            "ao2-github-draft-pr-v1-introduction must bind the merged passing current pair",
            self.validate(document),
        )

    def test_rejects_missing_mission_chain_provenance(self):
        document = copy.deepcopy(self.document)
        document["results"][3]["current_pair_evidence"]["test_sha256"] = "a" * 64
        self.assertIn(
            "mission-correlation-chain-v0.1-introduction evidence must match "
            "trusted immutable bindings",
            self.validate(document),
        )

    def test_rejects_failed_command_rollback_direction(self):
        document = copy.deepcopy(self.document)
        document["results"][5]["directional_evidence"][
            "rollback_to_previous_supported_contract"
        ]["status"] = "failed"
        errors = self.validate(document)
        self.assertIn(
            "command-mission-status-correlation-additive-7cda85e "
            "rollback_to_previous_supported_contract evidence must match its "
            "honest immutable status",
            errors,
        )

    def test_rejects_unknown_fields(self):
        document = copy.deepcopy(self.document)
        document["results"][0]["directional_evidence"][
            "rollback_to_previous_supported_contract"
        ]["unexpected"] = True
        self.assertIn(
            "rollback_to_previous_supported_contract evidence fields must exactly "
            "match the strict schema",
            self.validate(document),
        )


if __name__ == "__main__":
    unittest.main()
