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
                "canonical_vector_count": 0,
                "consumer_test_count": 0,
            },
            "safety": {
                "promotion_granted": False,
                "rsi_remains_denied": True,
                "migration_started": False,
            },
        }
        self.assertEqual(validate_document(document, expected_repositories={"ao-blueprint", "ao-atlas"}), [])

    def test_accepts_tested_edge_with_vector_and_consumer_test_evidence(self):
        document = {
            "schema": "ao.architecture.contract-compatibility-matrix.v0.1",
            "status": "proposed",
            "registry_owner": "ao-covenant",
            "owner_registry": "stack/contract-owner-registry.json",
            "edges": [{
                "producer": "ao2",
                "consumer": "ao2-control-plane",
                "contract_family": "execution_to_observation",
                "producer_contract": "execution_receipt",
                "consumer_contract": "evidence_event",
                "compatibility_status": "tested_current_release_pair",
                "canonical_vector": {
                    "repository": "ao2",
                    "path": "tests/fixtures/compatibility/ao2-execution-receipt-v0.5.1.json",
                    "pr": "https://github.com/uesugitorachiyo/ao2/pull/288",
                    "merge_commit": "5b568830360baac6198a653737f60abab393eec7",
                },
                "consumer_test": {
                    "repository": "ao2-control-plane",
                    "path": "crates/ao2-cp-server/tests/compatibility_vectors.rs",
                    "pr": "https://github.com/uesugitorachiyo/ao2-control-plane/pull/100",
                    "merge_commit": "3e57d80c6be05490930294a7d3ab4664d2856b55",
                },
            }],
            "coverage": {
                "edge_count": 1,
                "uncovered_owner_pairs": 0,
                "compatibility_gate_complete": False,
                "canonical_vector_count": 1,
                "consumer_test_count": 1,
            },
            "safety": {
                "promotion_granted": False,
                "rsi_remains_denied": True,
                "migration_started": False,
            },
        }
        self.assertEqual(validate_document(document, expected_repositories={"ao2", "ao2-control-plane"}), [])

    def test_rejects_tested_edge_without_evidence(self):
        document = {
            "schema": "ao.architecture.contract-compatibility-matrix.v0.1",
            "status": "proposed",
            "registry_owner": "ao-covenant",
            "owner_registry": "stack/contract-owner-registry.json",
            "edges": [{
                "producer": "ao2",
                "consumer": "ao2-control-plane",
                "contract_family": "execution_to_observation",
                "producer_contract": "execution_receipt",
                "consumer_contract": "evidence_event",
                "compatibility_status": "tested_current_release_pair",
            }],
            "coverage": {
                "edge_count": 1,
                "uncovered_owner_pairs": 0,
                "compatibility_gate_complete": False,
                "canonical_vector_count": 1,
                "consumer_test_count": 1,
            },
            "safety": {
                "promotion_granted": False,
                "rsi_remains_denied": True,
                "migration_started": False,
            },
        }
        errors = validate_document(document, expected_repositories={"ao2", "ao2-control-plane"})
        self.assertIn("edges[0].canonical_vector is required for tested edges", errors)
        self.assertIn("edges[0].consumer_test is required for tested edges", errors)

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
                "canonical_vector_count": 0,
                "consumer_test_count": 0,
            },
            "safety": {
                "promotion_granted": False,
                "rsi_remains_denied": True,
                "migration_started": False,
            },
        }
        errors = validate_document(document, expected_repositories={"ao-blueprint", "ao-atlas"})
        self.assertIn("status must remain proposed until compatibility gates pass", errors)
        self.assertIn(
            "edges[0].compatibility_status must be pending_canonical_vectors or tested_current_release_pair",
            errors,
        )


if __name__ == "__main__":
    unittest.main()
