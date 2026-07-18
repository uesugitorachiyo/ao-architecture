from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = ROOT / "stack" / "dsa-measurement-contract.json"
EXPECTED_FIELDS = {
    "correctness_invariant",
    "input_size_dimension",
    "expected_complexity_class",
    "operation_or_file_read_count_evidence",
    "allocation_evidence",
    "repeated_wall_clock_benchmark_evidence",
    "deterministic_output_requirement",
    "compatibility_requirement",
}


def require_bool(errors: list[str], document: dict[str, Any], path: str, expected: bool) -> None:
    current: Any = document
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            errors.append(f"{path} must be {str(expected).lower()}")
            return
        current = current[part]
    if current is not expected:
        errors.append(f"{path} must be {str(expected).lower()}")


def validate_document(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != "ao.architecture.dsa-measurement-contract.v0.1":
        errors.append("schema must be ao.architecture.dsa-measurement-contract.v0.1")
    if document.get("status") != "active":
        errors.append("status must be active")
    if document.get("standard_input_sizes") != [100, 1000, 10000]:
        errors.append("standard_input_sizes must be [100, 1000, 10000]")
    if document.get("status_values") != ["pass", "regression", "inconclusive"]:
        errors.append("status_values must be ['pass', 'regression', 'inconclusive']")

    fields = document.get("required_measurement_fields")
    if not isinstance(fields, list):
        errors.append("required_measurement_fields must be an array")
        fields = []
    for field in sorted(EXPECTED_FIELDS - set(fields)):
        errors.append(f"required_measurement_fields missing {field}")
    for field in sorted(set(fields) - EXPECTED_FIELDS):
        errors.append(f"required_measurement_fields unexpected {field}")

    require_bool(errors, document, "complexity_claim_rules.requires_implementation_argument", True)
    require_bool(errors, document, "complexity_claim_rules.requires_scale_evidence", True)
    require_bool(errors, document, "complexity_claim_rules.prefers_operation_counts_over_single_timing", True)
    require_bool(errors, document, "measurement_rules.operation_counts_preferred", True)
    require_bool(errors, document, "measurement_rules.single_noisy_timing_must_not_fail_ci", True)
    require_bool(errors, document, "measurement_rules.lower_bound_required_when_10000_items_is_unsafe", True)
    require_bool(errors, document, "measurement_rules.baseline_and_post_change_commits_required", True)
    require_bool(errors, document, "measurement_rules.no_credential_or_provider_dependency", True)
    require_bool(errors, document, "release_qualification_measurement.records_cumulative_compute_time", True)
    require_bool(errors, document, "release_qualification_measurement.records_operator_wall_time", True)
    require_bool(errors, document, "release_qualification_measurement.records_external_wait_separately", True)
    require_bool(errors, document, "release_qualification_measurement.requires_digest_bound_reuse", True)
    require_bool(errors, document, "release_qualification_measurement.allows_coverage_reduction_for_speed", False)
    require_bool(errors, document, "safety.promotion_granted", False)
    require_bool(errors, document, "safety.rsi_remains_denied", True)
    require_bool(errors, document, "safety.release_claim_made_by_contract", False)

    reuse_keys = document.get("digest_bound_reuse_keys")
    if not isinstance(reuse_keys, list) or not reuse_keys:
        errors.append("digest_bound_reuse_keys must be a non-empty array")
    elif len(reuse_keys) != len(set(reuse_keys)):
        errors.append("digest_bound_reuse_keys must not contain duplicates")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the AO DSA measurement contract")
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    args = parser.parse_args()
    try:
        document = json.loads(args.contract.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"verify_dsa_measurement_contract.py: {exc}", file=sys.stderr)
        return 1
    errors = validate_document(document)
    if errors:
        for error in errors:
            print(f"verify_dsa_measurement_contract.py: {error}", file=sys.stderr)
        return 1
    print("verify_dsa_measurement_contract.py: DSA measurement contract verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
