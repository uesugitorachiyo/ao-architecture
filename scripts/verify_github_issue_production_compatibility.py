#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOCUMENT = (
    ROOT / "stack" / "github-issue-repair-production-compatibility.json"
)

SCHEMA = "ao.architecture.autonomous-issue-repair.production-compatibility.v1"
DISCOVERY_SCHEMA = "ao.architecture.autonomous-issue-repair.discovery-result.v1"
READBACK_SCHEMA = "ao.command.github-issue-repair-readback.v1"
ARCHITECTURE_COMMIT = "b8c64860003238ab45fe7c76d7e8950f80a4043b"
AO2_COMMIT = "53e45313e8031071d730601a64be22b4d9b0c7fe"
COMMAND_COMMIT = "c1c729db79e6be6037184ea9322f59d1cf511748"
SCHEMA_PATH = (
    "stack/schemas/github-issue-repair/bounded-discovery-result-v1.schema.json"
)
SCHEMA_SHA256 = "f53c8ab36753cc645c48f391d8538ddb0b26cd9fe72edfd149e653e9975b3547"
INPUT_PATH = "examples/github-issue-repair/discovery-page-envelope.valid.json"
INPUT_SHA256 = "0fcb475fff6f23374b1785c8895e3f2c78ca62a832638189657e575164100414"
OUTPUT_PATH = "examples/github-issue-repair/discovery-result.valid.json"
OUTPUT_SHA256 = "b6d4eb04916984388af3568a9715c02397bf95b0cac7c67b3fe7c0f04242e3c3"
RFC3339 = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T"
    r"[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?"
    r"(?:Z|[+-][0-9]{2}:[0-9]{2})$"
)

TOP_FIELDS = {
    "schema",
    "status",
    "contract",
    "producer",
    "consumer",
    "verification",
    "boundaries",
}
CONTRACT_FIELDS = {
    "schema_id",
    "architecture_commit",
    "schema_path",
    "schema_sha256",
}
PRODUCER_FIELDS = {
    "repository",
    "commit",
    "pull_request",
    "workflow_run_ids",
    "input_repository",
    "input_path",
    "input_sha256",
    "output_sha256",
}
CONSUMER_FIELDS = {
    "repository",
    "commit",
    "pull_request",
    "workflow_run_id",
    "fixture_path",
    "fixture_sha256",
    "readback_schema",
}
VERIFICATION_FIELDS = {
    "completed_at",
    "producer_replay",
    "byte_match",
    "consumer_readback",
    "consumer_status",
    "dependency_prefetch",
}
BOUNDARY_FIELDS = {
    "operator_mode",
    "cold_runner_dependency_prefetch_required",
    "producer_runtime_network_required",
    "github_mutation",
    "credential_access",
    "provider_access",
    "approval_granted",
    "safe_to_execute",
    "release_or_publication",
    "activates_compatibility_gate",
}
EXPECTED_PROVENANCE = {
    "schema": "ao.command.github-issue-repair-readback-provenance.v1",
    "architecture_repository": "uesugitorachiyo/ao-architecture",
    "architecture_commit": ARCHITECTURE_COMMIT,
    "source_schema_id": DISCOVERY_SCHEMA,
    "source_schema_path": SCHEMA_PATH,
    "source_schema_sha256": SCHEMA_SHA256,
    "consumer_fixture_path": OUTPUT_PATH,
    "consumer_fixture_sha256": OUTPUT_SHA256,
    "producer_repository": "uesugitorachiyo/ao2",
    "producer_commit": AO2_COMMIT,
    "producer_input_path": INPUT_PATH,
    "producer_input_sha256": INPUT_SHA256,
    "producer_output_path": OUTPUT_PATH,
    "producer_output_sha256": OUTPUT_SHA256,
    "producer_runtime_network_required": False,
    "producer_mutates_github": False,
    "operator_mode": "read_only",
    "network_required": False,
    "shell_required": False,
    "grants_mutation_authority": False,
}
EXPECTED_READBACK = {
    "command_schema_version": "ao.command.v0.1",
    "schema": READBACK_SCHEMA,
    "source_schema": DISCOVERY_SCHEMA,
    "source_contract_commit": ARCHITECTURE_COMMIT,
    "source_schema_sha256": SCHEMA_SHA256,
    "run_id": "repair-run-20260728",
    "repository": "example/repair-fixture",
    "head_sha": "1111111111111111111111111111111111111111",
    "completed_at": "2026-07-27T23:00:00Z",
    "snapshot_count": 2,
    "candidate_count": 1,
    "exclusion_count": 1,
    "selected_issue": 101,
    "status": "candidate_selected",
    "operator_mode": "read_only",
    "safe_to_execute": False,
    "approves_work": False,
    "mutates_github": False,
    "exact_next_action": (
        "Submit the selected candidate only to downstream governance; "
        "AO Command grants no mutation authority."
    ),
}


