#!/usr/bin/env python3
"""Safely materialize or verify the frozen AO development baseline."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import stat
from typing import Any, Iterable


SAFE_COMPONENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
FILE_ATTRIBUTE_REPARSE_POINT = 0x0400


class BootstrapError(ValueError):
    """Raised when bootstrap input or host state is unsafe or inconsistent."""


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
