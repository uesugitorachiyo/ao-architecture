import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from verify_topology import validate_document


class VerifyTopologyTest(unittest.TestCase):
    def test_rejects_duplicate_authority_domain_owners(self):
        document = {
            "schema": "ao.architecture.authority-inventory.v0.1",
            "status": "current",
            "repositories": [{
                "repository": "ao-mission",
                "current_boundary": "independent_repository",
                "proposed_boundary": "ao-control",
                "primary_authority": "mission_state",
                "non_authority": ["execution", "approval"],
                "migration_status": "not_started",
            }],
            "authority_domains": [
                {"domain": "mission_state", "owner": "ao-mission"},
                {"domain": "requirements", "owner": "ao-mission"},
            ],
            "safety": {
                "promotion_granted": False,
                "rsi_remains_denied": True,
                "migration_started": False,
            },
        }
        errors = validate_document(document, expected_repositories={"ao-mission"})
        self.assertIn("authority domain owner ao-mission is duplicated", errors)

    def test_accepts_current_inventory_with_proposed_boundaries(self):
        document = {
            "schema": "ao.architecture.authority-inventory.v0.1",
            "status": "current",
            "repositories": [{
                "repository": "ao-mission",
                "current_boundary": "independent_repository",
                "proposed_boundary": "ao-control",
                "primary_authority": "mission_state",
                "non_authority": ["execution", "approval"],
                "migration_status": "not_started",
            }],
            "authority_domains": [
                {"domain": "mission_state", "owner": "ao-mission"},
            ],
            "safety": {
                "promotion_granted": False,
                "rsi_remains_denied": True,
                "migration_started": False,
            },
        }
        self.assertEqual(validate_document(document, expected_repositories={"ao-mission"}), [])


if __name__ == "__main__":
    unittest.main()