def _object(
    errors: list[str], document: dict[str, Any], field: str, fields: set[str]
) -> dict[str, Any]:
    value = document.get(field)
    if not isinstance(value, dict):
        errors.append(f"{field} must be an object")
        return {}
    if set(value) != fields:
        errors.append(f"{field} fields must exactly match the strict schema")
    return value


def validate_document(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if set(document) != TOP_FIELDS:
        errors.append("document fields must exactly match the strict schema")
    if document.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA}")
    if document.get("status") != "passed":
        errors.append("status must be passed")

    contract = _object(errors, document, "contract", CONTRACT_FIELDS)
    expected_contract = {
        "schema_id": DISCOVERY_SCHEMA,
        "architecture_commit": ARCHITECTURE_COMMIT,
        "schema_path": SCHEMA_PATH,
        "schema_sha256": SCHEMA_SHA256,
    }
    for field, expected in expected_contract.items():
        if contract.get(field) != expected:
            errors.append(f"contract.{field} must bind the exact Architecture contract")

    producer = _object(errors, document, "producer", PRODUCER_FIELDS)
    expected_producer = {
        "repository": "uesugitorachiyo/ao2",
        "commit": AO2_COMMIT,
        "pull_request": "https://github.com/uesugitorachiyo/ao2/pull/597",
        "workflow_run_ids": [30342174321, 30342174346],
        "input_repository": "uesugitorachiyo/ao-command",
        "input_path": INPUT_PATH,
        "input_sha256": INPUT_SHA256,
        "output_sha256": OUTPUT_SHA256,
    }
    for field, expected in expected_producer.items():
        if producer.get(field) != expected:
            errors.append(f"producer.{field} must bind the exact merged AO2 evidence")

    consumer = _object(errors, document, "consumer", CONSUMER_FIELDS)
    expected_consumer = {
        "repository": "uesugitorachiyo/ao-command",
        "commit": COMMAND_COMMIT,
        "pull_request": "https://github.com/uesugitorachiyo/ao-command/pull/150",
        "workflow_run_id": 30344676144,
        "fixture_path": OUTPUT_PATH,
        "fixture_sha256": OUTPUT_SHA256,
        "readback_schema": READBACK_SCHEMA,
    }
    for field, expected in expected_consumer.items():
        if consumer.get(field) != expected:
            errors.append(f"consumer.{field} must bind the exact merged Command evidence")

    verification = _object(
        errors, document, "verification", VERIFICATION_FIELDS
    )
    if (
        not isinstance(verification.get("completed_at"), str)
        or not RFC3339.fullmatch(verification["completed_at"])
    ):
        errors.append("verification.completed_at must be RFC3339")
    for field in ("producer_replay", "consumer_readback"):
        if verification.get(field) != "passed":
            errors.append(f"verification.{field} must be passed")
    if verification.get("byte_match") is not True:
        errors.append("verification.byte_match must be true")
    if verification.get("consumer_status") != "candidate_selected":
        errors.append("verification.consumer_status must be candidate_selected")
    if verification.get("dependency_prefetch") != "lockfile_verified":
        errors.append("verification.dependency_prefetch must be lockfile_verified")

    boundaries = _object(errors, document, "boundaries", BOUNDARY_FIELDS)
    if boundaries.get("operator_mode") != "read_only":
        errors.append("boundaries.operator_mode must be read_only")
    if boundaries.get("cold_runner_dependency_prefetch_required") is not True:
        errors.append(
            "boundaries.cold_runner_dependency_prefetch_required must be true"
        )
    for field in BOUNDARY_FIELDS - {
        "operator_mode",
        "cold_runner_dependency_prefetch_required",
    }:
        if boundaries.get(field) is not False:
            errors.append(f"boundaries.{field} must be false")
    return errors


