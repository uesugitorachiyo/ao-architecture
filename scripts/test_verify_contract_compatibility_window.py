import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "verify_contract_compatibility_window.py"
WINDOW_PATH = ROOT / "stack" / "contract-compatibility-window.json"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "verify_contract_compatibility_window", MODULE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class VerifyContractCompatibilityWindowTest(unittest.TestCase):
    def setUp(self):
        self.module = load_module()
        self.document = json.loads(WINDOW_PATH.read_text())

    def validate(self, document=None):
        return self.module.validate_document(
            self.document if document is None else document
        )

    def test_accepts_month3_compatibility_window(self):
        self.assertEqual(self.validate(), [])
        self.assertEqual(self.document["minimum_supported_releases"], 2)
        self.assertEqual(len(self.document["change_sets"]), 6)
        for index in (0, 4, 5):
            self.assertEqual(
                self.document["change_sets"][index]["directions"][
                    "new_producer_to_old_consumer"
                ]["status"],
                "not_demonstrated",
            )
        for index in (0, 4):
            self.assertEqual(
                self.document["change_sets"][index]["directions"][
                    "old_producer_to_new_consumer"
                ]["status"],
                "not_demonstrated",
            )

    def test_rejects_missing_additive_direction(self):
        document = copy.deepcopy(self.document)
        del document["change_sets"][0]["directions"][
            "new_producer_to_old_consumer"
        ]
        self.assertIn(
            "mission-lifecycle-correlation-additive-b02666e directions must "
            "exactly match the four required directions",
            self.validate(document),
        )

    def test_rejects_fictional_predecessor_result(self):
        document = copy.deepcopy(self.document)
        document["change_sets"][1]["directions"][
            "old_producer_to_new_consumer"
        ]["status"] = "passed"
        self.assertIn(
            "mission-objective-workflow-contract-v0.1-introduction "
            "old_producer_to_new_consumer must be not_applicable_no_predecessor",
            self.validate(document),
        )

    def test_rejects_failed_ao2_current_pair_after_merge(self):
        document = copy.deepcopy(self.document)
        document["change_sets"][2]["directions"][
            "current_producer_to_current_consumer"
        ]["status"] = "failed"
        self.assertIn(
            "ao2-github-draft-pr-v1-introduction current pair must be passed",
            self.validate(document),
        )

    def test_rejects_incomplete_new_additive_change(self):
        document = copy.deepcopy(self.document)
        document["change_sets"][5]["directions"][
            "rollback_to_previous_supported_contract"
        ]["status"] = "failed"
        self.assertIn(
            "command-mission-status-correlation-additive-7cda85e "
            "rollback_to_previous_supported_contract must be passed",
            self.validate(document),
        )

    def test_rejects_unknown_fields(self):
        document = copy.deepcopy(self.document)
        document["unexpected"] = True
        document["change_sets"][0]["unexpected"] = True
        errors = self.validate(document)
        self.assertIn("document fields must exactly match the strict schema", errors)
        self.assertIn(
            "change_sets[0] fields must exactly match the strict schema", errors
        )

    def test_rejects_semantic_meaning_drift(self):
        document = copy.deepcopy(self.document)
        document["change_sets"][2]["directions"][
            "current_producer_to_current_consumer"
        ]["meaning"] = "tests did not run"
        self.assertIn(
            "ao2-github-draft-pr-v1-introduction must match the trusted "
            "compatibility statement",
            self.validate(document),
        )


if __name__ == "__main__":
    unittest.main()
