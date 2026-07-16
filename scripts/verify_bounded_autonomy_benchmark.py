#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS = ROOT / "stack" / "bounded-autonomy-benchmark-corpus.json"
DEFAULT_SCHEMA = ROOT / "stack" / "bounded-autonomy-benchmark-result-schema.json"
DEFAULT_RESULTS = ROOT / "stack" / "bounded-autonomy-month1-baseline-results.json"

REQUIRED_TASK_CLASSES = {
    "documentation_correction",
    "single_repo_code_fix",
    "cross_repo_contract_update",
    "approval_required_mutation",
    "rollback_required_mutation",
    "failed_ci_diagnosis_repair",
    "interrupted_mission_resume",
}
REQUIRED_FAILURE_CLASSES = {
    "product",
    "workflow",
    "environment",
    "policy",
    "provider",
    "operator",
    "evidence_integrity",
}
REQUIRED_METRICS = {
    "completion_rate",
    "first_pass_verification_rate",
    "recovery_rate",
    "human_approvals",
    "human_interventions",
    "duplicate_work_count",
    "orphan_branch_count",
    "ready_node_count",
    "elapsed_seconds",
    "retry_count",
    "rollback_result",
    "evidence_integrity_result",
    "escaped_defect_count",
    "unsupported_claim_count",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_boundaries(errors: list[str], boundaries: dict[str, Any] | None) -> None:
    if not isinstance(boundaries, dict):
        errors.append("boundaries is required")
        return
    required = {
        "rsi_remains_denied": True,
        "provider_pilot": False,
        "external_beta_launched": False,
        "promotion_requested": False,
        "release_or_upload": False,
    }
    for key, expected in required.items():
        if boundaries.get(key) is not expected:
            want = str(expected).lower()
            errors.append(f"boundaries.{key} must remain {want}")


def validate_corpus(corpus: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if corpus.get("schema") != "ao.architecture.bounded-autonomy-benchmark-corpus.v0.1":
        errors.append("schema must be ao.architecture.bounded-autonomy-benchmark-corpus.v0.1")
    if corpus.get("benchmark_version") != "bounded-autonomy-month1-v0.1":
        errors.append("benchmark_version must be bounded-autonomy-month1-v0.1")
    pair = corpus.get("current_public_pair")
    if not isinstance(pair, dict):
        errors.append("current_public_pair is required")
    else:
        if pair.get("ao2_version") != "v0.5.1":
            errors.append("current_public_pair.ao2_version must be v0.5.1")
        if pair.get("control_plane_version") != "v0.1.15":
            errors.append("current_public_pair.control_plane_version must be v0.1.15")
    task_ids = {
        task.get("id")
        for task in corpus.get("task_classes", [])
        if isinstance(task, dict)
    }
    for task_id in sorted(REQUIRED_TASK_CLASSES):
        if task_id not in task_ids:
            errors.append(f"task_classes must include {task_id}")
    failure_classes = set(corpus.get("failure_classes", []))
    for failure_class in sorted(REQUIRED_FAILURE_CLASSES):
        if failure_class not in failure_classes:
            errors.append(f"failure_classes must include {failure_class}")
    validate_boundaries(errors, corpus.get("boundaries") if isinstance(corpus.get("boundaries"), dict) else None)
    return errors


def validate_schema(schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if schema.get("schema") != "ao.architecture.bounded-autonomy-benchmark-result-schema.v0.1":
        errors.append("schema must be ao.architecture.bounded-autonomy-benchmark-result-schema.v0.1")
    if schema.get("benchmark_version") != "bounded-autonomy-month1-v0.1":
        errors.append("benchmark_version must be bounded-autonomy-month1-v0.1")
    metrics = set(schema.get("required_metrics", []))
    for metric in sorted(REQUIRED_METRICS):
        if metric not in metrics:
            errors.append(f"required_metrics must include {metric}")
    failure_classes = set(schema.get("required_failure_classes", []))
    for failure_class in sorted(REQUIRED_FAILURE_CLASSES):
        if failure_class not in failure_classes:
            errors.append(f"required_failure_classes must include {failure_class}")
    return errors


def validate_results(results: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if results.get("schema") != "ao.architecture.bounded-autonomy-baseline-results.v0.1":
        errors.append("schema must be ao.architecture.bounded-autonomy-baseline-results.v0.1")
    if results.get("benchmark_version") != schema.get("benchmark_version"):
        errors.append("benchmark_version must match result schema")
    if results.get("status") != "baseline_recorded":
        errors.append("status must be baseline_recorded")
    metrics = results.get("metrics")
    if not isinstance(metrics, dict):
        errors.append("metrics is required")
    else:
        for metric in schema.get("required_metrics", []):
            if metric not in metrics:
                errors.append(f"metrics.{metric} is required")
    classes = results.get("failure_classification")
    if not isinstance(classes, dict):
        errors.append("failure_classification is required")
    else:
        for failure_class in schema.get("required_failure_classes", []):
            if failure_class not in classes:
                errors.append(f"failure_classification.{failure_class} is required")
    validate_boundaries(errors, results.get("boundaries") if isinstance(results.get("boundaries"), dict) else None)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate bounded-autonomy benchmark corpus, schema, and Month 1 baseline")
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    args = parser.parse_args()
    try:
        corpus = read_json(args.corpus)
        schema = read_json(args.schema)
        results = read_json(args.results)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"verify_bounded_autonomy_benchmark.py: {exc}", file=sys.stderr)
        return 1
    errors = []
    errors.extend(validate_corpus(corpus))
    errors.extend(validate_schema(schema))
    errors.extend(validate_results(results, schema))
    if errors:
        for error in errors:
            print(f"verify_bounded_autonomy_benchmark.py: {error}", file=sys.stderr)
        return 1
    print("verify_bounded_autonomy_benchmark.py: bounded autonomy benchmark baseline verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
