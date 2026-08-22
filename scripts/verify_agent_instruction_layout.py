#!/usr/bin/env python3
"""Validate the AO Stack repository instruction layout without mutation or network access."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "docs" / "agent-instructions" / "layout-v1.json"
EXACT_CLAUDE_BYTES = b"@AGENTS.md\n"

EXPECTED_REPOSITORIES = {
    "ao-architecture",
    "ao-arena",
    "ao-atlas",
    "ao-blueprint",
    "ao-command",
    "ao-conductor",
    "ao-control-plane",
    "ao-covenant",
    "ao-covenant-stub-20260617",
    "ao-crucible",
    "ao-forge",
    "ao-foundry",
    "ao-hardening-runner",
    "ao-mission",
    "ao-next",
    "ao-operator",
    "ao-promoter",
    "ao-runtime",
    "ao-sentinel",
    "ao-stack-evaluation",
    "ao2",
    "ao2-control-plane",
}
LIFECYCLES = {
    "active_hosted",
    "active_local_only",
    "archived_hosted",
    "excluded_legacy_hosted",
    "excluded_local_stub",
}
LEGACY_HOSTED_REPOSITORIES = {
    "ao-conductor",
    "ao-control-plane",
    "ao-operator",
    "ao-runtime",
}
TOP_LEVEL_FIELDS = {"schema_version", "repositories"}
REPOSITORY_FIELDS = {
    "name",
    "lifecycle",
    "remote",
    "required_root_files",
    "allowed_nested_scopes",
    "exclusion_reason",
    "content_sha256",
    "expected_head",
}
DISCOVERY_EXCLUDED_NAMES = {
    ".cache",
    ".git",
    ".mypy_cache",
    ".nox",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "evidence",
    "generated",
    "node_modules",
    "target",
    "vendor",
    "venv",
}
USER_PATH_PATTERNS = (
    re.compile(r"/Users/[^/\s]+/"),
    re.compile(r"/home/[^/\s]+/"),
    re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+\\"),
)
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\b" + "gh" + r"p_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\b" + "github_" + r"pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"(?i)\bauthorization\s*:\s*bearer\s+[A-Za-z0-9._~+/=-]{16,}"),
    re.compile(
        r"(?i)\b(?:api[_ -]?key|access[_ -]?token|password|client[_ -]?secret)"
        r"\s*[:=]\s*[\"']?[A-Za-z0-9._~+/=-]{16,}"
    ),
)


class ManifestError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ManifestError("MANIFEST_DUPLICATE_KEY", f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ManifestError("MANIFEST_UNREADABLE", f"cannot read manifest: {exc}") from exc
    try:
        document = json.loads(text, object_pairs_hook=_strict_object)
    except ManifestError:
        raise
    except json.JSONDecodeError as exc:
        raise ManifestError(
            "MANIFEST_MALFORMED",
            f"malformed JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}",
        ) from exc
    if not isinstance(document, dict):
        raise ManifestError("MANIFEST_MALFORMED", "manifest root must be a JSON object")
    return document


def content_fingerprint(root: Path) -> str:
    """Hash every non-.git file, symlink target, path, kind, and size deterministically."""
    records: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if ".git" in relative.parts:
            continue
        mode = path.lstat().st_mode
        if stat.S_ISDIR(mode):
            continue
        if stat.S_ISLNK(mode):
            data = os.readlink(path).encode("utf-8")
            kind = "symlink"
        else:
            data = path.read_bytes()
            kind = "file"
        records.append(
            {
                "path": relative.as_posix(),
                "kind": kind,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    aggregate = hashlib.sha256()
    for record in records:
        aggregate.update(json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        aggregate.update(b"\n")
    return aggregate.hexdigest()


def conflict(
    code: str,
    message: str,
    *,
    repository: str | None = None,
    path: str | None = None,
) -> dict[str, object]:
    return {
        "code": code,
        "message": message,
        "path": path,
        "repository": repository,
    }


def _is_absolute_manifest_path(value: str) -> bool:
    return PurePosixPath(value).is_absolute() or bool(re.match(r"^[A-Za-z]:[\\/]", value))


def _is_unsafe_manifest_path(value: str) -> bool:
    if not value or "\\" in value:
        return True
    parts = PurePosixPath(value).parts
    return any(part in {"", ".", ".."} for part in parts)


def validate_manifest(document: dict[str, Any]) -> list[dict[str, object]]:
    conflicts: list[dict[str, object]] = []
    unknown_top = sorted(set(document) - TOP_LEVEL_FIELDS)
    for field in unknown_top:
        conflicts.append(conflict("MANIFEST_UNKNOWN_FIELD", f"unknown top-level field: {field}", path=field))
    if document.get("schema_version") != "1.0.0":
        conflicts.append(conflict("MANIFEST_SCHEMA_VERSION", "schema_version must equal 1.0.0"))
    entries = document.get("repositories")
    if not isinstance(entries, list):
        conflicts.append(conflict("MANIFEST_MALFORMED", "repositories must be an array"))
        return conflicts

    seen: set[str] = set()
    names: set[str] = set()
    for index, entry in enumerate(entries):
        entry_path = f"repositories[{index}]"
        if not isinstance(entry, dict):
            conflicts.append(conflict("MANIFEST_MALFORMED", "repository entry must be an object", path=entry_path))
            continue
        name = entry.get("name")
        repository = name if isinstance(name, str) else None
        unknown_fields = sorted(set(entry) - REPOSITORY_FIELDS)
        for field in unknown_fields:
            conflicts.append(
                conflict(
                    "MANIFEST_UNKNOWN_FIELD",
                    f"unknown repository field: {field}",
                    repository=repository,
                    path=f"{entry_path}.{field}",
                )
            )
        if not isinstance(name, str) or not name:
            conflicts.append(conflict("MANIFEST_MALFORMED", "repository name must be a non-empty string", path=entry_path))
            continue
        if _is_absolute_manifest_path(name):
            conflicts.append(conflict("MANIFEST_ABSOLUTE_PATH", "repository name must be relative", repository=name, path=name))
        elif _is_unsafe_manifest_path(name) or "/" in name:
            conflicts.append(conflict("MANIFEST_UNSAFE_PATH", "repository name is not a safe single path component", repository=name, path=name))
        if name in seen:
            conflicts.append(conflict("MANIFEST_DUPLICATE_REPOSITORY", "repository name appears more than once", repository=name))
        seen.add(name)
        names.add(name)

        lifecycle = entry.get("lifecycle")
        if lifecycle not in LIFECYCLES:
            conflicts.append(
                conflict(
                    "MANIFEST_UNKNOWN_LIFECYCLE",
                    f"unknown lifecycle state: {lifecycle!r}",
                    repository=name,
                )
            )
        if (name in LEGACY_HOSTED_REPOSITORIES) != (lifecycle == "excluded_legacy_hosted"):
            conflicts.append(
                conflict(
                    "MANIFEST_LIFECYCLE_CLASSIFICATION",
                    "excluded_legacy_hosted is reserved for the four named legacy repositories outside the maintained AO Stack",
                    repository=name,
                )
            )
        expected_remote = "none" if lifecycle in {"active_local_only", "excluded_local_stub"} else "hosted"
        if entry.get("remote") not in {"hosted", "none"} or (
            lifecycle in LIFECYCLES and entry.get("remote") != expected_remote
        ):
            conflicts.append(
                conflict(
                    "MANIFEST_REMOTE_EXPECTATION",
                    f"remote must equal {expected_remote!r} for lifecycle {lifecycle!r}",
                    repository=name,
                )
            )

        required = entry.get("required_root_files")
        expected_required = (
            []
            if lifecycle in {"excluded_local_stub", "excluded_legacy_hosted"}
            else ["AGENTS.md", "CLAUDE.md"]
        )
        if required != expected_required:
            conflicts.append(
                conflict(
                    "MANIFEST_REQUIRED_ROOT_FILES",
                    f"required_root_files must equal {expected_required!r}",
                    repository=name,
                )
            )

        scopes = entry.get("allowed_nested_scopes")
        if not isinstance(scopes, list) or any(not isinstance(scope, str) for scope in scopes):
            conflicts.append(
                conflict(
                    "MANIFEST_MALFORMED",
                    "allowed_nested_scopes must be an array of strings",
                    repository=name,
                )
            )
            scopes = []
        if len(scopes) != len(set(scopes)):
            conflicts.append(
                conflict(
                    "MANIFEST_DUPLICATE_SCOPE",
                    "allowed_nested_scopes contains a duplicate",
                    repository=name,
                )
            )
        for scope in scopes:
            if _is_absolute_manifest_path(scope):
                conflicts.append(
                    conflict(
                        "MANIFEST_ABSOLUTE_PATH",
                        "nested scope must be repository-relative",
                        repository=name,
                        path=scope,
                    )
                )
            elif _is_unsafe_manifest_path(scope):
                conflicts.append(
                    conflict(
                        "MANIFEST_UNSAFE_PATH",
                        "nested scope contains traversal or unsafe separators",
                        repository=name,
                        path=scope,
                    )
                )

        if lifecycle in {"excluded_local_stub", "excluded_legacy_hosted"}:
            if not isinstance(entry.get("exclusion_reason"), str) or not entry["exclusion_reason"].strip():
                conflicts.append(
                    conflict(
                        "MANIFEST_EXCLUSION_REASON",
                        "excluded repository requires an exclusion_reason",
                        repository=name,
                    )
                )
            if scopes:
                conflicts.append(
                    conflict(
                        "MANIFEST_EXCLUDED_SCOPE",
                        "excluded repository cannot allow nested instruction scopes",
                        repository=name,
                    )
                )
            if lifecycle == "excluded_local_stub":
                fingerprint = entry.get("content_sha256")
                if not isinstance(fingerprint, str) or not re.fullmatch(r"[0-9a-f]{64}", fingerprint):
                    conflicts.append(
                        conflict(
                            "MANIFEST_EXCLUDED_FINGERPRINT",
                            "excluded local repository requires a lowercase SHA-256 content fingerprint",
                            repository=name,
                        )
                    )
                if "expected_head" in entry:
                    conflicts.append(
                        conflict(
                            "MANIFEST_UNKNOWN_FIELD",
                            "expected_head is valid only for an excluded hosted repository",
                            repository=name,
                        )
                    )
            else:
                expected_head = entry.get("expected_head")
                if not isinstance(expected_head, str) or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", expected_head):
                    conflicts.append(
                        conflict(
                            "MANIFEST_EXCLUDED_HEAD",
                            "excluded hosted repository requires a lowercase 40- or 64-character Git head",
                            repository=name,
                        )
                    )
                if "content_sha256" in entry:
                    conflicts.append(
                        conflict(
                            "MANIFEST_UNKNOWN_FIELD",
                            "content_sha256 is valid only for an excluded local repository",
                            repository=name,
                        )
                    )
        elif any(field in entry for field in ("exclusion_reason", "content_sha256", "expected_head")):
            conflicts.append(
                conflict(
                    "MANIFEST_UNKNOWN_FIELD",
                    "exclusion fields are valid only for an excluded repository",
                    repository=name,
                )
            )

    for name in sorted(EXPECTED_REPOSITORIES - names):
        conflicts.append(conflict("MANIFEST_MISSING_REPOSITORY", "required repository is absent", repository=name))
    for name in sorted(names - EXPECTED_REPOSITORIES):
        conflicts.append(conflict("MANIFEST_UNEXPECTED_REPOSITORY", "repository is outside the AO Stack contract", repository=name))
    return conflicts


def discover_instruction_files(repo: Path) -> list[Path]:
    paths: list[Path] = []
    for root, directories, files in os.walk(repo, followlinks=False):
        current = Path(root)
        directories[:] = sorted(
            name
            for name in directories
            if name not in DISCOVERY_EXCLUDED_NAMES
        )
        for file_name in sorted(files):
            if file_name in {"AGENTS.md", "CLAUDE.md"}:
                paths.append(current / file_name)
    return sorted(paths)


def _validate_instruction_file(
    path: Path,
    *,
    repository: str,
    relative_path: str,
    kind: str,
    lifecycle: str,
) -> tuple[list[dict[str, object]], int]:
    conflicts: list[dict[str, object]] = []
    try:
        mode = path.lstat().st_mode
    except OSError:
        return conflicts, 0
    if stat.S_ISLNK(mode):
        conflicts.append(
            conflict(
                "INSTRUCTION_SYMLINK",
                "instruction files must be regular tracked files, not symlinks",
                repository=repository,
                path=relative_path,
            )
        )
        return conflicts, 0
    if not stat.S_ISREG(mode):
        conflicts.append(
            conflict(
                "INSTRUCTION_NOT_REGULAR",
                "instruction path is not a regular file",
                repository=repository,
                path=relative_path,
            )
        )
        return conflicts, 0
    try:
        data = path.read_bytes()
    except OSError as exc:
        conflicts.append(
            conflict(
                "INSTRUCTION_UNREADABLE",
                f"cannot read instruction file: {exc}",
                repository=repository,
                path=relative_path,
            )
        )
        return conflicts, 0
    if not data:
        conflicts.append(
            conflict(
                "EMPTY_INSTRUCTION_FILE",
                "instruction file must not be empty",
                repository=repository,
                path=relative_path,
            )
        )
        return conflicts, 0
    if path.name == "CLAUDE.md":
        if data != EXACT_CLAUDE_BYTES:
            conflicts.append(
                conflict(
                    "CLAUDE_BYTES_INVALID",
                    "CLAUDE.md must contain exactly @AGENTS.md followed by one newline",
                    repository=repository,
                    path=relative_path,
                )
            )
        return conflicts, len(data)
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        conflicts.append(
            conflict(
                "INSTRUCTION_NOT_UTF8",
                "AGENTS.md must be UTF-8 text",
                repository=repository,
                path=relative_path,
            )
        )
        return conflicts, len(data)

    line_count = len(text.splitlines())
    if kind == "root":
        byte_limit = 8 * 1024 if lifecycle == "archived_hosted" else 12 * 1024
        line_limit = 60 if lifecycle == "archived_hosted" else 120
        size_code = "ROOT_SIZE_LIMIT"
    else:
        byte_limit = 8 * 1024
        line_limit = 80
        size_code = "NESTED_SIZE_LIMIT"
    if len(data) > byte_limit or line_count > line_limit:
        conflicts.append(
            conflict(
                size_code,
                f"{kind} AGENTS.md is {len(data)} bytes/{line_count} lines; limit is {byte_limit} bytes/{line_limit} lines",
                repository=repository,
                path=relative_path,
            )
        )
    if any(pattern.search(text) for pattern in USER_PATH_PATTERNS):
        conflicts.append(
            conflict(
                "USER_ABSOLUTE_PATH",
                "instruction file contains a user-specific absolute path",
                repository=repository,
                path=relative_path,
            )
        )
    if any(pattern.search(text) for pattern in SECRET_PATTERNS):
        conflicts.append(
            conflict(
                "SECRET_MATERIAL",
                "instruction file contains obvious secret-like material",
                repository=repository,
                path=relative_path,
            )
        )
    return conflicts, len(data)


def _validate_repository(
    workspace_root: Path,
    entry: dict[str, Any],
) -> list[dict[str, object]]:
    name = entry["name"]
    lifecycle = entry["lifecycle"]
    repo = workspace_root / name
    conflicts: list[dict[str, object]] = []
    if not repo.is_dir():
        return [
            conflict(
                "MISSING_REPOSITORY_DIRECTORY",
                "repository directory is missing",
                repository=name,
                path=name,
            )
        ]
    if lifecycle == "excluded_local_stub":
        expected = entry.get("content_sha256")
        try:
            actual = content_fingerprint(repo)
        except OSError as exc:
            return [
                conflict(
                    "EXCLUDED_REPOSITORY_UNREADABLE",
                    f"cannot fingerprint excluded repository: {exc}",
                    repository=name,
                )
            ]
        if expected != actual:
            conflicts.append(
                conflict(
                    "EXCLUDED_REPOSITORY_MODIFIED",
                    f"excluded repository fingerprint differs: expected {expected}, found {actual}",
                    repository=name,
                )
            )
        return conflicts

    if lifecycle == "excluded_legacy_hosted":
        git_environment = os.environ.copy()
        git_environment["GIT_OPTIONAL_LOCKS"] = "0"
        try:
            head_result = subprocess.run(
                ["git", "rev-parse", "--verify", "HEAD"],
                cwd=repo,
                check=False,
                capture_output=True,
                text=True,
                env=git_environment,
            )
            status_result = subprocess.run(
                ["git", "status", "--porcelain=v1", "--untracked-files=no"],
                cwd=repo,
                check=False,
                capture_output=True,
                text=True,
                env=git_environment,
            )
        except OSError as exc:
            return [
                conflict(
                    "EXCLUDED_REPOSITORY_UNREADABLE",
                    f"cannot inspect excluded hosted repository: {exc}",
                    repository=name,
                )
            ]
        if head_result.returncode != 0 or status_result.returncode != 0:
            return [
                conflict(
                    "EXCLUDED_REPOSITORY_UNREADABLE",
                    "cannot inspect excluded hosted repository Git state",
                    repository=name,
                )
            ]
        actual_head = head_result.stdout.strip()
        expected_head = entry.get("expected_head")
        if actual_head != expected_head:
            conflicts.append(
                conflict(
                    "EXCLUDED_REPOSITORY_HEAD_CHANGED",
                    f"excluded repository head differs: expected {expected_head}, found {actual_head}",
                    repository=name,
                )
            )
        if status_result.stdout:
            conflicts.append(
                conflict(
                    "EXCLUDED_REPOSITORY_MODIFIED",
                    "excluded hosted repository has tracked working-tree or index changes",
                    repository=name,
                )
            )
        return conflicts

    root_sizes: dict[str, int] = {}
    for file_name, missing_code in (
        ("AGENTS.md", "MISSING_ROOT_AGENTS"),
        ("CLAUDE.md", "MISSING_ROOT_CLAUDE"),
    ):
        path = repo / file_name
        if not path.exists() and not path.is_symlink():
            conflicts.append(
                conflict(
                    missing_code,
                    f"required root {file_name} is missing",
                    repository=name,
                    path=file_name,
                )
            )
            continue
        file_conflicts, size = _validate_instruction_file(
            path,
            repository=name,
            relative_path=file_name,
            kind="root",
            lifecycle=lifecycle,
        )
        conflicts.extend(file_conflicts)
        root_sizes[file_name] = size

    gitignore = repo / ".gitignore"
    try:
        ignore_lines = gitignore.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        ignore_lines = []
    for required_ignore in ("CLAUDE.local.md", ".claude/settings.local.json"):
        if required_ignore not in ignore_lines:
            conflicts.append(
                conflict(
                    "MISSING_LOCAL_IGNORE",
                    f".gitignore lacks exact entry {required_ignore}",
                    repository=name,
                    path=".gitignore",
                )
            )

    discovered = discover_instruction_files(repo)
    nested_by_scope: dict[str, set[str]] = {}
    for path in discovered:
        relative = path.relative_to(repo)
        if len(relative.parts) == 1:
            continue
        scope = relative.parent.as_posix()
        nested_by_scope.setdefault(scope, set()).add(path.name)
    allowed = set(entry["allowed_nested_scopes"])
    for scope in sorted(set(nested_by_scope) - allowed):
        for file_name in sorted(nested_by_scope[scope]):
            conflicts.append(
                conflict(
                    "UNEXPECTED_INSTRUCTION_SCOPE",
                    "instruction file is outside an allowed nested scope",
                    repository=name,
                    path=f"{scope}/{file_name}",
                )
            )
    nested_agent_sizes: dict[str, int] = {}
    for scope in sorted(allowed | set(nested_by_scope)):
        present = nested_by_scope.get(scope, set())
        if present != {"AGENTS.md", "CLAUDE.md"}:
            conflicts.append(
                conflict(
                    "NESTED_PAIR_MISSING",
                    "nested instruction scope must contain paired AGENTS.md and exact CLAUDE.md",
                    repository=name,
                    path=scope,
                )
            )
        for file_name in sorted(present):
            path = repo / scope / file_name
            file_conflicts, size = _validate_instruction_file(
                path,
                repository=name,
                relative_path=f"{scope}/{file_name}",
                kind="nested",
                lifecycle=lifecycle,
            )
            conflicts.extend(file_conflicts)
            if file_name == "AGENTS.md":
                nested_agent_sizes[scope] = size

    root_agent_size = root_sizes.get("AGENTS.md", 0)
    for leaf in sorted(allowed):
        leaf_path = PurePosixPath(leaf)
        ancestors = [
            scope
            for scope in allowed
            if PurePosixPath(scope) == leaf_path or PurePosixPath(scope) in leaf_path.parents
        ]
        chain_size = root_agent_size + sum(nested_agent_sizes.get(scope, 0) for scope in ancestors)
        if chain_size > 24 * 1024:
            conflicts.append(
                conflict(
                    "CHAIN_SIZE_LIMIT",
                    f"root+nested AGENTS.md chain is {chain_size} bytes; limit is {24 * 1024}",
                    repository=name,
                    path=leaf,
                )
            )
    return conflicts


def _sorted_conflicts(conflicts: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    return sorted(
        conflicts,
        key=lambda item: (
            str(item.get("repository") or ""),
            str(item.get("path") or ""),
            str(item["code"]),
            str(item["message"]),
        ),
    )


def validate_workspace(
    workspace_root: Path,
    manifest_path: Path = DEFAULT_MANIFEST,
    *,
    repository: str | None = None,
) -> dict[str, object]:
    workspace_root = workspace_root.resolve()
    document = load_manifest(manifest_path)
    conflicts = validate_manifest(document)
    entries = document.get("repositories")
    valid_entries = [
        entry
        for entry in entries
        if isinstance(entries, list)
        and isinstance(entry, dict)
        and isinstance(entry.get("name"), str)
        and entry.get("lifecycle") in LIFECYCLES
        and isinstance(entry.get("allowed_nested_scopes"), list)
    ] if isinstance(entries, list) else []
    by_name = {entry["name"]: entry for entry in valid_entries}
    if repository is not None and repository not in EXPECTED_REPOSITORIES:
        conflicts.append(
            conflict(
                "MANIFEST_UNKNOWN_REPOSITORY_SELECTOR",
                "repository selector is outside the AO Stack contract",
                repository=repository,
            )
        )
    selected = sorted(by_name) if repository is None else ([repository] if repository in by_name else [])
    for name in selected:
        conflicts.extend(_validate_repository(workspace_root, by_name[name]))
    conflicts = _sorted_conflicts(conflicts)
    results = []
    for name in selected:
        entry = by_name[name]
        codes = sorted({item["code"] for item in conflicts if item.get("repository") == name})
        status = "conflict" if codes else (
            "excluded_unchanged"
            if entry["lifecycle"] in {"excluded_local_stub", "excluded_legacy_hosted"}
            else "ok"
        )
        results.append(
            {
                "conflict_codes": codes,
                "lifecycle": entry["lifecycle"],
                "name": name,
                "status": status,
            }
        )
    return {
        "conflict_count": len(conflicts),
        "conflicts": conflicts,
        "manifest": str(manifest_path.resolve()),
        "repositories": results,
        "schema_version": "1.0.0",
        "status": "ok" if not conflicts else "conflict",
        "workspace_root": str(workspace_root),
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=ROOT.parent,
        help="directory containing the AO repository checkouts (default: parent of ao-architecture)",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="layout manifest to validate",
    )
    parser.add_argument(
        "--repository",
        help="validate one repository's files while still validating the complete manifest",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        result = validate_workspace(
            args.workspace_root,
            args.manifest,
            repository=args.repository,
        )
    except ManifestError as exc:
        result = {
            "conflict_count": 1,
            "conflicts": [
                conflict(
                    exc.code,
                    exc.message,
                    path=str(args.manifest),
                )
            ],
            "manifest": str(args.manifest.resolve()),
            "repositories": [],
            "schema_version": "1.0.0",
            "status": "conflict",
            "workspace_root": str(args.workspace_root.resolve()),
        }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
