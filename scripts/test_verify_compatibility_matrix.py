import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from verify_compatibility_matrix import validate_document


class VerifyCompatibilityMatrixTest(unittest.TestCase):
    def test_accepts_pending_matrix_edge(self):
        document = {
            "schema": "ao.architecture.contract-compatibility-matrix.v0.1",
            "status": "proposed",
            "registry_owner": "ao-covenant",
            "owner_registry": "stack/contract-owner-registry.json",
            "edges": [{
                "producer": "ao-blueprint",
                "consumer": "ao-atlas",
                "contract_family": "requirements_to_workgraph",
                "producer_contract": "blueprint_pack",
                "consumer_contract": "context_pack",
                "compatibility_status": "pending_canonical_vectors",
            }],
            "coverage": {
                "edge_count": 1,
                "uncovered_owner_pairs": 0,
                "compatibility_gate_complete": False,
            },
            "safety": {
                "promotion_granted": False,
                "rsi_remains_denied": True,
                "migration_started": False,
            },
        }
        self.assertEqual(validate_document(document, expected_repositories={"ao-blueprint", "ao-atlas"}), [])

    def test_rejects_activated_edge(self):
        document = {
            "schema": "ao.architecture.contract-compatibility-matrix.v0.1",
            "status": "active",
            "registry_owner": "ao-covenant",
            "owner_registry": "stack/contract-owner-registry.json",
            "edges": [{
                "producer": "ao-blueprint",
                "consumer": "ao-atlas",
                "contract_family": "requirements_to_workgraph",
                "producer_contract": "blueprint_pack",
                "consumer_contract": "context_pack",
                "compatibility_status": "compatible",
            }],
            "coverage": {
                "edge_count": 1,
                "uncovered_owner_pairs": 0,
                "compatibility_gate_complete": True,
            },
            "safety": {
                "promotion_granted": False,
                "rsi_remains_denied": True,
                "migration_started": False,
            },
        }
        errors = validate_document(document, expected_repositories={"ao-blueprint", "ao-atlas"})
        self.assertIn("status must remain proposed until compatibility gates pass", errors)
        self.assertIn("edges[0].compatibility_status must remain pending_canonical_vectors", errors)


if __name__ == "__main__":
    unittest.main()
