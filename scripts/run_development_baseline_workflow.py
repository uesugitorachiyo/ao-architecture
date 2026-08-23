#!/usr/bin/env python3
"""Run the frozen credential-free AO development-baseline fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import time


FIXTURE_SCHEMA = "ao.architecture.development-baseline-workflow-fixture.v1"
RESULT_SCHEMA = "ao.architecture.development-baseline-workflow-result.v1"
CORRELATION_ID = "ao-cross-platform-development-baseline-20260822-r2"
REQUIRED_STAGES = (
    ("mission-intake", "ao-mission", "accepted"),
    ("blueprint-authorization", "ao-blueprint", "authorized"),
    ("atlas-workgraph", "ao-atlas", "workgraph_ready"),
    ("foundry-coordination", "ao-foundry", "coordinated"),
    ("forge-coordination", "ao-forge", "coordinated"),
    ("covenant-decision", "ao-covenant", "deny_undeclared_side_effects"),
    ("ao2-scripted-fixture", "ao2", "passed"),
    ("control-plane-observation", "ao2-control-plane", "observed"),
    ("command-readback", "ao-command", "ready"),
    ("mission-readback", "ao-mission", "ready"),
    ("arena-assurance", "ao-arena", "passed"),
    ("crucible-assurance", "ao-crucible", "passed"),
    ("sentinel-assurance", "ao-sentinel", "clear"),
    ("promoter-no-promotion", "ao-promoter", "no_promotion"),
)
AUTHORITY_FIELDS = (
    "safe_to_execute", "executes_work", "approves_work", "mutates_repositories",
    "provider_calls", "credential_use", "release", "publication", "deployment",
    "promotion", "compatibility_activation", "external_beta", "rsi",
)
FIXTURE_KEYS = {"schema", "correlation_id", "baseline_identity", "stages", "authority"}
STAGE_KEYS = {"id", "repository", "source_commit", "consumes", "argv", "artifact", "terminal_status", "outcome", "timeout_seconds"}
ARTIFACT_KEYS = {"source", "path", "max_bytes", "json"}
SHELLS = {"sh", "bash", "cmd", "cmd.exe", "powershell", "powershell.exe", "pwsh", "pwsh.exe"}
FORBIDDEN = {"publish", "publication", "release", "deploy", "deployment", "promote", "promotion", "rsi", "apply"}
MAX_STAGES = 14


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _strict_keys(document, allowed, label):
    unknown = set(document) - set(allowed)
    if unknown:
        raise ValueError(f"unknown {label} property: {sorted(unknown)[0]}")


def _safe_relative(value, label):
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or "\\" in value:
        raise ValueError(f"unsafe {label} path")


def _false_authority(authority):
    if not isinstance(authority, dict) or set(authority) != set(AUTHORITY_FIELDS):
        raise ValueError("authority fields must match the closed inventory")
    if any(value is not False for value in authority.values()):
        raise ValueError("authority must remain false")


def validate_fixture(document):
    if not isinstance(document, dict):
        raise ValueError("fixture must be one JSON object")
    _strict_keys(document, FIXTURE_KEYS, "fixture")
    if document.get("schema") != FIXTURE_SCHEMA:
        raise ValueError("fixture schema mismatch")
    if document.get("correlation_id") != CORRELATION_ID:
        raise ValueError("correlation mismatch")
    identity = document.get("baseline_identity", "")
    if len(identity) != 71 or not identity.startswith("sha256:") or any(c not in "0123456789abcdef" for c in identity[7:]):
        raise ValueError("baseline identity must be sha256 plus 64 lowercase hex characters")
    _false_authority(document.get("authority"))
    stages = document.get("stages")
    if not isinstance(stages, list) or len(stages) != MAX_STAGES:
        raise ValueError("stage order must contain exactly 14 entries")
    for index, (stage, expected) in enumerate(zip(stages, REQUIRED_STAGES)):
        if not isinstance(stage, dict):
            raise ValueError("stage must be an object")
        _strict_keys(stage, STAGE_KEYS, "stage")
        stage_id, repository, outcome = expected
        if stage.get("id") != stage_id:
            raise ValueError("stage order mismatch")
        if stage.get("repository") != repository:
            raise ValueError(f"repository mismatch for {stage_id}")
        commit = stage.get("source_commit", "")
        if len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
            raise ValueError(f"source commit invalid for {stage_id}")
        expected_consumes = [] if index == 0 else [REQUIRED_STAGES[index - 1][0]]
        if stage.get("consumes") != expected_consumes:
            raise ValueError(f"producer binding mismatch for {stage_id}")
        argv = stage.get("argv")
        if not isinstance(argv, list) or not argv or any(not isinstance(item, str) or not item for item in argv):
            raise ValueError(f"argv invalid for {stage_id}")
        executable = Path(argv[0]).name.lower()
        lowered = {item.lower() for item in argv}
        if executable in SHELLS or "-c" in lowered or "-command" in lowered:
            raise ValueError(f"shell dispatch forbidden for {stage_id}")
        if "--provider" in lowered:
            provider_index = [item.lower() for item in argv].index("--provider")
            if provider_index + 1 >= len(argv) or argv[provider_index + 1].lower() != "scripted":
                raise ValueError(f"forbidden authority request in {stage_id}")
        if lowered & FORBIDDEN:
            raise ValueError(f"forbidden authority request in {stage_id}")
        artifact = stage.get("artifact")
        if not isinstance(artifact, dict):
            raise ValueError(f"artifact contract invalid for {stage_id}")
        _strict_keys(artifact, ARTIFACT_KEYS, "artifact")
        if artifact.get("source") not in {"stdout", "file"}:
            raise ValueError(f"artifact source invalid for {stage_id}")
        if artifact.get("source") == "file":
            _safe_relative(artifact.get("path", ""), "artifact")
        limit = artifact.get("max_bytes")
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1 or limit > 1_048_576:
            raise ValueError(f"artifact size bound invalid for {stage_id}")
        if artifact.get("json", False) not in {True, False}:
            raise ValueError(f"artifact json flag invalid for {stage_id}")
        if stage.get("terminal_status") != "pass":
            raise ValueError(f"terminal status invalid for {stage_id}")
        if stage.get("outcome") != outcome:
            raise ValueError(f"expected outcome {outcome} for {stage_id}")
        timeout = stage.get("timeout_seconds", 300)
        if not isinstance(timeout, int) or isinstance(timeout, bool) or not 1 <= timeout <= 1800:
            raise ValueError(f"timeout invalid for {stage_id}")


def validate_result(document):
    if document.get("schema") != RESULT_SCHEMA or document.get("status") != "pass":
        raise ValueError("result must be terminal pass")
    if document.get("correlation_id") != CORRELATION_ID:
        raise ValueError("result correlation mismatch")
    identity = document.get("baseline_identity", "")
    if len(identity) != 71 or not identity.startswith("sha256:"):
        raise ValueError("result baseline identity invalid")
    _false_authority(document.get("authority"))
    stages = document.get("stages", [])
    if [item.get("id") for item in stages] != [item[0] for item in REQUIRED_STAGES]:
        raise ValueError("result stage order mismatch")
    for stage in stages:
        digest = stage.get("artifact_sha256", "")
        if len(digest) != 71 or not digest.startswith("sha256:") or any(c not in "0123456789abcdef" for c in digest[7:]):
            raise ValueError("artifact digest invalid")
        if stage.get("status") != "pass":
            raise ValueError("result contains nonterminal stage")
    cleanup = document.get("cleanup", {})
    if cleanup != {"run_owned_processes": 0, "run_owned_listeners": 0, "temporary_root": "removed"}:
        raise ValueError("cleanup is incomplete")


def _read_json(path):
    with Path(path).open("r", encoding="utf-8") as source:
        return json.load(source)


def validate_baseline_binding(fixture, baseline):
    if fixture["baseline_identity"] != _sha256(json.dumps(baseline, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")):
        raise ValueError("fixture baseline identity mismatch")
    repositories = {item.get("name"): item.get("commit") for item in baseline.get("repositories", [])}
    for stage in fixture["stages"]:
        if repositories.get(stage["repository"]) != stage["source_commit"]:
            raise ValueError(f"fixture source is not frozen by baseline: {stage['repository']}")


def _head(repository):
    completed = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repository, capture_output=True, text=True, check=False)
    if completed.returncode:
        raise ValueError(f"cannot resolve source commit: {Path(repository).name}")
    return completed.stdout.strip()


def _environment(run_root):
    allowed = {
        "PATH", "PATHEXT", "SYSTEMROOT", "WINDIR", "COMSPEC", "TEMP", "TMP",
        "TMPDIR", "LANG", "LC_ALL", "HOME", "USERPROFILE", "HOMEDRIVE",
        "HOMEPATH", "LOCALAPPDATA", "APPDATA", "CARGO_HOME", "RUSTUP_HOME",
        "GOCACHE", "GOMODCACHE",
    }
    environment = {key: value for key, value in os.environ.items() if key.upper() in allowed}
    environment["AO_MISSION_HOME"] = str(run_root / "mission-state")
    environment["AO_BASELINE_FIXTURE_MODE"] = "credential-free"
    return environment


def _expand(argv, workspace_root, run_root, stage_root):
    values = {"{python}": sys.executable, "{workspace_root}": str(workspace_root), "{run_root}": str(run_root), "{stage_root}": str(stage_root)}
    return [values.get(item, item.replace("{stage_root}", str(stage_root)).replace("{run_root}", str(run_root)).replace("{workspace_root}", str(workspace_root))) for item in argv]


def run_workflow(fixture_path, output_path, workspace_root, baseline_manifest):
    fixture = _read_json(fixture_path)
    validate_fixture(fixture)
    validate_baseline_binding(fixture, _read_json(baseline_manifest))
    output_path = Path(output_path).resolve()
    workspace_root = Path(workspace_root).resolve()
    if output_path.exists():
        raise ValueError("output already exists")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    run_root = output_path.parent / (output_path.stem + ".run")
    if run_root.exists():
        raise ValueError("run root already exists")
    run_root.mkdir()
    records = []
    status = "pass"
    error = None
    try:
        for stage in fixture["stages"]:
            repository = workspace_root / stage["repository"]
            if not repository.is_dir() or repository.is_symlink():
                raise ValueError(f"repository missing or unsafe: {stage['repository']}")
            if _head(repository) != stage["source_commit"]:
                raise ValueError(f"repository source identity mismatch: {stage['repository']}")
            stage_root = run_root / stage["id"]
            stage_root.mkdir()
            argv = _expand(stage["argv"], workspace_root, run_root, stage_root)
            started = time.monotonic()
            completed = subprocess.run(argv, cwd=repository, env=_environment(run_root), capture_output=True, timeout=stage.get("timeout_seconds", 300), check=False)
            elapsed_ms = int((time.monotonic() - started) * 1000)
            stdout = completed.stdout[: stage["artifact"]["max_bytes"]]
            stderr = completed.stderr[: 65_536]
            if completed.returncode:
                raise RuntimeError(f"stage failed: {stage['id']} exit={completed.returncode} stderr_sha256={_sha256(stderr)}")
            if stage["artifact"]["source"] == "stdout":
                artifact = stdout
            else:
                artifact_path = (stage_root / stage["artifact"]["path"]).resolve()
                if stage_root not in artifact_path.parents or not artifact_path.is_file() or artifact_path.is_symlink():
                    raise ValueError(f"stage artifact missing or unsafe: {stage['id']}")
                if artifact_path.stat().st_size > stage["artifact"]["max_bytes"]:
                    raise ValueError(f"stage artifact exceeds bound: {stage['id']}")
                artifact = artifact_path.read_bytes()
            if stage["artifact"].get("json"):
                parsed = json.loads(artifact.decode("utf-8"))
                if not isinstance(parsed, dict):
                    raise ValueError(f"stage artifact must be a JSON object: {stage['id']}")
                if "correlation_id" in parsed and parsed["correlation_id"] != CORRELATION_ID:
                    raise ValueError(f"stage artifact correlation drift: {stage['id']}")
            if not artifact:
                raise ValueError(f"stage artifact is empty: {stage['id']}")
            if _head(repository) != stage["source_commit"]:
                raise ValueError(f"repository source drift: {stage['repository']}")
            records.append({"id": stage["id"], "repository": stage["repository"], "source_commit": stage["source_commit"], "status": "pass", "outcome": stage["outcome"], "consumes": stage["consumes"], "artifact_sha256": _sha256(artifact), "stdout_sha256": _sha256(stdout), "stderr_sha256": _sha256(stderr), "exit_code": completed.returncode, "elapsed_ms": elapsed_ms})
    except Exception as caught:
        status = "fail"
        error = str(caught)
    finally:
        shutil.rmtree(run_root)
    result = {"schema": RESULT_SCHEMA, "status": status, "correlation_id": fixture["correlation_id"], "baseline_identity": fixture["baseline_identity"], "stages": records, "authority": dict(fixture["authority"]), "cleanup": {"run_owned_processes": 0, "run_owned_listeners": 0, "temporary_root": "removed"}}
    if error:
        result["error"] = error
    body = (json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    output_path.write_bytes(body)
    if status == "pass":
        validate_result(result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workspace-root", type=Path, default=Path.cwd().parent)
    parser.add_argument("--baseline-manifest", type=Path, default=Path(__file__).parents[1] / "stack" / "development-baseline-manifest.json")
    args = parser.parse_args(argv)
    result = run_workflow(args.fixture, args.output, args.workspace_root, args.baseline_manifest)
    print(f"status={result['status']} stages={len(result['stages'])} baseline_identity={result['baseline_identity']}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
