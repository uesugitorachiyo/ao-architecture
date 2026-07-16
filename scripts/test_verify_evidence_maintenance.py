import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from test_verify_evidence_freshness import valid_manifest, valid_matrix, valid_readback
from verify_evidence_maintenance import validate_report


def valid_report():
    return {
        "schema": "ao.architecture.evidence-maintenance-report.v0.1",
        "status": "fresh",
        "generated_at_utc": "2026-07-16T05:49:38Z",
        "source_reports": {
            "current_release_manifest": "stack/current-release-manifest.json",
            "compatibility_matrix": "stack/contract-compatibility-matrix.json",
            "evidence_freshness_readback": "stack/evidence-freshness-readback.json",
            "operator_adoption_drill": "docs/adoption-operator-drill.md",
        },
        "current_public_release_pair": valid_readback()["current_public_release_pair"],
        "compatibility_matrix": valid_readback()["compatibility_matrix"],
        "compatibility_gate": valid_readback()["compatibility_gate"],
        "maintenance_checks": {
            "current_release_metadata_matches_manifest": "fresh",
            "matrix_counts_match_edges": "fresh",
            "tested_edges_have_canonical_vectors": "fresh",
            "tested_edges_have_consumer_tests": "fresh",
            "local_architecture_vectors_exist": "fresh",
            "operator_workflow_readback_available": "fresh",
            "denied_authority_boundaries_present": "fresh",
        },
        "automation_readiness": {
            "repeatable_report": True,
            "detects_stale_public_metadata": True,
            "detects_missing_vector": True,
            "detects_missing_consumer_test": True,
            "detects_count_mismatch": True,
            "detects_gate_activation_overclaim": True,
            "operator_readback_ready": True,
        },
        "boundaries": valid_readback()["boundaries"],
        "next_action": "use AO Atlas to replay the maintenance workgraph and compare this report with current release metadata",
    }


class VerifyEvidenceMaintenanceTest(unittest.TestCase):
    def test_accepts_fresh_maintenance_report(self):
        errors = validate_report(
            valid_report(),
            valid_manifest(),
            valid_matrix(),
            valid_readback(),
            existing_paths={"stack/fixtures/compatibility/architecture-route-context-v0.1.json"},
            existing_docs={"docs/adoption-operator-drill.md"},
        )
        self.assertEqual(errors, [])

    def test_rejects_stale_public_metadata(self):
        report = valid_report()
        report["current_public_release_pair"]["ao2"]["tag_target"] = "0" * 40
        errors = validate_report(
            report,
            valid_manifest(),
            valid_matrix(),
            valid_readback(),
            existing_paths={"stack/fixtures/compatibility/architecture-route-context-v0.1.json"},
            existing_docs={"docs/adoption-operator-drill.md"},
        )
        self.assertIn("ao2.tag_target must match current release manifest", errors)

    def test_rejects_missing_vector_and_consumer_test_references(self):
        matrix = valid_matrix()
        matrix["edges"][0] = copy.deepcopy(matrix["edges"][0])
        matrix["edges"][0].pop("canonical_vector")
        matrix["edges"][1] = copy.deepcopy(matrix["edges"][1])
        matrix["edges"][1].pop("consumer_test")
        errors = validate_report(
            valid_report(),
            valid_manifest(),
            matrix,
            valid_readback(),
            existing_paths={"stack/fixtures/compatibility/architecture-route-context-v0.1.json"},
            existing_docs={"docs/adoption-operator-drill.md"},
        )
        self.assertIn("edges[0] tested edge must reference canonical vector path", errors)
        self.assertIn("edges[1] tested edge must reference consumer test path", errors)

    def test_rejects_count_mismatch(self):
        report = valid_report()
        report["compatibility_matrix"]["tested_edge_count"] = 1
        errors = validate_report(
            report,
            valid_manifest(),
            valid_matrix(),
            valid_readback(),
            existing_paths={"stack/fixtures/compatibility/architecture-route-context-v0.1.json"},
            existing_docs={"docs/adoption-operator-drill.md"},
        )
        self.assertIn("compatibility_matrix.tested_edge_count must be 2", errors)

    def test_rejects_unsupported_gate_activation(self):
        report = valid_report()
        report["compatibility_gate"]["state"] = "active"
        report["compatibility_gate"]["activation_authorized"] = False
        errors = validate_report(
            report,
            valid_manifest(),
            valid_matrix(),
            valid_readback(),
            existing_paths={"stack/fixtures/compatibility/architecture-route-context-v0.1.json"},
            existing_docs={"docs/adoption-operator-drill.md"},
        )
        self.assertIn("compatibility_gate active requires activation_authorized=true", errors)

    def test_rejects_missing_operator_drill_and_boundary_overclaim(self):
        report = valid_report()
        report["boundaries"]["promotion_requested"] = True
        errors = validate_report(
            report,
            valid_manifest(),
            valid_matrix(),
            valid_readback(),
            existing_paths={"stack/fixtures/compatibility/architecture-route-context-v0.1.json"},
            existing_docs=set(),
        )
        self.assertIn("operator adoption drill source is missing", errors)
        self.assertIn("promotion_requested must remain false", errors)


if __name__ == "__main__":
    unittest.main()
