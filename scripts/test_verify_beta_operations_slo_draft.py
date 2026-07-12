import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from verify_beta_operations_slo_draft import validate_document


def valid_document():
    return {
        "schema": "ao.architecture.beta-operations-slo-draft.v0.1",
        "status": "draft_planning_only",
        "scope": "ao-stack-month6-beta-operations",
        "source_recommendation_rank": 37,
        "source_recommendation_task": "Create beta operations SLO draft fixture",
        "safety_gate": "planning_only_no_provider_no_release",
        "slos": [
            {
                "id": "mission_restart_recovery",
                "owner_repo": "ao-mission",
                "objective": "Resume an interrupted mission without losing durable checkpoints.",
                "target": "95_percent_resume_without_manual_state_repair",
                "measurement": "replay fixture and mission event index readback",
                "blocks_beta": True,
            },
            {
                "id": "approval_digest_integrity",
                "owner_repo": "ao-covenant",
                "objective": "Bind approval evidence to exact proposed bytes and base commit.",
                "target": "100_percent_gate_critical_approvals_digest_bound",
                "measurement": "contract registry compatibility and approval packet replay",
                "blocks_beta": True,
            },
            {
                "id": "rollback_receipt_latency",
                "owner_repo": "ao2",
                "objective": "Produce rollback receipts for bounded dry-run mutations.",
                "target": "rollback_receipt_under_5_minutes_in_rehearsal",
                "measurement": "rollback receipt replay fixture",
                "blocks_beta": True,
            },
            {
                "id": "evidence_freshness",
                "owner_repo": "ao-sentinel",
                "objective": "Warn when mission evidence is stale before promotion review.",
                "target": "100_percent_stale_evidence_warning_on_expired_inputs",
                "measurement": "Sentinel evidence freshness warning panel",
                "blocks_beta": True,
            },
        ],
        "slo_count": 4,
        "safety": {
            "planning_only": True,
            "provider_calls": False,
            "credential_use": False,
            "release_or_publish": False,
            "promotion_granted": False,
            "direct_main_mutation": False,
            "hidden_instruction_change": False,
            "rsi_remains_denied": True,
        },
    }


class VerifyBetaOperationsSLODraftTest(unittest.TestCase):
    def test_accepts_beta_operations_slo_draft(self):
        self.assertEqual(validate_document(valid_document()), [])

    def test_rejects_missing_blocking_slo(self):
        document = valid_document()
        document["slos"][0]["blocks_beta"] = False
        self.assertIn("slos[0].blocks_beta must be true", validate_document(document))

    def test_rejects_promoting_or_executing_draft(self):
        document = valid_document()
        document["safety"]["provider_calls"] = True
        document["safety"]["promotion_granted"] = True
        errors = validate_document(document)
        self.assertIn("safety.provider_calls must be false", errors)
        self.assertIn("safety.promotion_granted must be false", errors)

    def test_accepts_current_stack_fixture(self):
        document = __import__("json").loads(Path("stack/beta-operations-slo-draft.json").read_text())
        self.assertEqual(validate_document(document), [])


if __name__ == "__main__":
    unittest.main()
