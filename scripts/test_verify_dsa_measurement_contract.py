import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "stack" / "dsa-measurement-contract.json"
sys.path.insert(0, str(ROOT / "scripts"))


class VerifyDsaMeasurementContractTest(unittest.TestCase):
    def test_contract_records_required_measurement_semantics(self):
        self.assertTrue(CONTRACT.exists(), "stack/dsa-measurement-contract.json is required")
        contract = json.loads(CONTRACT.read_text())

        self.assertEqual(contract["schema"], "ao.architecture.dsa-measurement-contract.v0.1")
        self.assertEqual(contract["status_values"], ["pass", "regression", "inconclusive"])
        self.assertEqual(contract["standard_input_sizes"], [100, 1000, 10000])

        required_dimensions = {
            "correctness_invariant",
            "input_size_dimension",
            "expected_complexity_class",
            "operation_or_file_read_count_evidence",
            "allocation_evidence",
            "repeated_wall_clock_benchmark_evidence",
            "deterministic_output_requirement",
            "compatibility_requirement",
        }
        self.assertEqual(set(contract["required_measurement_fields"]), required_dimensions)

        release_qualification = contract["release_qualification_measurement"]
        self.assertTrue(release_qualification["records_cumulative_compute_time"])
        self.assertTrue(release_qualification["records_operator_wall_time"])
        self.assertTrue(release_qualification["records_external_wait_separately"])
        self.assertTrue(release_qualification["requires_digest_bound_reuse"])
        self.assertFalse(release_qualification["allows_coverage_reduction_for_speed"])

        claim_rules = contract["complexity_claim_rules"]
        self.assertTrue(claim_rules["requires_implementation_argument"])
        self.assertTrue(claim_rules["requires_scale_evidence"])
        self.assertTrue(claim_rules["prefers_operation_counts_over_single_timing"])

    def test_validator_rejects_missing_required_semantics(self):
        from verify_dsa_measurement_contract import validate_document

        errors = validate_document({
            "schema": "ao.architecture.dsa-measurement-contract.v0.1",
            "standard_input_sizes": [100, 1000],
            "status_values": ["pass", "regression"],
            "required_measurement_fields": ["correctness_invariant"],
            "complexity_claim_rules": {
                "requires_implementation_argument": False,
                "requires_scale_evidence": True,
                "prefers_operation_counts_over_single_timing": True,
            },
            "release_qualification_measurement": {
                "records_cumulative_compute_time": True,
                "records_operator_wall_time": True,
                "records_external_wait_separately": False,
                "requires_digest_bound_reuse": True,
                "allows_coverage_reduction_for_speed": True,
            },
        })

        self.assertIn("standard_input_sizes must be [100, 1000, 10000]", errors)
        self.assertIn("status_values must be ['pass', 'regression', 'inconclusive']", errors)
        self.assertIn("required_measurement_fields missing allocation_evidence", errors)
        self.assertIn("complexity_claim_rules.requires_implementation_argument must be true", errors)
        self.assertIn("release_qualification_measurement.records_external_wait_separately must be true", errors)
        self.assertIn("release_qualification_measurement.allows_coverage_reduction_for_speed must be false", errors)


if __name__ == "__main__":
    unittest.main()
