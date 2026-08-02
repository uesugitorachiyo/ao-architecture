#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import stat
import sys
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LAYOUT = ROOT / "docs" / "agent-instructions" / "layout-v1.json"
DEFAULT_REGISTRY = ROOT / "docs" / "quality-gates" / "registry-v1.json"
MANIFEST_NAME = "ao-quality-gates.json"
MANIFEST_SCHEMA = "ao.quality-gates.v1"
REGISTRY_SCHEMA = "ao.stack.quality-gate-registry.v1"
MAX_JSON_BYTES = 256 * 1024
ACTIVE_LIFECYCLES = {"active_hosted", "active_local_only"}
ADOPTION_STATUSES = {"planned", "adopted"}
LEVEL_SNAPSHOTS = {
    "commit": "staged_tree",
    "push": "outgoing_commits",
    "full": "source_head",
}
FAST_LEVEL_LIMITS = {"commit": 10, "push": 120}
SHELL_EVALUATORS = {"sh", "bash", "zsh", "dash", "cmd", "cmd.exe", "powershell", "pwsh"}
SHELL_EVAL_FLAGS = {"-c", "/c", "-command", "--command"}


class StrictJSONError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def issue(code: str, message: str, repository: str | None = None) -> dict[str, str]:
    result = {"code": code, "message": message}
    if repository:
        result["repository"] = repository
    return result


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    document: dict[str, Any] = {}
    for key, value in pairs:
        if key in document:
            raise StrictJSONError("JSON_DUPLICATE_KEY", f"duplicate key: {key}")
        document[key] = value
    return document


def strict_load(path: Path, *, kind: str) -> Any:
    try:
        info = path.lstat()
    except FileNotFoundError as exc:
        raise StrictJSONError(f"{kind}_MISSING", f"missing file: {path}") from exc
    if stat.S_ISLNK(info.st_mode):
        raise StrictJSONError(f"{kind}_SYMLINK", f"symlink is not allowed: {path}")
    if not stat.S_ISREG(info.st_mode):
        raise StrictJSONError(f"{kind}_REGULAR_FILE_REQUIRED", f"regular file required: {path}")
    if info.st_size > MAX_JSON_BYTES:
        raise StrictJSONError(f"{kind}_SIZE_LIMIT", f"file exceeds {MAX_JSON_BYTES} bytes: {path}")
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise StrictJSONError(f"{kind}_READ_FAILED", f"cannot read UTF-8 file: {path}: {exc}") from exc
    try:
        return json.loads(raw, object_pairs_hook=_reject_duplicate_pairs)
    except StrictJSONError as exc:
        raise StrictJSONError(f"{kind}_DUPLICATE_KEY", str(exc)) from exc
    except json.JSONDecodeError as exc:
        raise StrictJSONError(f"{kind}_MALFORMED_JSON", f"invalid JSON: {path}: {exc}") from exc


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _safe_relative_pattern(value: Any) -> bool:
    if not _is_non_empty_string(value) or "\x00" in value or "\\" in value:
        return False
    if value.startswith("/") or (len(value) >= 2 and value[1] == ":"):
        return False
    return ".." not in PurePosixPath(value).parts


def _check_exact_fields(
    document: dict[str, Any],
    allowed: set[str],
    required: set[str],
    prefix: str,
    errors: list[dict[str, str]],
    repository: str,
) -> None:
    for field in sorted(required - document.keys()):
        errors.append(issue(f"{prefix}_FIELD_REQUIRED", f"missing required field: {field}", repository))
    for field in sorted(document.keys() - allowed):
        errors.append(issue(f"{prefix}_UNKNOWN_FIELD", f"unknown field: {field}", repository))


