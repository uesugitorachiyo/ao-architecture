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
        self.assertIn("document must mention AO2 Control Plane v0.1.15", errors)
        self.assertIn("document must state RSI remains denied", errors)
        self.assertIn("document must state promotion is not requested or granted", errors)

    def test_rejects_missing_operator_steps_and_gates(self):
        doc = "\n".join(
            [
                "AO2 v0.5.1",
                "AO2 Control Plane v0.1.15",
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


if __name__ == "__main__":
    unittest.main()
