import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from verify_controlled_self_improvement import validate_manifest


class VerifyControlledSelfImprovementTest(unittest.TestCase):
    def test_accepts_dry_run_only_manifest(self):
        manifest = json.loads(
            (Path(__file__).resolve().parents[1] / "stack" / "controlled-self-improvement-dry-run.json").read_text()
        )
        self.assertEqual(validate_manifest(manifest), [])

    def test_rejects_rsi_or_live_self_modification_authority(self):
        manifest = {
            "schema": "ao.architecture.controlled-self-improvement-dry-run.v0.1",
            "status": "dry_run_only",
            "rsi_authorized": True,
            "live_self_modification_authorized": True,
            "provider_execution_authorized": True,
            "promotion_requested": True,
            "external_beta_launched": True,
            "required_gates": [],
            "evidence_requirements": {},
        }
        errors = validate_manifest(manifest)
        self.assertIn("rsi_authorized must be false", errors)
        self.assertIn("live_self_modification_authorized must be false", errors)
        self.assertIn("provider_execution_authorized must be false", errors)
        self.assertIn("promotion_requested must be false", errors)
        self.assertIn("external_beta_launched must be false", errors)

    def test_rejects_missing_required_gates(self):
        manifest = {
            "schema": "ao.architecture.controlled-self-improvement-dry-run.v0.1",
            "status": "dry_run_only",
            "rsi_authorized": False,
            "live_self_modification_authorized": False,
            "provider_execution_authorized": False,
            "promotion_requested": False,
            "promotion_granted": False,
            "external_beta_launched": False,
            "required_gates": ["proposal"],
            "evidence_requirements": {
                "proposal": True,
            },
        }
        errors = validate_manifest(manifest)
        self.assertIn("required_gates must include policy_classification", errors)
        self.assertIn("required_gates must include human_approval", errors)
        self.assertIn("required_gates must include rollback_proof", errors)
        self.assertIn("evidence_requirements.rollback_proof must be true", errors)


if __name__ == "__main__":
    unittest.main()
