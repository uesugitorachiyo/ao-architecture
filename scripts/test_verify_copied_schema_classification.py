import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from verify_copied_schema_classification import validate_document


class VerifyCopiedSchemaClassificationTest(unittest.TestCase):
    def test_accepts_fully_classified_schema_counts(self):
        document = {
            "schema": "ao.architecture.copied-schema-classification.v0.1",
            "status": "classified_pending_covenant_registry",
            "registry_authority": "ao-covenant",
            "inventory_snapshot": "stack/contract-inventory.json",
            "classification_policy": {
                "allowed_classes": ["stable", "experimental", "deprecated"],
                "stable_rule": "canonical ao-covenant public schema authority",
                "experimental_rule": "repo-local copied schema pending covenant compatibility gate",
                "deprecated_rule": "retired copied schema retained only for compatibility readback",
            },
            "repositories": [
                {
                    "repository": "ao-covenant",
                    "schema_document_count_from_inventory": 2,
                    "stable_schema_document_count": 2,
                    "experimental_schema_document_count": 0,
                    "deprecated_schema_document_count": 0,
                    "classification_status": "stable_registry_authority",
                    "owner": "ao-covenant",
                },
                {
                    "repository": "ao-mission",
                    "schema_document_count_from_inventory": 3,
                    "stable_schema_document_count": 0,
                    "experimental_schema_document_count": 3,
                    "deprecated_schema_document_count": 0,
                    "classification_status": "experimental_pending_covenant_registry",
                    "owner": "ao-mission",
                },
            ],
            "totals": {
                "schema_document_count_from_inventory": 5,
                "stable_schema_document_count": 2,
                "experimental_schema_document_count": 3,
                "deprecated_schema_document_count": 0,
                "unclassified_schema_document_count": 0,
            },
            "safety": {
                "promotion_granted": False,
                "rsi_remains_denied": True,
                "migration_started": False,
            },
        }
        self.assertEqual(validate_document(document, expected_repositories={"ao-covenant", "ao-mission"}), [])

    def test_rejects_unclassified_schema_count(self):
        document = {
            "schema": "ao.architecture.copied-schema-classification.v0.1",
            "status": "classified_pending_covenant_registry",
            "registry_authority": "ao-covenant",
            "inventory_snapshot": "stack/contract-inventory.json",
            "classification_policy": {
                "allowed_classes": ["stable", "experimental", "deprecated"],
                "stable_rule": "canonical ao-covenant public schema authority",
                "experimental_rule": "repo-local copied schema pending covenant compatibility gate",
                "deprecated_rule": "retired copied schema retained only for compatibility readback",
            },
            "repositories": [{
                "repository": "ao-mission",
                "schema_document_count_from_inventory": 3,
                "stable_schema_document_count": 1,
                "experimental_schema_document_count": 1,
                "deprecated_schema_document_count": 0,
                "classification_status": "experimental_pending_covenant_registry",
                "owner": "ao-mission",
            }],
            "totals": {
                "schema_document_count_from_inventory": 3,
                "stable_schema_document_count": 1,
                "experimental_schema_document_count": 1,
                "deprecated_schema_document_count": 0,
                "unclassified_schema_document_count": 1,
            },
            "safety": {
                "promotion_granted": False,
                "rsi_remains_denied": True,
                "migration_started": False,
            },
        }
        errors = validate_document(document, expected_repositories={"ao-mission"})
        self.assertIn("repositories[0] classified counts must equal schema_document_count_from_inventory", errors)
        self.assertIn("totals.unclassified_schema_document_count must be zero", errors)


if __name__ == "__main__":
    unittest.main()
