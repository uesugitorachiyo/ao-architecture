import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VECTOR = ROOT / "stack" / "fixtures" / "bounded-autonomy" / "benchmark-to-command-readback-v0.1.json"


class BoundedAutonomyCommandVectorTest(unittest.TestCase):
    def test_vector_proves_benchmark_contract_for_command_readback(self):
        with VECTOR.open(encoding="utf-8") as handle:
            vector = json.load(handle)

        self.assertEqual(vector["schema"], "ao.architecture.bounded-autonomy-command-readback-vector.v0.1")
        self.assertEqual(vector["edge"], "ao-architecture.bounded_autonomy_benchmark -> ao-command.operator_workflow_readback")
        self.assertEqual(vector["producer"]["repository"], "ao-architecture")
        self.assertEqual(vector["consumer"]["repository"], "ao-command")

        baseline = vector["source_baseline"]
        self.assertEqual(baseline["benchmark_version"], "bounded-autonomy-month1-v0.1")
        self.assertEqual(baseline["status"], "baseline_recorded")
        self.assertEqual(baseline["task_classes"], 7)
        self.assertEqual(baseline["metrics"]["unsupported_claim_count"], 0)

        readback = vector["expected_command_readback"]
        self.assertEqual(readback["schema"], "ao.command.operator-workflow-readback.v0.1")
        self.assertEqual(readback["benchmark_version"], "bounded-autonomy-month1-v0.1")
        self.assertEqual(readback["benchmark_status"], "baseline_recorded")
        self.assertEqual(readback["benchmark_task_classes"], 7)
        self.assertEqual(readback["unsupported_claim_count"], 0)
        self.assertEqual(readback["compatibility_gate_state"], "ready")
        self.assertFalse(readback["compatibility_gate_activation_authorized"])

        boundaries = vector["boundaries"]
        for key in [
            "release_or_upload",
            "provider_pilot",
            "external_beta_launched",
            "promotion_requested",
            "promotion_granted",
            "live_self_modification",
        ]:
            self.assertFalse(boundaries[key], key)
        self.assertTrue(boundaries["rsi_remains_denied"])


if __name__ == "__main__":
    unittest.main()
