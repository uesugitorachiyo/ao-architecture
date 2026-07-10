import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from verify_contract_inventory import validate_document


class VerifyContractInventoryTest(unittest.TestCase):
    def test_accepts_pending_owner_baseline(self):
        document = {
            "schema": "ao.architecture.contract-inventory.v0.1",
            "status": "baseline",
            "snapshot_source": "checked_out_repositories",
            "repositories": [{
                "repository": "ao-mission",
                "snapshot_commit": "a" * 40,
                "branch": "main",
                "schema_document_count": 1,
                "schema_version_literal_count": 2,
                "distinct_schema_version_count": 1,
                "contract_owner_status": "pending_owner_assignment",
                "proposed_registry_owner": "ao-covenant",
            }],
            "totals": {
                "schema_document_count": 1,
                "schema_version_literal_count": 2,
                "distinct_schema_version_count": 1,
            },
            "safety": {
                "promotion_granted": False,
                "rsi_remains_denied": True,
                "migration_started": False,
            },
        }
        self.assertEqual(validate_document(document, expected_repositories={"ao-mission"}), [])

    def test_rejects_missing_commit_and_owner_state(self):
        document = {
            "schema": "ao.architecture.contract-inventory.v0.1",
            "status": "baseline",
            "snapshot_source": "checked_out_repositories",
            "repositories": [{
                "repository": "ao-mission",
                "snapshot_commit": "unknown",
                "branch": "main",
                "schema_document_count": 0,
                "schema_version_literal_count": 0,
                "distinct_schema_version_count": 0,
                "contract_owner_status": "assigned",
                "proposed_registry_owner": "ao-covenant",
            }],
            "totals": {
                "schema_document_count": 0,
                "schema_version_literal_count": 0,
                "distinct_schema_version_count": 0,
            },
            "safety": {
                "promotion_granted": False,
                "rsi_remains_denied": True,
                "migration_started": False,
            },
        }
        errors = validate_document(document, expected_repositories={"ao-mission"})
        self.assertIn("repositories[0].snapshot_commit must be a 40-character commit", errors)
        self.assertIn("repositories[0].contract_owner_status must remain pending_owner_assignment", errors)


if __name__ == "__main__":
    unittest.main()