def validate_manifest(document: Any, expected_repository: str, expected_lifecycle: str) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if not isinstance(document, dict):
        return [issue("MANIFEST_OBJECT_REQUIRED", "manifest must be an object", expected_repository)]
    _check_exact_fields(
        document,
        {
            "schema_version",
            "repository",
            "lifecycle",
            "supported_platforms",
            "required_tools",
            "generated_paths",
            "protected_paths",
            "compatibility",
            "evidence",
            "levels",
        },
        {
            "schema_version",
            "repository",
            "lifecycle",
            "supported_platforms",
            "required_tools",
            "generated_paths",
            "protected_paths",
            "compatibility",
            "evidence",
            "levels",
        },
        "MANIFEST",
        errors,
        expected_repository,
    )
    if document.get("schema_version") != MANIFEST_SCHEMA:
        errors.append(issue("MANIFEST_SCHEMA_UNSUPPORTED", f"schema_version must be {MANIFEST_SCHEMA}", expected_repository))
    if document.get("repository") != expected_repository:
        errors.append(issue("MANIFEST_REPOSITORY_MISMATCH", "repository identity does not match registry", expected_repository))
    if document.get("lifecycle") != expected_lifecycle:
        errors.append(issue("MANIFEST_LIFECYCLE_MISMATCH", "lifecycle does not match Architecture layout", expected_repository))

    platforms = document.get("supported_platforms")
    if not isinstance(platforms, list) or not platforms or any(item not in {"linux", "macos", "windows"} for item in platforms) or len(platforms) != len(set(platforms)):
        errors.append(issue("MANIFEST_PLATFORMS_INVALID", "supported_platforms must be a unique non-empty supported platform list", expected_repository))
    tools = document.get("required_tools")
    if not isinstance(tools, list) or not tools or any(not _is_non_empty_string(item) for item in tools) or len(tools) != len(set(tools)):
        errors.append(issue("MANIFEST_TOOLS_INVALID", "required_tools must be a unique non-empty string list", expected_repository))

    for field in ("generated_paths", "protected_paths"):
        values = document.get(field)
        if not isinstance(values, list) or any(not _safe_relative_pattern(value) for value in values):
            errors.append(issue("PATH_PATTERN_UNSAFE", f"{field} must contain only safe repository-relative patterns", expected_repository))

    compatibility = document.get("compatibility")
    if not isinstance(compatibility, dict):
        errors.append(issue("MANIFEST_COMPATIBILITY_REQUIRED", "compatibility must be an object", expected_repository))
    else:
        _check_exact_fields(
            compatibility,
            {"minimum_consumer_version", "owner"},
            {"minimum_consumer_version", "owner"},
            "COMPATIBILITY",
            errors,
            expected_repository,
        )
        if compatibility.get("minimum_consumer_version") != "1.0.0":
            errors.append(issue("MANIFEST_COMPATIBILITY_UNSUPPORTED", "minimum_consumer_version must be 1.0.0", expected_repository))
        if compatibility.get("owner") != expected_repository:
            errors.append(issue("MANIFEST_COMMAND_OWNER_MISMATCH", "compatibility owner must be the source repository", expected_repository))

    evidence = document.get("evidence")
    if not isinstance(evidence, dict):
        errors.append(issue("MANIFEST_EVIDENCE_REQUIRED", "evidence must be an object", expected_repository))
    else:
        _check_exact_fields(
            evidence,
            {"public_safe", "local_artifact_root", "maximum_result_bytes"},
            {"public_safe", "local_artifact_root", "maximum_result_bytes"},
            "EVIDENCE",
            errors,
            expected_repository,
        )
        if evidence.get("public_safe") is not True:
            errors.append(issue("EVIDENCE_PUBLIC_SAFE_REQUIRED", "public_safe must be true", expected_repository))
        if not _safe_relative_pattern(evidence.get("local_artifact_root")):
            errors.append(issue("PATH_PATTERN_UNSAFE", "local_artifact_root must be repository-relative", expected_repository))
        maximum_result_bytes = evidence.get("maximum_result_bytes")
        if not isinstance(maximum_result_bytes, int) or isinstance(maximum_result_bytes, bool) or not 4096 <= maximum_result_bytes <= 1024 * 1024:
            errors.append(issue("EVIDENCE_SIZE_LIMIT_INVALID", "maximum_result_bytes must be between 4096 and 1048576", expected_repository))

    levels = document.get("levels")
    if not isinstance(levels, dict):
        return errors + [issue("MANIFEST_LEVELS_REQUIRED", "levels must be an object", expected_repository)]
    if set(levels) != set(LEVEL_SNAPSHOTS):
        errors.append(issue("MANIFEST_LEVEL_SET_INVALID", "levels must contain exactly commit, push, and full", expected_repository))
    for level_name, expected_snapshot in LEVEL_SNAPSHOTS.items():
        level = levels.get(level_name)
        if not isinstance(level, dict):
            errors.append(issue("LEVEL_OBJECT_REQUIRED", f"{level_name} must be an object", expected_repository))
            continue
        _check_exact_fields(
            level,
            {"snapshot", "maximum_duration_seconds", "network_allowed", "mutates_source", "steps"},
            {"snapshot", "maximum_duration_seconds", "network_allowed", "mutates_source", "steps"},
            "LEVEL",
            errors,
            expected_repository,
        )
        if level.get("snapshot") != expected_snapshot:
            errors.append(issue("LEVEL_SNAPSHOT_MISMATCH", f"{level_name} snapshot must be {expected_snapshot}", expected_repository))
        maximum_duration = level.get("maximum_duration_seconds")
        if not isinstance(maximum_duration, int) or isinstance(maximum_duration, bool) or maximum_duration <= 0:
            errors.append(issue("LEVEL_DURATION_INVALID", f"{level_name} maximum_duration_seconds must be positive", expected_repository))
            maximum_duration = 0
        if level_name in FAST_LEVEL_LIMITS and maximum_duration > FAST_LEVEL_LIMITS[level_name]:
            errors.append(issue("FAST_GATE_DURATION_EXCEEDED", f"{level_name} exceeds its duration limit", expected_repository))
        if level_name in FAST_LEVEL_LIMITS and level.get("network_allowed") is not False:
            errors.append(issue("FAST_GATE_NETWORK_FORBIDDEN", f"{level_name} must disable network", expected_repository))
        if level_name in FAST_LEVEL_LIMITS and level.get("mutates_source") is not False:
            errors.append(issue("FAST_GATE_MUTATION_FORBIDDEN", f"{level_name} must not mutate source", expected_repository))
        if not isinstance(level.get("network_allowed"), bool) or not isinstance(level.get("mutates_source"), bool):
            errors.append(issue("LEVEL_POLICY_BOOLEAN_REQUIRED", f"{level_name} policy flags must be booleans", expected_repository))
        steps = level.get("steps")
        if not isinstance(steps, list) or not steps:
            errors.append(issue("LEVEL_STEPS_REQUIRED", f"{level_name} steps must be a non-empty array", expected_repository))
            continue
        step_ids: list[str] = []
        for index, step in enumerate(steps):
            if not isinstance(step, dict):
                errors.append(issue("STEP_OBJECT_REQUIRED", f"{level_name}.steps[{index}] must be an object", expected_repository))
                continue
            _check_exact_fields(
                step,
                {"id", "argv", "timeout_seconds", "path_triggers"},
                {"id", "argv", "timeout_seconds", "path_triggers"},
                "STEP",
                errors,
                expected_repository,
            )
            step_id = step.get("id")
            if not _is_non_empty_string(step_id):
                errors.append(issue("STEP_ID_REQUIRED", f"{level_name}.steps[{index}].id is required", expected_repository))
            else:
                step_ids.append(step_id)
            argv = step.get("argv")
            if not isinstance(argv, list) or not argv or any(not _is_non_empty_string(arg) for arg in argv):
                errors.append(issue("STEP_ARGV_REQUIRED", f"{level_name}.steps[{index}].argv must be a non-empty string array", expected_repository))
            elif Path(argv[0]).name.lower() in SHELL_EVALUATORS and len(argv) > 1 and argv[1].lower() in SHELL_EVAL_FLAGS:
                errors.append(issue("SHELL_EVALUATION_FORBIDDEN", f"{level_name}.steps[{index}] requests shell evaluation", expected_repository))
            timeout = step.get("timeout_seconds")
            if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0 or (maximum_duration and timeout > maximum_duration):
                errors.append(issue("STEP_TIMEOUT_INVALID", f"{level_name}.steps[{index}] timeout exceeds the level bound", expected_repository))
            triggers = step.get("path_triggers")
            if not isinstance(triggers, list) or not triggers or any(not _safe_relative_pattern(value) for value in triggers):
                errors.append(issue("PATH_PATTERN_UNSAFE", f"{level_name}.steps[{index}] has unsafe path triggers", expected_repository))
        if len(step_ids) != len(set(step_ids)):
            errors.append(issue("STEP_ID_DUPLICATE", f"{level_name} step ids must be unique", expected_repository))
    return errors


