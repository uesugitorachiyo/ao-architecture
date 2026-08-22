#!/usr/bin/env python3
"""Run the frozen repository-owned development gates sequentially."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any, Callable, Sequence


sys.path.insert(0, str(Path(__file__).resolve().parent))
import bootstrap_development_baseline as bootstrap  # noqa: E402


MAX_GATE_OUTPUT_BYTES = 1024 * 1024


class GateError(ValueError):
    pass


def prepare_output_root(path: str | Path) -> Path:
    target = Path(os.path.abspath(os.fspath(path)))
    bootstrap._require_no_link_ancestors(target.parent)
    if target.exists() or bootstrap.is_link_or_reparse(target):
        raise GateError("output root must be absent")
    target.mkdir(parents=False)
    return target


def _safe_identifier(value: Any, label: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", value):
        raise GateError(f"unsafe {label}")
    return value


def resolve_gate_argv(
    gate: dict[str, Any],
    *,
    operating_system: str | None = None,
    which: Callable[[str], str | None] = shutil.which,
) -> list[str]:
    argv = gate.get("argv")
    if not isinstance(argv, list) or not argv or not all(
        isinstance(item, str) and item for item in argv
    ):
        raise GateError("gate argv is invalid")
    shell = gate.get("shell")
    current_os = operating_system or os.name
    if shell == "direct":
        try:
            return bootstrap.resolve_command_argv(
                argv, operating_system=current_os, which=which
            )
        except bootstrap.BootstrapError as exc:
            raise GateError(str(exc)) from exc
    if shell != "posix-script":
        raise GateError("gate shell is invalid")
    script = argv[0]
    if Path(script).is_absolute() or ".." in Path(script).parts or not script.endswith(".sh"):
        raise GateError("POSIX gate script path is unsafe")
    bash = which("bash")
    if current_os == "nt":
        if bash is None or not re.search(r"[\\/]Git[\\/](?:bin|usr[\\/]bin)[\\/]bash\.exe$", bash, re.IGNORECASE):
            raise GateError("Git for Windows Bash is required")
    elif bash is None:
        raise GateError("Bash is required for POSIX gate scripts")
    return [bash, *argv]


def select_gate(
    repositories: Sequence[dict[str, Any]], repository_name: str, gate_id: str
) -> dict[str, Any]:
    for repository in repositories:
        if repository.get("name") != repository_name:
            continue
        for gate in repository.get("development_gates", []):
            if isinstance(gate, dict) and gate.get("id") == gate_id:
                return gate
        raise GateError(f"unknown gate: {repository_name}/{gate_id}")
    raise GateError(f"unknown repository: {repository_name}")


def _git(checkout: Path, argv: Sequence[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    executable = shutil.which("git")
    if executable is None:
        raise GateError("git executable was not found")
    completed = subprocess.run(
        [executable, *argv],
        cwd=checkout,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=120,
        check=False,
        shell=False,
        env={**os.environ, "GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "Never"},
    )
    if check and completed.returncode != 0:
        raise GateError(f"git inspection failed: {argv[0]}")
    return completed


def tracked_state(checkout: Path) -> tuple[str, bool]:
    head = _git(checkout, ["rev-parse", "HEAD"]).stdout.strip()
    status = _git(
        checkout, ["status", "--porcelain=v1", "--untracked-files=no"]
    ).stdout
    index = _git(checkout, ["ls-files", "-s"]).stdout
    diff = _git(checkout, ["diff", "--binary", "HEAD"]).stdout
    body = (head + "\n" + index + diff).encode("utf-8")
    return "sha256:" + hashlib.sha256(body).hexdigest(), bool(status)


def verify_repository(checkout: Path, repository: dict[str, Any]) -> str:
    if bootstrap.is_link_or_reparse(checkout) or not checkout.is_dir():
        raise GateError(f"repository is missing or unsafe: {repository.get('name')}")
    head = _git(checkout, ["rev-parse", "HEAD"]).stdout.strip()
    if head != repository.get("commit"):
        raise GateError(f"repository commit mismatch: {repository.get('name')}")
    symbolic = _git(checkout, ["symbolic-ref", "-q", "HEAD"], check=False)
    if symbolic.returncode not in {1, 128}:
        raise GateError(f"repository is not detached: {repository.get('name')}")
    origin = _git(checkout, ["remote", "get-url", "origin"]).stdout.strip()
    if not bootstrap._same_upstream(origin, str(repository.get("upstream_url", ""))):
        raise GateError(f"repository origin mismatch: {repository.get('name')}")
    state, dirty = tracked_state(checkout)
    if dirty:
        raise GateError(f"repository tracked state is dirty: {repository.get('name')}")
    return state


def _write_log(path: Path, body: bytes, maximum: int) -> tuple[str, int, bool]:
    retained = body[:maximum]
    with path.open("xb") as output:
        output.write(retained)
    return (
        "sha256:" + hashlib.sha256(body).hexdigest(),
        len(body),
        len(body) > maximum,
    )


def _run_one_gate(
    checkout: Path,
    repository_name: str,
    gate: dict[str, Any],
    log_root: Path,
    maximum: int,
) -> dict[str, Any]:
    gate_id = _safe_identifier(gate.get("id"), "gate id")
    before_digest, before_dirty = tracked_state(checkout)
    if before_dirty:
        raise GateError(f"repository tracked state is dirty before gate: {repository_name}/{gate_id}")
    argv = resolve_gate_argv(gate)
    environment = os.environ.copy()
    environment.update(
        {
            "GIT_TERMINAL_PROMPT": "0",
            "GCM_INTERACTIVE": "Never",
            "GIT_OPTIONAL_LOCKS": "0",
            **gate.get("environment", {}),
        }
    )
    timed_out = False
    exit_status: int | None
    try:
        completed = subprocess.run(
            argv,
            cwd=checkout,
            env=environment,
            capture_output=True,
            timeout=gate["timeout_seconds"],
            check=False,
            shell=False,
        )
        stdout = completed.stdout
        stderr = completed.stderr
        exit_status = completed.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = exc.stdout or b""
        stderr = exc.stderr or b""
        if isinstance(stdout, str):
            stdout = stdout.encode("utf-8", errors="replace")
        if isinstance(stderr, str):
            stderr = stderr.encode("utf-8", errors="replace")
        exit_status = None
    except OSError as exc:
        stdout = b""
        stderr = str(exc).encode("utf-8", errors="replace")
        exit_status = None

    stdout_path = log_root / f"{gate_id}.stdout.log"
    stderr_path = log_root / f"{gate_id}.stderr.log"
    stdout_digest, stdout_bytes, stdout_truncated = _write_log(stdout_path, stdout, maximum)
    stderr_digest, stderr_bytes, stderr_truncated = _write_log(stderr_path, stderr, maximum)
    after_digest, after_dirty = tracked_state(checkout)
    failure_category: str | None = None
    if timed_out:
        failure_category = "timeout"
    elif stdout_truncated or stderr_truncated:
        failure_category = "output_limit"
    elif exit_status != 0:
        failure_category = "nonzero_exit" if exit_status is not None else "launch_failure"
    elif gate.get("success_stdout", "any") == "empty" and stdout:
        failure_category = "stdout_policy"
    elif after_dirty or after_digest != before_digest:
        failure_category = "tracked_state_drift"
    return {
        "repository": repository_name,
        "gate_id": gate_id,
        "status": "fail" if failure_category else "pass",
        "failure_category": failure_category,
        "exit_status": exit_status,
        "timed_out": timed_out,
        "stdout_path": f"{repository_name}/{stdout_path.name}",
        "stdout_bytes": stdout_bytes,
        "stdout_sha256": stdout_digest,
        "stdout_truncated": stdout_truncated,
        "stderr_path": f"{repository_name}/{stderr_path.name}",
        "stderr_bytes": stderr_bytes,
        "stderr_sha256": stderr_digest,
        "stderr_truncated": stderr_truncated,
        "tracked_state_before": before_digest,
        "tracked_state_after": after_digest,
    }


def run_gate_inventory(
    root: str | Path,
    repositories: Sequence[dict[str, Any]],
    output_root: str | Path,
    *,
    max_output_bytes: int = MAX_GATE_OUTPUT_BYTES,
) -> dict[str, Any]:
    workspace = bootstrap.validate_materialization_root(root, "verify-existing")
    output = prepare_output_root(output_root)
    records: list[dict[str, Any]] = []
    for repository in repositories:
        name = _safe_identifier(repository.get("name"), "repository name")
        checkout = bootstrap.contained_child(workspace, str(repository.get("path")))
        verify_repository(checkout, repository)
        repository_logs = output / name
        repository_logs.mkdir()
        development_gates = repository.get("development_gates")
        if not isinstance(development_gates, list) or not development_gates:
            raise GateError(f"repository has no development gates: {name}")
        for gate in development_gates:
            if not isinstance(gate, dict) or gate.get("required") is not True:
                raise GateError(f"undeclared skip or invalid gate: {name}")
            record = _run_one_gate(
                checkout, name, gate, repository_logs, max_output_bytes
            )
            records.append(record)
            if record["status"] != "pass":
                return {
                    "schema": "ao.architecture.development-baseline-gate-result.v1",
                    "status": "fail",
                    "gates": records,
                    "authority": dict(bootstrap.AUTHORITY),
                }
    return {
        "schema": "ao.architecture.development-baseline-gate-result.v1",
        "status": "pass",
        "gates": records,
        "authority": dict(bootstrap.AUTHORITY),
    }


def argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run frozen repository development gates.")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--release-manifest", required=True, type=Path)
    parser.add_argument("--controller-commit", required=True)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--result", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = argument_parser().parse_args(argv)
    try:
        bootstrap.validate_cli_commit(args.controller_commit)
        manifest = bootstrap.load_json_file(args.manifest, 1024 * 1024)
        schema = bootstrap.load_json_file(args.schema, 256 * 1024)
        release = bootstrap.load_json_file(args.release_manifest, 1024 * 1024)
        errors = bootstrap.validate_s01_inputs(
            manifest, schema, release, args.release_manifest
        )
        if errors:
            raise GateError("; ".join(sorted(set(errors))))
        result_path = bootstrap.validate_result_path(args.root, args.result, "verify-existing")
        specs = bootstrap.repository_specs(manifest)
        bootstrap.verify_repositories(args.root, specs, bootstrap.CommandRunner())
        document = run_gate_inventory(
            args.root, manifest["repositories"], args.output
        )
        document.update(
            {
                "correlation_id": "ao-cross-platform-development-baseline-20260822-r2",
                "slice": "S03",
                "controller_source_commit": args.controller_commit,
                "baseline_identity": "sha256:"
                + hashlib.sha256(bootstrap.canonical_bytes(manifest)).hexdigest(),
                "platform": bootstrap.native_platform(),
                "repository_count": len(manifest["repositories"]),
                "declared_gate_count": sum(
                    len(repository["development_gates"])
                    for repository in manifest["repositories"]
                ),
                "completed_gate_count": len(document["gates"]),
            }
        )
        digest = bootstrap.write_json_exclusive(result_path, document)
    except (bootstrap.BootstrapError, GateError) as exc:
        print(f"error={exc}", file=sys.stderr)
        return 1
    print(f"result_digest={digest}")
    print(f"baseline_identity={document['baseline_identity']}")
    print(f"repositories={document['repository_count']}")
    print(f"declared_gates={document['declared_gate_count']}")
    print(f"completed_gates={document['completed_gate_count']}")
    print(f"status={document['status']}")
    print("errors=0" if document["status"] == "pass" else "errors=1")
    return 0 if document["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
