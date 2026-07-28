import copy
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import github_issue_autonomous_contracts as contracts


ROOT = Path(__file__).resolve().parents[1]


class GitHubIssueAutonomousContractsTest(unittest.TestCase):
    def load_vector(self, name):
        vector = contracts.AUTONOMOUS_CONTRACTS[name][2]
        return json.loads((ROOT / vector).read_text())

    def test_requires_all_eight_separately_versioned_strict_schemas(self):
        self.assertEqual(len(contracts.AUTONOMOUS_CONTRACTS), 8)
        for schema_id, schema_path, vector_path in contracts.AUTONOMOUS_CONTRACTS.values():
            schema_file = ROOT / schema_path
            vector_file = ROOT / vector_path
            self.assertTrue(schema_file.is_file(), schema_path)
            self.assertTrue(vector_file.is_file(), vector_path)
            schema = json.loads(schema_file.read_text())
            self.assertEqual(schema["$schema"], contracts.SCHEMA_DIALECT)
            self.assertEqual(schema["$id"], schema_id)
            self.assertFalse(schema["additionalProperties"])

    def test_rejects_unknown_authority_field(self):
        envelope = self.load_vector("immutable_run_envelope")
        envelope["authority_override"] = {"merge": True}
        errors = contracts.validate_contract_instance(
            "immutable_run_envelope", envelope
        )
        self.assertTrue(any("additional property" in error for error in errors), errors)

    def test_rejects_widened_successor_envelope(self):
        previous = self.load_vector("immutable_run_envelope")
        successor = copy.deepcopy(previous)
        successor["run_id"] = "repair-run-successor"
        successor["lineage"] = {
            "kind": "narrower_successor",
            "predecessor_run_id": previous["run_id"],
            "predecessor_digest": previous["canonical_digest"],
        }
        successor["predecessor_digest"] = previous["canonical_digest"]
        successor["budgets"]["publication_count"] += 1
        errors = contracts.validate_successor_envelope(previous, successor)
        self.assertIn(
            "successor budgets.publication_count must not exceed predecessor",
            errors,
        )

    def test_rejects_discovery_bounds_above_fifty_and_ten(self):
        discovery = self.load_vector("bounded_discovery_result")
        discovery["snapshot_limit"] = 51
        discovery["candidate_limit"] = 11
        errors = contracts.validate_contract_instance(
            "bounded_discovery_result", discovery
        )
        self.assertTrue(any("snapshot_limit" in error for error in errors), errors)
        self.assertTrue(any("candidate_limit" in error for error in errors), errors)

    def test_rejects_invalid_reviewer_status(self):
        review = self.load_vector("reviewer_independence")
        review["status"] = "trusted"
        errors = contracts.validate_contract_instance("reviewer_independence", review)
        self.assertTrue(any("status" in error for error in errors), errors)

    def test_rejects_unsafe_external_governance(self):
        governance = self.load_vector("governance_decision")
        governance["merge"]["authorized"] = True
        governance["merge"]["mode"] = "auto_merge"
        errors = contracts.validate_contract_instance(
            "governance_decision", governance
        )
        self.assertIn("external governance must deny merge", errors)

    def test_rejects_stale_or_mismatched_action_digest(self):
        action = self.load_vector("github_action_digest")
        action["head_sha"] = "c" * 40
        errors = contracts.validate_contract_instance(
            "github_action_digest",
            action,
            reference_time=datetime(2026, 7, 28, tzinfo=timezone.utc),
        )
        self.assertIn("github action digest does not match canonical action fields", errors)

        stale = self.load_vector("github_action_digest")
        errors = contracts.validate_contract_instance(
            "github_action_digest",
            stale,
            reference_time=datetime(2026, 7, 30, tzinfo=timezone.utc),
        )
        self.assertIn("github action digest approval is stale", errors)

    def test_rejects_malformed_checkpoint_event_linkage(self):
        event = self.load_vector("append_only_event")
        checkpoint = self.load_vector("checkpoint")
        checkpoint["last_event_digest"] = "f" * 64
        errors = contracts.validate_checkpoint_event_linkage(checkpoint, event)
        self.assertIn("checkpoint last_event_digest must match event digest", errors)

        event["sequence"] += 1
        errors = contracts.validate_checkpoint_event_linkage(
            self.load_vector("checkpoint"), event
        )
        self.assertIn("checkpoint last_event_sequence must match event sequence", errors)


if __name__ == "__main__":
    unittest.main()