def _sha256(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def _execution_environment() -> dict[str, str]:
    environment = {
        name: os.environ[name]
        for name in (
            "PATH",
            "HOME",
            "CARGO_HOME",
            "RUSTUP_HOME",
            "GOCACHE",
            "GOMODCACHE",
            "GOPATH",
            "TMPDIR",
            "LANG",
            "LC_ALL",
        )
        if name in os.environ
    }
    environment.update(
        {
            "CARGO_NET_OFFLINE": "true",
            "GIT_NO_REPLACE_OBJECTS": "1",
            "GOENV": "off",
            "GONOSUMDB": "*",
            "GOPROXY": "off",
            "GOTOOLCHAIN": "local",
            "RUSTUP_TOOLCHAIN": "1.95.0",
        }
    )
    return environment


def _run(args: list[str], repository: Path, timeout: int = 900) -> bytes:
    process = subprocess.run(
        args,
        cwd=repository,
        env=_execution_environment(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )
    if process.returncode != 0:
        stderr = process.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"{args[0]} exited {process.returncode}: {stderr}")
    return process.stdout


def _head(repository: Path) -> str:
    return _run(["git", "rev-parse", "HEAD"], repository, timeout=30).decode().strip()


def _export_commit(repository: Path, commit: str, destination: Path) -> None:
    archive = _run(
        ["git", "--no-pager", "archive", "--format=tar", commit],
        repository,
        timeout=60,
    )
    destination.mkdir()
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as bundle:
        bundle.extractall(destination)


def _exact_object_errors(
    label: str, actual: dict[str, Any], expected: dict[str, Any]
) -> list[str]:
    errors = []
    if set(actual) != set(expected):
        errors.append(f"{label} fields must exactly match the production contract")
    for field, expected_value in expected.items():
        if actual.get(field) != expected_value:
            errors.append(f"{label}.{field} does not match the production contract")
    return errors


def validate_provenance(provenance: dict[str, Any]) -> list[str]:
    return _exact_object_errors("provenance", provenance, EXPECTED_PROVENANCE)


def validate_readback(readback: dict[str, Any]) -> list[str]:
    return _exact_object_errors("readback", readback, EXPECTED_READBACK)


def replay_pair(ao2_repository: Path, command_repository: Path) -> None:
    if _head(ao2_repository) != AO2_COMMIT:
        raise RuntimeError("AO2 checkout is not the exact recorded producer commit")
    if _head(command_repository) != COMMAND_COMMIT:
        raise RuntimeError("AO Command checkout is not the exact recorded consumer commit")

    schema = (ROOT / SCHEMA_PATH).read_bytes()
    if _sha256(schema) != SCHEMA_SHA256:
        raise RuntimeError("Architecture schema digest does not match")

    with tempfile.TemporaryDirectory(prefix="ao-issue-compatibility-") as temp:
        export_root = Path(temp)
        exported_ao2 = export_root / "ao2"
        exported_command = export_root / "ao-command"
        _export_commit(ao2_repository, AO2_COMMIT, exported_ao2)
        _export_commit(command_repository, COMMAND_COMMIT, exported_command)

        producer_source = (
            exported_ao2
            / "crates"
            / "ao2-cli"
            / "src"
            / "github_issue_discovery.rs"
        ).read_text(encoding="utf-8")
        if (
            DISCOVERY_SCHEMA not in producer_source
            or "mutation_performed: false" not in producer_source
        ):
            raise RuntimeError(
                "AO2 producer source does not retain the discovery schema "
                "and read-only boundary"
            )

        input_path = exported_command / INPUT_PATH
        fixture_path = exported_command / OUTPUT_PATH
        if _sha256(input_path.read_bytes()) != INPUT_SHA256:
            raise RuntimeError("sanitized producer input digest does not match")
        fixture = fixture_path.read_bytes()
        if _sha256(fixture) != OUTPUT_SHA256:
            raise RuntimeError("consumer fixture digest does not match")

        provenance = json.loads(
            (
                exported_command
                / "examples"
                / "github-issue-repair"
                / "provenance-manifest.json"
            ).read_text(encoding="utf-8")
        )
        provenance_errors = validate_provenance(provenance)
        if provenance_errors:
            raise RuntimeError("; ".join(provenance_errors))

        replay_path = Path(temp) / "discovery-result.json"
        replay = _run(
            [
                "cargo",
                "run",
                "--quiet",
                "--locked",
                "--offline",
                "--bin",
                "ao2",
                "--",
                "issue",
                "discover",
                "--page-envelope",
                str(input_path),
                "--url",
                "https://github.com/example/repair-fixture/issues/?ignored=yes#fragment",
                "--repository",
                "example/repair-fixture",
                "--default-branch",
                "master",
                "--head-sha",
                "1111111111111111111111111111111111111111",
                "--run-id",
                "repair-run-20260728",
                "--completed-at",
                "2026-07-27T23:00:00Z",
                "--snapshot-limit",
                "50",
                "--candidate-limit",
                "10",
                "--json",
            ],
            exported_ao2,
        )
        replay_path.write_bytes(replay)
        if replay != fixture or _sha256(replay) != OUTPUT_SHA256:
            raise RuntimeError("AO2 replay does not byte-match the Command fixture")

        readback = json.loads(
            _run(
                [
                    "go",
                    "run",
                    "./cmd/ao-command",
                    "github-issue",
                    "repair-readback",
                    "--discovery",
                    str(replay_path),
                    "--json",
                ],
                exported_command,
            )
        )
    readback_errors = validate_readback(readback)
    if readback_errors:
        raise RuntimeError("; ".join(readback_errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--document", type=Path, default=DEFAULT_DOCUMENT)
    parser.add_argument("--ao2-repository", type=Path)
    parser.add_argument("--command-repository", type=Path)
    parser.add_argument("--replay", action="store_true")
    args = parser.parse_args()

    document = json.loads(args.document.read_text(encoding="utf-8"))
    errors = validate_document(document)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    if args.replay:
        if args.ao2_repository is None or args.command_repository is None:
            print("--replay requires both repository paths", file=sys.stderr)
            return 2
        try:
            replay_pair(
                args.ao2_repository.resolve(),
                args.command_repository.resolve(),
            )
        except (OSError, RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError) as error:
            print(f"production compatibility replay failed: {error}", file=sys.stderr)
            return 1
    print(
        "verify_github_issue_production_compatibility.py: "
        "validated exact AO2 producer and AO Command consumer evidence"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
