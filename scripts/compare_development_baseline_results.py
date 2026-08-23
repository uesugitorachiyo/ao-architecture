#!/usr/bin/env python3
"""Independently rehash and compare two native AO workflow results."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import re


RESULT_SCHEMA = "ao.architecture.development-baseline-workflow-result.v1"
PARITY_SCHEMA = "ao.architecture.development-baseline-parity.v1"
PROFILE_SCHEMA = "ao.architecture.development-baseline-normalization.v1"
REQUIRED_RULES = (
    "absolute_root", "path_separator", "executable_suffix", "shell_name",
    "timestamp", "duration", "process_id", "archive_format",
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
AUTHORITY_FIELDS = (
    "safe_to_execute", "executes_work", "approves_work", "mutates_repositories",
    "provider_calls", "credential_use", "release", "publication", "deployment",
    "promotion", "compatibility_activation", "external_beta", "rsi",
)
RESULT_KEYS = {"schema", "status", "correlation_id", "baseline_identity", "normalization", "stages", "authority", "cleanup"}
STAGE_KEYS = {
    "id", "repository", "source_commit", "status", "outcome", "consumes",
    "artifact_sha256", "artifact_evidence", "stdout_sha256", "stdout_evidence",
    "stderr_sha256", "stderr_evidence", "exit_code", "elapsed_ms",
    "prepare_exit_code", "prepare_stdout_sha256", "prepare_stdout_evidence",
    "prepare_stderr_sha256", "prepare_stderr_evidence",
}
EVIDENCE_KEYS = {"encoding", "bytes", "sha256", "data"}
NORMALIZATION_KEYS = {"absolute_roots", "path_separator", "executable_suffix", "shell_names", "archive_suffixes"}
PROFILE_KEYS = {"schema", "rules", "duration_fields", "process_id_fields", "max_evidence_bytes"}
TIMESTAMP = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z")


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha256(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _strict_keys(value, expected, label, required=None):
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    unknown = set(value) - set(expected)
    missing = set(required if required is not None else expected) - set(value)
    if unknown or missing:
        raise ValueError(f"{label} keys invalid: missing={sorted(missing)} unknown={sorted(unknown)}")


def load_profile(path):
    profile = json.loads(Path(path).read_text(encoding="utf-8"))
    _strict_keys(profile, PROFILE_KEYS, "normalization profile")
    if profile["schema"] != PROFILE_SCHEMA or profile["rules"] != list(REQUIRED_RULES) or len(set(profile["rules"])) != len(REQUIRED_RULES):
        raise ValueError("normalization rules do not match the frozen allowlist")
    for name in ("duration_fields", "process_id_fields"):
        values = profile[name]
        if not isinstance(values, list) or not values or len(set(values)) != len(values) or any(not isinstance(item, str) or not item for item in values):
            raise ValueError(f"normalization profile {name} invalid")
    if not isinstance(profile["max_evidence_bytes"], int) or isinstance(profile["max_evidence_bytes"], bool) or not 1 <= profile["max_evidence_bytes"] <= 1_048_576:
        raise ValueError("normalization evidence bound invalid")
    return profile


def _absolute(value):
    return isinstance(value, str) and (value.startswith("/") or re.fullmatch(r"[A-Za-z]:[\\/].+", value) is not None)


def _validate_metadata(value):
    _strict_keys(value, NORMALIZATION_KEYS, "normalization metadata")
    roots = value["absolute_roots"]
    if not isinstance(roots, list) or not roots or len(set(roots)) != len(roots) or any(not _absolute(item) for item in roots):
        raise ValueError("normalization absolute roots invalid")
    if value["path_separator"] not in {"/", "\\"} or value["executable_suffix"] not in {"", ".exe"}:
        raise ValueError("normalization platform fields invalid")
    for name in ("shell_names", "archive_suffixes"):
        items = value[name]
        if not isinstance(items, list) or not items or len(set(items)) != len(items) or any(not isinstance(item, str) or not item for item in items):
            raise ValueError(f"normalization {name} invalid")
    return value


def normalize_value(value, key, metadata, profile):
    if isinstance(value, dict):
        return {name: normalize_value(item, name, metadata, profile) for name, item in sorted(value.items())}
    if isinstance(value, list):
        return [normalize_value(item, key, metadata, profile) for item in value]
    if key in profile["duration_fields"]:
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
            raise ValueError(f"duration field invalid: {key}")
        return "$DURATION"
    if key in profile["process_id_fields"]:
        if not isinstance(value, (int, str, list)) or isinstance(value, bool):
            raise ValueError(f"process identifier invalid: {key}")
        return "$PROCESS_ID"
    if not isinstance(value, str):
        return value
    normalized = value
    for root in sorted(metadata["absolute_roots"], key=len, reverse=True):
        normalized = normalized.replace(root, "$ROOT").replace(root.replace("\\", "/"), "$ROOT")
    if metadata["path_separator"] == "\\":
        normalized = normalized.replace("\\", "/")
    suffix = metadata["executable_suffix"]
    if suffix:
        normalized = re.sub(re.escape(suffix) + r"(?=$|[\s\"'/:,])", "", normalized, flags=re.IGNORECASE)
    for shell in sorted(metadata["shell_names"], key=len, reverse=True):
        normalized = re.sub(r"(?<![A-Za-z0-9_.-])" + re.escape(shell) + r"(?![A-Za-z0-9_.-])", "$SHELL", normalized, flags=re.IGNORECASE)
    normalized = TIMESTAMP.sub("$TIMESTAMP", normalized)
    for archive in sorted(metadata["archive_suffixes"], key=len, reverse=True):
        normalized = re.sub(re.escape(archive) + r"(?=$|[\s\"',}])", ".$ARCHIVE", normalized, flags=re.IGNORECASE)
    return normalized


def _decode_evidence(value, label, profile):
    _strict_keys(value, EVIDENCE_KEYS, label)
    if value["encoding"] != "base64" or not isinstance(value["bytes"], int) or isinstance(value["bytes"], bool) or value["bytes"] < 0 or value["bytes"] > profile["max_evidence_bytes"]:
        raise ValueError(f"{label} bound or encoding invalid")
    try:
        data = base64.b64decode(value["data"], validate=True)
    except Exception as error:
        raise ValueError(f"{label} base64 invalid") from error
    if len(data) != value["bytes"] or _sha256(data) != value["sha256"]:
        raise ValueError(f"{label} digest mismatch")
    return data


def _artifact_value(data, metadata, profile):
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("artifact evidence is not UTF-8") from error
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        value = text
    return normalize_value(value, "artifact", metadata, profile)


def _validated_semantics(document, profile):
    _strict_keys(document, RESULT_KEYS, "workflow result")
    if document["schema"] != RESULT_SCHEMA or document["status"] != "pass":
        raise ValueError("self-declared pass is not a valid terminal result")
    if re.fullmatch(r"sha256:[0-9a-f]{64}", document["baseline_identity"]) is None:
        raise ValueError("baseline identity invalid")
    if not isinstance(document["correlation_id"], str) or not document["correlation_id"]:
        raise ValueError("correlation identity invalid")
    metadata = _validate_metadata(document["normalization"])
    if set(document["authority"]) != set(AUTHORITY_FIELDS) or any(document["authority"].get(name) is not False for name in AUTHORITY_FIELDS):
        raise ValueError("authority widening detected")
    expected_cleanup = {"run_owned_processes": 0, "run_owned_listeners": 0, "temporary_root": "removed"}
    if document["cleanup"] != expected_cleanup:
        raise ValueError("cleanup is incomplete")
    stages = document["stages"]
    if not isinstance(stages, list) or len(stages) != len(REQUIRED_STAGES):
        raise ValueError("missing or extra evidence stages")
    semantic_stages = []
    for index, (stage, expected) in enumerate(zip(stages, REQUIRED_STAGES)):
        _strict_keys(stage, STAGE_KEYS, f"stage {index}", required=STAGE_KEYS - {"prepare_exit_code", "prepare_stdout_sha256", "prepare_stdout_evidence", "prepare_stderr_sha256", "prepare_stderr_evidence"})
        stage_id, repository, outcome = expected
        if (stage["id"], stage["repository"], stage["outcome"]) != expected or stage["status"] != "pass" or stage["exit_code"] != 0 or re.fullmatch(r"[0-9a-f]{40}", stage["source_commit"]) is None:
            raise ValueError(f"stage identity or terminal content invalid: {stage_id}")
        if not isinstance(stage["consumes"], list) or any(not isinstance(item, str) for item in stage["consumes"]):
            raise ValueError(f"stage producer edges invalid: {stage_id}")
        artifact = _decode_evidence(stage["artifact_evidence"], f"{stage_id} artifact", profile)
        if stage["artifact_sha256"] != _sha256(artifact):
            raise ValueError(f"{stage_id} artifact digest mismatch")
        for stream in ("stdout", "stderr"):
            data = _decode_evidence(stage[f"{stream}_evidence"], f"{stage_id} {stream}", profile)
            if stage[f"{stream}_sha256"] != _sha256(data):
                raise ValueError(f"{stage_id} {stream} digest mismatch")
        optional = set(stage) & {"prepare_exit_code", "prepare_stdout_sha256", "prepare_stdout_evidence", "prepare_stderr_sha256", "prepare_stderr_evidence"}
        if optional:
            required_prepare = {"prepare_exit_code", "prepare_stdout_sha256", "prepare_stdout_evidence", "prepare_stderr_sha256", "prepare_stderr_evidence"}
            if optional != required_prepare or stage["prepare_exit_code"] != 0:
                raise ValueError(f"{stage_id} prepare evidence incomplete")
            for stream in ("stdout", "stderr"):
                data = _decode_evidence(stage[f"prepare_{stream}_evidence"], f"{stage_id} prepare {stream}", profile)
                if stage[f"prepare_{stream}_sha256"] != _sha256(data):
                    raise ValueError(f"{stage_id} prepare {stream} digest mismatch")
        semantic_stages.append({
            "id": stage_id,
            "repository": repository,
            "source_commit": stage["source_commit"],
            "status": stage["status"],
            "outcome": outcome,
            "consumes": stage["consumes"],
            "artifact": _artifact_value(artifact, metadata, profile),
            "exit_code": stage["exit_code"],
            "elapsed_ms": normalize_value(stage["elapsed_ms"], "elapsed_ms", metadata, profile),
            "prepare_exit_code": stage.get("prepare_exit_code"),
        })
    return {
        "schema": document["schema"],
        "status": document["status"],
        "correlation_id": document["correlation_id"],
        "baseline_identity": document["baseline_identity"],
        "stages": semantic_stages,
        "authority": document["authority"],
        "cleanup": document["cleanup"],
    }


def compare_documents(macos, windows, profile, macos_digest, windows_digest):
    if macos_digest == windows_digest:
        raise ValueError("native inputs must be distinct")
    left = _validated_semantics(macos, profile)
    right = _validated_semantics(windows, profile)
    if left["baseline_identity"] != right["baseline_identity"]:
        raise ValueError("baseline manifest identity mismatch")
    if left["correlation_id"] != right["correlation_id"]:
        raise ValueError("correlation identity mismatch")
    left_bytes = _canonical(left)
    right_bytes = _canonical(right)
    if left_bytes != right_bytes:
        raise ValueError("semantic parity mismatch after frozen normalization")
    profile_digest = _sha256(_canonical(profile))
    normalized_digest = _sha256(left_bytes)
    return {
        "schema": PARITY_SCHEMA,
        "parity": "pass",
        "baseline_identity": left["baseline_identity"],
        "correlation_id": left["correlation_id"],
        "normalization_profile_sha256": profile_digest,
        "inputs": {"macos_sha256": macos_digest, "windows_sha256": windows_digest},
        "normalized_result_sha256": normalized_digest,
        "differences": [],
        "authority": {name: False for name in AUTHORITY_FIELDS},
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--macos", type=Path, required=True)
    parser.add_argument("--windows", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--profile", type=Path, default=Path(__file__).parents[1] / "stack" / "development-baseline-normalization-v1.json")
    args = parser.parse_args(argv)
    if args.output.exists():
        raise ValueError("output already exists")
    macos_bytes = args.macos.read_bytes()
    windows_bytes = args.windows.read_bytes()
    verdict = compare_documents(json.loads(macos_bytes), json.loads(windows_bytes), load_profile(args.profile), _sha256(macos_bytes), _sha256(windows_bytes))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(json.dumps(verdict, sort_keys=True, indent=2).encode("utf-8") + b"\n")
    print(f"parity={verdict['parity']} baseline_identity={verdict['baseline_identity']} differences=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
