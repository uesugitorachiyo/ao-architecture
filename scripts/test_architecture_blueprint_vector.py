import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VECTOR = ROOT / "stack" / "fixtures" / "compatibility" / "architecture-source-truth-to-blueprint-authorization-scope-v0.1.json"


class ArchitectureBlueprintVectorTest(unittest.TestCase):
    def test_vector_proves_architecture_source_truth_for_blueprint_authorization_scope(self):
        with VECTOR.open() as handle:
            vector = json.load(handle)

        self.assertEqual(
            vector["schema_version"],
            "ao.compatibility.architecture-source-truth-to-blueprint-authorization-scope-vector.v1",
        )
        self.assertEqual(vector["edge"], "ao-architecture.source_of_truth -> ao-blueprint.authorization_scope")
        self.assertEqual(vector["producer"]["repository"], "ao-architecture")
        self.assertEqual(vector["consumer"]["repository"], "ao-blueprint")

        source = vector["source_of_truth"]
        self.assertEqual(source["ao2_version"], "v0.5.1")
        self.assertEqual(source["control_plane_version"], "v0.1.15")
        self.assertEqual(source["canonical_vector_count"], 15)
        self.assertEqual(source["consumer_test_count"], 15)
        self.assertFalse(source["full_stack_compatibility_complete"])
        self.assertFalse(source["external_beta_launched"])
        self.assertFalse(source["promotion_requested"])
        self.assertFalse(source["promotion_granted"])
        self.assertTrue(source["rsi_remains_denied"])

        scope = vector["authorization_scope"]
        self.assertEqual(scope["schema_version"], "ao.blueprint.authorization-scope.v1")
        self.assertEqual(scope["status"], "ready")
        self.assertEqual(scope["scope_boundary"], "compatibility_evidence_only")
        self.assertEqual(scope["next_allowed_action"], "ao-atlas-workgraph-readback")

        expected = vector["expected_blueprint_authorization_scope"]
        self.assertEqual(expected["schema_version"], "ao.blueprint.authorization-scope-readback.v1")
        self.assertEqual(expected["status"], "ready")
        self.assertFalse(expected["full_stack_compatibility_complete"])

        boundaries = vector["boundaries"]
        for forbidden in [
            "release_or_publish",
            "creates_tag",
            "uploads_assets",
            "deploys",
            "contacts_external_users",
            "provider_pilot",
            "promotion_requested",
            "promotion_granted",
            "executes_work",
            "approves_work",
            "mutates_repositories",
        ]:
            self.assertFalse(boundaries[forbidden], forbidden)
        self.assertTrue(boundaries["rsi_remains_denied"])


if __name__ == "__main__":
    unittest.main()
