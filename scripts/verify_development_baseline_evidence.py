#!/usr/bin/env python3
"""Verify and close a complete AO development-baseline evidence package."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re


SCHEMA = "ao.architecture.development-baseline-evidence-closure.v1"
MAX_FILE_BYTES = 1_048_576
MAX_FILES = 500
AUTHORITY_FIELDS = (
    "safe_to_execute", "executes_work", "approves_work", "mutates_repositories",
    "provider_calls", "credential_use", "release", "publication", "deployment",
    "promotion", "compatibility_activation", "external_beta", "rsi",
)
REPOSITORIES = (
    "ao-architecture", "ao-arena", "ao-atlas", "ao-blueprint", "ao-command",
    "ao-covenant", "ao-crucible", "ao-forge", "ao-foundry", "ao-mission",
    "ao-promoter", "ao-sentinel", "ao2", "ao2-control-plane",
)
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


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(65_536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json(path):
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid JSON evidence: {path.name}") from error
    if not isinstance(value, dict):
        raise ValueError(f"evidence must be a JSON object: {path.name}")
    return value


def validate_relative_paths(paths):
    seen = set()
    for raw in paths:
        if not isinstance(raw, str) or not raw or "\\" in raw or re.match(r"^[A-Za-z]:", raw):
            raise ValueError("evidence paths must be safe relative POSIX paths")
        path = PurePosixPath(raw)
        if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
            raise ValueError("evidence paths must be safe relative POSIX paths")
        folded = raw.casefold()
        if folded in seen:
            raise ValueError("duplicate case-folded evidence path")
        seen.add(folded)


def _authority(value, label):
    if not isinstance(value, dict) or set(value) != set(AUTHORITY_FIELDS) or any(value.get(name) is not False for name in AUTHORITY_FIELDS):
        raise ValueError(f"unsafe authority in {label}")


def _identity(value, source_commit, baseline_identity, label, commit_field="controller_source_commit"):
    if value.get("status") != "pass" or value.get("baseline_identity") != baseline_identity:
        raise ValueError(f"baseline identity or status mismatch in {label}")
    if value.get(commit_field) != source_commit:
        raise ValueError(f"source identity mismatch in {label}")


def verify_evidence(root, source_commit, baseline_identity):
    root = Path(root)
    if not root.is_dir() or root.is_symlink():
        raise ValueError("evidence root is missing or unsafe")
    if re.fullmatch(r"[0-9a-f]{40}", source_commit) is None or re.fullmatch(r"sha256:[0-9a-f]{64}", baseline_identity) is None:
        raise ValueError("source or baseline identity invalid")
    files = sorted((path for path in root.rglob("*") if path.is_file()), key=lambda path: path.relative_to(root).as_posix())
    if len(files) > MAX_FILES:
        raise ValueError("evidence file count exceeds bound")
    if any(path.is_symlink() for path in files):
        raise ValueError("evidence contains a linked file")
    relative = [path.relative_to(root).as_posix() for path in files]
    validate_relative_paths(relative)
    inventory = []
    for path, name in zip(files, relative):
        size = path.stat().st_size
        if size > MAX_FILE_BYTES:
            raise ValueError(f"evidence file size exceeds bound: {name}")
        inventory.append({"path": name, "bytes": size, "sha256": _sha256(path)})

    hosts = [path for path in files if path.name.endswith("-host.json")]
    gates = [path for path in files if path.name.endswith("-gates.json")]
    workflows = [path for path in files if path.name.endswith("-workflow.json")]
    cleanups = [path for path in files if path.name.endswith("-cleanup.json")]
    rehashes = [path for path in files if path.name.endswith("-rehash.json")]
    parities = [path for path in files if path.name == "parity.json"]
    classified = set(hosts + gates + workflows + cleanups + rehashes + parities)
    logs = [path for path in files if path.suffix == ".log" and "gates" in path.relative_to(root).parts]
    classified.update(logs)
    extras = [path for path in files if path not in classified]
    if extras:
        raise ValueError(f"extra unclassified evidence: {extras[0].name}")
    expected_counts = (len(hosts), len(gates), len(workflows), len(cleanups), len(rehashes), len(parities))
    if expected_counts != (2, 2, 2, 2, 1, 1):
        raise ValueError(f"missing or extra required evidence sets: {expected_counts}")
    for path in hosts + gates + workflows + cleanups + rehashes:
        if source_commit not in path.name:
            raise ValueError(f"source identity missing from evidence name: {path.name}")

    host_values = [_json(path) for path in hosts]
    platforms = {}
    repository_sets = []
    for value in host_values:
        _identity(value, source_commit, baseline_identity, "host")
        _authority(value.get("authority"), "host")
        platform = value.get("platform")
        architecture = value.get("architecture")
        if (platform, architecture) not in {("macos", "arm64"), ("windows", "amd64")} or platform in platforms:
            raise ValueError("wrong or duplicate native runner result")
        platforms[platform] = value
        repositories = value.get("repositories")
        if not isinstance(repositories, list) or len(repositories) != 14:
            raise ValueError("host repository set is incomplete")
        identities = sorted((item.get("repository"), item.get("commit")) for item in repositories)
        if [name for name, _ in identities] != sorted(REPOSITORIES) or any(item.get("clean") is not True or item.get("detached") is not True or item.get("submodules_clean") is not True for item in repositories):
            raise ValueError("host repository set or state mismatch")
        repository_sets.append(identities)
    if repository_sets[0] != repository_sets[1]:
        raise ValueError("native repository sets disagree")

    for path in gates:
        value = _json(path)
        _identity(value, source_commit, baseline_identity, "gate result")
        _authority(value.get("authority"), "gate result")
        if value.get("declared_gate_count") != 59 or value.get("completed_gate_count") != 59:
            raise ValueError("gate result is incomplete")

    workflow_digests = {}
    for path in workflows:
        value = _json(path)
        if value.get("status") != "pass" or value.get("baseline_identity") != baseline_identity:
            raise ValueError("baseline workflow identity mismatch")
        _authority(value.get("authority"), "workflow")
        stages = value.get("stages")
        if not isinstance(stages, list) or [(item.get("id"), item.get("repository"), item.get("outcome")) for item in stages] != list(REQUIRED_STAGES) or any(item.get("status") != "pass" for item in stages):
            raise ValueError("workflow stage set is incomplete")
        cleanup = value.get("cleanup")
        if cleanup != {"run_owned_processes": 0, "run_owned_listeners": 0, "temporary_root": "removed"}:
            raise ValueError("workflow residue detected")
        platform = "windows" if path.name.startswith("windows-") else "macos" if path.name.startswith("macos-") else None
        if not platform or platform in workflow_digests:
            raise ValueError("wrong or duplicate workflow runner")
        workflow_digests[platform] = "sha256:" + _sha256(path)

    cleanup_platforms = set()
    for path in cleanups:
        value = _json(path)
        if value.get("cleanup_status") != "root_absent" or value.get("source_commit") != source_commit or value.get("platform") not in {"macos-26", "windows-2025"}:
            raise ValueError("wrong runner or cleanup residue")
        cleanup_platforms.add(value["platform"])
    if cleanup_platforms != {"macos-26", "windows-2025"}:
        raise ValueError("wrong or duplicate cleanup runner")

    rehash = _json(rehashes[0])
    if rehash.get("schema") != "ao.architecture.development-baseline-rehash.v1" or rehash.get("status") != "pass" or rehash.get("source_commit") != source_commit or rehash.get("baseline_identity") != baseline_identity:
        raise ValueError("rehash identity mismatch")
    for field in ("missing", "extra", "size_mismatches", "digest_mismatches", "gate_log_mismatches"):
        if rehash.get(field) != 0:
            raise ValueError("rehash reports a size or digest mismatch")

    parity = _json(parities[0])
    if parity.get("schema") != "ao.architecture.development-baseline-parity.v1" or parity.get("parity") != "pass" or parity.get("baseline_identity") != baseline_identity or parity.get("differences") != []:
        raise ValueError("parity verdict is incomplete")
    _authority(parity.get("authority"), "parity")
    if parity.get("inputs") != {"macos_sha256": workflow_digests["macos"], "windows_sha256": workflow_digests["windows"]}:
        raise ValueError("parity input digest mismatch")

    return {
        "schema": SCHEMA,
        "status": "pass",
        "source_commit": source_commit,
        "baseline_identity": baseline_identity,
        "correlation_id": parity.get("correlation_id"),
        "counts": {"files": len(files), "host_results": 2, "gate_results": 2, "workflow_results": 2, "cleanup_results": 2, "rehash_results": 1, "parity_results": 1},
        "inventory": inventory,
        "missing": 0,
        "extra": 0,
        "size_mismatches": 0,
        "digest_mismatches": 0,
        "authority": {name: False for name in AUTHORITY_FIELDS},
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--baseline-identity", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.output.exists():
        raise ValueError("output already exists")
    result = verify_evidence(args.root, args.source_commit, args.baseline_identity)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(f"status=pass files={result['counts']['files']} missing=0 extra=0 digest_mismatches=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
