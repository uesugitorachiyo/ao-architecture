#!/usr/bin/env python3
"""Safely materialize or verify the frozen AO development baseline."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import stat
import subprocess
from typing import Any, Iterable, NamedTuple, Sequence


SAFE_COMPONENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
FILE_ATTRIBUTE_REPARSE_POINT = 0x0400
MAX_COMMAND_OUTPUT_BYTES = 1024 * 1024


class BootstrapError(ValueError):
    """Raised when bootstrap input or host state is unsafe or inconsistent."""


class RepositorySpec(NamedTuple):
    name: str
    path: str
    upstream_url: str
    commit: str


class CommandRecord(NamedTuple):
    argv: tuple[str, ...]
    cwd: str
    environment: dict[str, str]
    returncode: int
    stdout: str
    stderr: str


class CommandRunner:
    def __init__(self) -> None:
        self.records: list[CommandRecord] = []

    def run(
        self,
        argv: Sequence[str],
        *,
        cwd: str | Path,
        check: bool = True,
        timeout: int = 300,
    ) -> CommandRecord:
        if not argv or not all(isinstance(item, str) and item for item in argv):
            raise BootstrapError("command argv must contain non-empty strings")
        environment = os.environ.copy()
        overrides = {
            "GIT_TERMINAL_PROMPT": "0",
            "GCM_INTERACTIVE": "Never",
            "GIT_OPTIONAL_LOCKS": "0",
        }
        environment.update(overrides)
        try:
            completed = subprocess.run(
                list(argv),
                cwd=os.fspath(cwd),
                env=environment,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=timeout,
                check=False,
                shell=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise BootstrapError(f"command failed to start or timed out: {argv[0]}") from exc
        if len(completed.stdout.encode("utf-8")) > MAX_COMMAND_OUTPUT_BYTES or len(
            completed.stderr.encode("utf-8")
        ) > MAX_COMMAND_OUTPUT_BYTES:
            raise BootstrapError(f"command output exceeds {MAX_COMMAND_OUTPUT_BYTES} bytes: {argv[0]}")
        record = CommandRecord(
            tuple(argv),
            os.fspath(cwd),
            overrides,
            completed.returncode,
            completed.stdout,
            completed.stderr,
        )
        self.records.append(record)
        if check and completed.returncode != 0:
            raise BootstrapError(
                f"command failed with exit {completed.returncode}: {' '.join(argv[:3])}"
            )
        return record


def reject_duplicate_pairs(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise BootstrapError(f"duplicate key: {key}")
        result[key] = value
    return result


def is_link_or_reparse(path: str | Path) -> bool:
    target = Path(path)
    try:
        metadata = target.lstat()
    except FileNotFoundError:
        return False
    attributes = getattr(metadata, "st_file_attributes", 0)
    return stat.S_ISLNK(metadata.st_mode) or bool(
        attributes & FILE_ATTRIBUTE_REPARSE_POINT
    )


def load_json_file(path: str | Path, maximum_bytes: int) -> Any:
    target = Path(path)
    try:
        metadata = target.lstat()
    except OSError as exc:
        raise BootstrapError(f"cannot inspect input: {target}") from exc
    if (
        not stat.S_ISREG(metadata.st_mode)
        or is_link_or_reparse(target)
    ):
        raise BootstrapError(f"input must be a regular non-link file: {target}")
    if metadata.st_size > maximum_bytes:
        raise BootstrapError(f"input exceeds {maximum_bytes} bytes: {target}")
    try:
        text = target.read_bytes().decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BootstrapError(f"input is not UTF-8: {target}") from exc
    try:
        return json.loads(text, object_pairs_hook=reject_duplicate_pairs)
    except json.JSONDecodeError as exc:
        raise BootstrapError(f"invalid JSON: {target}: {exc.msg}") from exc


def _absolute_without_resolving(path: str | Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def _require_no_link_ancestors(path: Path) -> None:
    target = _absolute_without_resolving(path)
    candidates = list(reversed((target, *target.parents)))
    for candidate in candidates:
        try:
            candidate.lstat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise BootstrapError(f"cannot inspect path component: {candidate}") from exc
        if is_link_or_reparse(candidate):
            raise BootstrapError(f"path component is a link or reparse point: {candidate}")


def validate_materialization_root(path: str | Path, mode: str) -> Path:
    if mode not in {"materialize", "verify-existing"}:
        raise BootstrapError("mode must be materialize or verify-existing")
    target = _absolute_without_resolving(path)
    _require_no_link_ancestors(target)
    try:
        metadata = target.lstat()
    except FileNotFoundError:
        if mode == "verify-existing":
            raise BootstrapError("verify-existing root must exist")
        return target
    except OSError as exc:
        raise BootstrapError(f"cannot inspect materialization root: {target}") from exc
    if not stat.S_ISDIR(metadata.st_mode) or is_link_or_reparse(target):
        raise BootstrapError("materialization root must be a regular non-link directory")
    if mode == "materialize":
        try:
            next(target.iterdir())
        except StopIteration:
            pass
        else:
            raise BootstrapError("materialize root must be empty")
    return target.resolve(strict=True)


def contained_child(root: str | Path, name: str) -> Path:
    if (
        not isinstance(name, str)
        or not SAFE_COMPONENT.fullmatch(name)
        or "/" in name
        or "\\" in name
    ):
        raise BootstrapError(f"unsafe child name: {name!r}")
    base = _absolute_without_resolving(root)
    child = base / name
    try:
        if os.path.commonpath((os.fspath(base), os.fspath(child))) != os.fspath(base):
            raise BootstrapError(f"child escapes materialization root: {name}")
    except ValueError as exc:
        raise BootstrapError(f"child escapes materialization root: {name}") from exc
    return child


def require_unique_casefold(names: Iterable[str]) -> None:
    seen: dict[str, str] = {}
    for name in names:
        folded = name.casefold()
        if folded in seen:
            raise BootstrapError(
                f"case-fold collision: {seen[folded]} and {name}"
            )
        seen[folded] = name


def _validate_repository_specs(specs: Sequence[RepositorySpec]) -> None:
    names = [spec.name for spec in specs]
    paths = [spec.path for spec in specs]
    require_unique_casefold(names)
    require_unique_casefold(paths)
    if len(set(names)) != len(names) or len(set(paths)) != len(paths):
        raise BootstrapError("repository names and paths must be unique")
    for spec in specs:
        contained_child(Path.cwd(), spec.name)
        contained_child(Path.cwd(), spec.path)
        if spec.name != spec.path:
            raise BootstrapError(f"repository path must equal name: {spec.name}")
        if not re.fullmatch(r"[0-9a-f]{40}", spec.commit):
            raise BootstrapError(f"repository commit is invalid: {spec.name}")
        if not spec.upstream_url:
            raise BootstrapError(f"repository upstream is required: {spec.name}")


def validate_submodule_status(lines: Iterable[str]) -> None:
    for line in lines:
        if not line:
            continue
        if line[0] in {"-", "+", "U"}:
            raise BootstrapError(f"unsafe submodule status: {line[0]}")
        if line[0] != " ":
            raise BootstrapError("invalid submodule status")


def _same_upstream(actual: str, expected: str) -> bool:
    if actual == expected:
        return True
    if "://" not in actual and "://" not in expected:
        return os.path.normcase(os.path.abspath(actual)) == os.path.normcase(
            os.path.abspath(expected)
        )
    return actual.rstrip("/") == expected.rstrip("/")


def _verify_repository(
    root: Path, spec: RepositorySpec, runner: CommandRunner
) -> dict[str, Any]:
    checkout = contained_child(root, spec.path)
    try:
        metadata = checkout.lstat()
    except OSError as exc:
        raise BootstrapError(f"repository is missing: {spec.name}") from exc
    if not stat.S_ISDIR(metadata.st_mode) or is_link_or_reparse(checkout):
        raise BootstrapError(f"repository is a link, reparse point, or non-directory: {spec.name}")
    if checkout.resolve(strict=True).parent != root.resolve(strict=True):
        raise BootstrapError(f"repository escapes materialization root: {spec.name}")

    head = runner.run(["git", "rev-parse", "HEAD"], cwd=checkout).stdout.strip()
    if head != spec.commit:
        raise BootstrapError(f"repository commit mismatch: {spec.name}")
    symbolic = runner.run(
        ["git", "symbolic-ref", "-q", "HEAD"], cwd=checkout, check=False
    )
    if symbolic.returncode == 0:
        raise BootstrapError(f"repository is not detached: {spec.name}")
    if symbolic.returncode not in {1, 128}:
        raise BootstrapError(f"cannot classify detached HEAD: {spec.name}")
    origin = runner.run(
        ["git", "remote", "get-url", "origin"], cwd=checkout
    ).stdout.strip()
    if not _same_upstream(origin, spec.upstream_url):
        raise BootstrapError(f"repository origin mismatch: {spec.name}")
    status_output = runner.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=checkout
    ).stdout
    if status_output:
        raise BootstrapError(f"repository is dirty: {spec.name}")
    submodules = runner.run(
        ["git", "submodule", "status", "--recursive"], cwd=checkout
    ).stdout.splitlines()
    validate_submodule_status(submodules)
    return {
        "repository": spec.name,
        "commit": head,
        "origin": spec.upstream_url,
        "detached": True,
        "clean": True,
        "submodules_clean": True,
    }


def materialize_repositories(
    root: str | Path,
    specs: Sequence[RepositorySpec],
    runner: CommandRunner,
) -> list[dict[str, Any]]:
    _validate_repository_specs(specs)
    target = validate_materialization_root(root, "materialize")
    target.mkdir(parents=False, exist_ok=True)
    records: list[dict[str, Any]] = []
    for spec in specs:
        checkout = contained_child(target, spec.path)
        runner.run(
            [
                "git",
                "clone",
                "--no-checkout",
                "--no-tags",
                spec.upstream_url,
                os.fspath(checkout),
            ],
            cwd=target,
        )
        runner.run(
            ["git", "checkout", "--detach", spec.commit], cwd=checkout
        )
        records.append(_verify_repository(target, spec, runner))
    return records


def verify_repositories(
    root: str | Path,
    specs: Sequence[RepositorySpec],
    runner: CommandRunner,
) -> list[dict[str, Any]]:
    _validate_repository_specs(specs)
    target = validate_materialization_root(root, "verify-existing")
    expected = {spec.path for spec in specs} | {".ao-baseline"}
    actual = {entry.name for entry in target.iterdir()}
    require_unique_casefold(actual)
    if actual != expected:
        raise BootstrapError(
            "workspace sibling set mismatch: "
            f"missing={sorted(expected - actual)} extra={sorted(actual - expected)}"
        )
    return [_verify_repository(target, spec, runner) for spec in specs]
