import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from verify_operator_workflow import validate_operator_workflow


class VerifyOperatorWorkflowTest(unittest.TestCase):
    def test_accepts_month5_operator_workflow_doc(self):
        doc = (Path(__file__).resolve().parents[1] / "docs" / "operator-workflow.md").read_text()
        self.assertEqual(validate_operator_workflow(doc), [])

    def test_rejects_missing_current_release_pair_and_denied_states(self):
        doc = "# Operator Workflow\n\nCompatibility evidence is present.\n"
        errors = validate_operator_workflow(doc)
        self.assertIn("document must mention AO2 v0.5.1", errors)
        self.assertIn("document must mention AO2 Control Plane v0.1.16", errors)
        self.assertIn("document must state compatibility gate is ready, not active", errors)
        self.assertIn("document must state RSI remains denied", errors)
        self.assertIn("document must state promotion is not requested or granted", errors)

    def test_rejects_missing_operator_steps_and_gates(self):
        doc = "\n".join(
            [
                "AO2 v0.5.1",
                "AO2 Control Plane v0.1.16",
                "compatibility gate remains false",
                "RSI remains denied",
                "promotion is not requested or granted",
                "external beta is not launched",
                "live self-modification is denied",
                "provider pilot did not run",
            ]
        )
        errors = validate_operator_workflow(doc)
        self.assertIn("document must include gate release gate", errors)
        self.assertIn("document must include operator step choose safe next work", errors)
        self.assertIn("document must include support evidence field exact command", errors)

    def test_rejects_stale_false_gate_language(self):
        doc = "\n".join(
            [
                "AO2 v0.5.1",
                "AO2 Control Plane v0.1.16",
                "16 tested compatibility edges",
                "compatibility gate remains false",
                "RSI remains denied",
                "live self-modification is denied",
                "provider pilot did not run",
                "external beta is not launched",
                "promotion is not requested or granted",
                "Month 4 dry-run",
                "release gate",
                "compatibility evidence gate",
                "policy approval gate",
                "dry-run/self-improvement gate",
                "observation/readback gate",
                "promotion/no-RSI gate",
                "read current state",
                "choose safe next work",
                "inspect policy gates",
                "run or read dry-run evidence",
                "inspect rollback and observation",
                "review Sentinel and Promoter boundaries",
                "collect support evidence",
                "AO2 version",
                "platform",
                "exact command",
                "expected result",
                "actual result",
                "evidence path",
                "approval status",
                "manifest or checksum state",
                "rollback status",
                "observation status",
                "sanitized logs",
                "do not paste credentials",
            ]
        )
        errors = validate_operator_workflow(doc)
        self.assertIn("document must state compatibility gate is ready, not active", errors)


if __name__ == "__main__":
    unittest.main()