def validate_registry(
    *,
    workspace_root: Path,
    layout_path: Path = DEFAULT_LAYOUT,
    registry_path: Path = DEFAULT_REGISTRY,
    repository: str | None = None,
    repository_root: Path | None = None,
    require_adopted: bool = False,
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    try:
        layout = strict_load(layout_path, kind="LAYOUT")
        registry = strict_load(registry_path, kind="REGISTRY")
    except StrictJSONError as exc:
        return {"status": "failed", "repository_count": 0, "adopted_count": 0, "errors": [issue(exc.code, str(exc))]}
    if not isinstance(layout, dict) or not isinstance(layout.get("repositories"), list):
        return {"status": "failed", "repository_count": 0, "adopted_count": 0, "errors": [issue("LAYOUT_INVALID", "layout repositories must be an array")]}
    if not isinstance(registry, dict):
        return {"status": "failed", "repository_count": 0, "adopted_count": 0, "errors": [issue("REGISTRY_OBJECT_REQUIRED", "registry must be an object")]}
    if registry.get("schema_version") != REGISTRY_SCHEMA:
        errors.append(issue("REGISTRY_SCHEMA_UNSUPPORTED", f"schema_version must be {REGISTRY_SCHEMA}"))
    if registry.get("manifest_schema_version") != MANIFEST_SCHEMA:
        errors.append(issue("REGISTRY_MANIFEST_SCHEMA_MISMATCH", f"manifest_schema_version must be {MANIFEST_SCHEMA}"))
    if registry.get("lifecycle_source") != "docs/agent-instructions/layout-v1.json":
        errors.append(issue("REGISTRY_LIFECYCLE_SOURCE_MISMATCH", "lifecycle_source must identify the Architecture layout"))
    entries = registry.get("repositories")
    if not isinstance(entries, list):
        entries = []
        errors.append(issue("REGISTRY_REPOSITORIES_REQUIRED", "repositories must be an array"))

    expected = {
        item.get("name"): item.get("lifecycle")
        for item in layout["repositories"]
        if isinstance(item, dict) and item.get("lifecycle") in ACTIVE_LIFECYCLES and _is_non_empty_string(item.get("name"))
    }
    by_name: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(issue("REGISTRY_ENTRY_OBJECT_REQUIRED", f"repositories[{index}] must be an object"))
            continue
        name = entry.get("repository")
        if not _is_non_empty_string(name):
            errors.append(issue("REGISTRY_REPOSITORY_REQUIRED", f"repositories[{index}].repository is required"))
            continue
        if name in by_name:
            errors.append(issue("REGISTRY_DUPLICATE_REPOSITORY", f"duplicate repository: {name}", name))
        by_name[name] = entry
        if set(entry) != {"repository", "lifecycle", "manifest_path", "adoption_status", "command_owner"}:
            errors.append(issue("REGISTRY_ENTRY_FIELDS_INVALID", "registry entry fields are incomplete or unknown", name))
        if name not in expected:
            errors.append(issue("REGISTRY_UNKNOWN_REPOSITORY", "repository is not active in the lifecycle layout", name))
        elif entry.get("lifecycle") != expected[name]:
            errors.append(issue("REGISTRY_LIFECYCLE_MISMATCH", "registry lifecycle differs from Architecture layout", name))
        if entry.get("manifest_path") != MANIFEST_NAME:
            errors.append(issue("REGISTRY_MANIFEST_PATH_INVALID", f"manifest_path must be {MANIFEST_NAME}", name))
        if entry.get("adoption_status") not in ADOPTION_STATUSES:
            errors.append(issue("REGISTRY_ADOPTION_STATUS_INVALID", "adoption_status must be planned or adopted", name))
        if entry.get("command_owner") != name:
            errors.append(issue("REGISTRY_COMMAND_OWNER_MISMATCH", "command_owner must be the source repository", name))
    for name in sorted(set(expected) - set(by_name)):
        errors.append(issue("REGISTRY_MISSING_REPOSITORY", "active lifecycle repository is absent from registry", name))
    for name in sorted(set(by_name) - set(expected)):
        errors.append(issue("REGISTRY_EXTRA_REPOSITORY", "registry contains a non-active repository", name))
    if repository and repository not in expected:
        errors.append(issue("REGISTRY_REPOSITORY_SELECTOR_INVALID", "selected repository is not active", repository))
    if repository_root is not None and repository is None:
        errors.append(issue("REGISTRY_REPOSITORY_ROOT_UNSCOPED", "--repository-root requires --repository"))

    selected = [repository] if repository else sorted(expected)
    adopted_count = sum(1 for entry in entries if isinstance(entry, dict) and entry.get("adoption_status") == "adopted")
    for name in selected:
        entry = by_name.get(name)
        if entry is None:
            continue
        if require_adopted and entry.get("adoption_status") != "adopted":
            errors.append(issue("REGISTRY_ADOPTION_INCOMPLETE", "repository manifest adoption is incomplete", name))
        root = repository_root if repository == name and repository_root is not None else workspace_root / name
        manifest_path = root / MANIFEST_NAME
        manifest_exists = manifest_path.exists() or manifest_path.is_symlink()
        if not manifest_exists:
            if entry.get("adoption_status") == "adopted":
                errors.append(issue("MANIFEST_REQUIRED", f"adopted repository is missing {MANIFEST_NAME}", name))
            continue
        try:
            manifest = strict_load(manifest_path, kind="MANIFEST")
        except StrictJSONError as exc:
            errors.append(issue(exc.code, str(exc), name))
            continue
        errors.extend(validate_manifest(manifest, name, expected[name]))

    return {
        "schema": "ao.architecture.quality-gate-registry-validation.v1",
        "status": "passed" if not errors else "failed",
        "repository_count": len(expected),
        "adopted_count": adopted_count,
        "selected_repositories": selected,
        "errors": errors,
        "schedules_work": False,
        "executes_work": False,
        "approves_work": False,
        "mutates_repositories": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AO Stack source-owned quality gate manifests")
    parser.add_argument("--workspace-root", type=Path, default=ROOT.parent)
    parser.add_argument("--layout", type=Path, default=DEFAULT_LAYOUT)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--repository")
    parser.add_argument("--repository-root", type=Path)
    parser.add_argument("--require-adopted", action="store_true")
    args = parser.parse_args()
    result = validate_registry(
        workspace_root=args.workspace_root,
        layout_path=args.layout,
        registry_path=args.registry,
        repository=args.repository,
        repository_root=args.repository_root,
        require_adopted=args.require_adopted,
    )
    if result["status"] != "passed":
        for error in result["errors"]:
            repository = f" repository={error['repository']}" if error.get("repository") else ""
            print(f"verify_quality_gate_registry.py: [{error['code']}]{repository} {error['message']}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
