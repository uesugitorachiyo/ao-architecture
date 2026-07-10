import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from verify_contract_owner_registry import validate_document


class VerifyContractOwnerRegistryTest(unittest.TestCase):
    def test_accepts_recorded_pending_compatibility_gate(self):
        document = {
            "schema": "ao.architecture.contract-owner-registry.v0.1",
            "status": "proposed",
            "registry_authority": "ao-covenant",
            "inventory_snapshot": "stack/contract-inventory.json",
            "assignments": [{
                "repository": "ao-mission",
                "contract_domain": "mission_lifecycle",
                "owner": "ao-mission",
                "consumer_boundary": "ao-control",
                "assignment_status": "recorded_pending_compatibility_gate",
            }],
            "coverage": {
                "repository_count": 1,
                "unclassified_repository_count": 0,
                "unclassified_schema_document_count": 0,
            },
            "safety": {
                "promotion_granted": False,
                "rsi_remains_denied": True,
                "migration_started": False,
            },
        }
        self.assertEqual(validate_document(document, expected_repositories={"ao-mission"}), [])

    def test_rejects_duplicate_repository_and_active_status(self):
        document = {
            "schema": "ao.architecture.contract-owner-registry.v0.1",
            "status": "active",
            "registry_authority": "ao-covenant",
            "inventory_snapshot": "stack/contract-inventory.json",
            "assignments": [
                {
                    "repository": "ao-mission",
                    "contract_domain": "mission_lifecycle",
                    "owner": "ao-mission",
                    "consumer_boundary": "ao-control",
                    "assignment_status": "recorded_pending_compatibility_gate",
                },
                {
                    "repository": "ao-mission",
                    "contract_domain": "requirements",
                    "owner": "ao-blueprint",
                    "consumer_boundary": "ao-control",
                    "assignment_status": "recorded_pending_compatibility_gate",
                },
            ],
            "coverage": {
                "repository_count": 2,
                "unclassified_repository_count": 0,
                "unclassified_schema_document_count": 0,
            },
            "safety": {
                "promotion_granted": False,
                "rsi_remains_denied": True,
                "migration_started": False,
            },
        }
        errors = validate_document(document, expected_repositories={"ao-mission"})
        self.assertIn("status must remain proposed until compatibility gates pass", errors)
        self.assertIn("assignments must not contain duplicate repositories", errors)


if __name__ == "__main__":
    unittest.main()
