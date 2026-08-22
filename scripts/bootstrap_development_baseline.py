#!/usr/bin/env python3
"""Safely materialize or verify the frozen AO development baseline."""

from __future__ import annotations

import json
import hashlib
import os
import platform
from pathlib import Path
from pathlib import PurePosixPath
import re
import stat
import subprocess
import shutil
import tarfile
import tempfile
from typing import Any, Iterable, NamedTuple, Sequence
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen
import zipfile


SAFE_COMPONENT = re.compile(
    r"^(?:[A-Za-z0-9][A-Za-z0-9._-]*|\.[A-Za-z0-9][A-Za-z0-9._-]*)$"
)
FILE_ATTRIBUTE_REPARSE_POINT = 0x0400
MAX_COMMAND_OUTPUT_BYTES = 1024 * 1024
MAX_ASSET_BYTES = 256 * 1024 * 1024
MAX_ARCHIVE_MEMBER_BYTES = 256 * 1024 * 1024
MAX_ARCHIVE_EXPANDED_BYTES = 512 * 1024 * 1024
MAX_ARCHIVE_MEMBERS = 1024
AUTHORITY = {
    "safe_to_execute": False,
    "executes_work": False,
    "approves_work": False,
    "mutates_repositories": False,
    "provider_calls": False,
    "credential_use": False,
    "release": False,
    "publication": False,
    "deployment": False,
    "promotion": False,
    "compatibility_activation": False,
    "external_beta": False,
    "rsi": False,
}


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


class RuntimeAssetSpec(NamedTuple):
    repository: str
    release_url: str
    platform: str
    architecture: str
    name: str
    sha256: str


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


def asset_download_url(release_url: str, name: str) -> str:
    parsed = urlparse(release_url)
    marker = "/releases/tag/"
    if parsed.scheme != "https" or parsed.netloc.lower() != "github.com":
        raise BootstrapError("release URL must be HTTPS on github.com")
    if marker not in parsed.path or parsed.query or parsed.fragment:
        raise BootstrapError("release URL must identify one immutable tag")
    prefix, tag = parsed.path.split(marker, 1)
    if not tag or "/" in tag:
        raise BootstrapError("release URL tag is invalid")
    if not name or "/" in name or "\\" in name:
        raise BootstrapError("runtime asset name must be a basename")
    return f"https://github.com{prefix}/releases/download/{quote(tag, safe='')}/{quote(name, safe='')}"


def select_runtime_assets(
    releases: Sequence[dict[str, Any]], platform_name: str
) -> list[RuntimeAssetSpec]:
    if platform_name not in {"linux", "macos", "windows"}:
        raise BootstrapError(f"unsupported runtime platform: {platform_name}")
    selected: list[RuntimeAssetSpec] = []
    seen: set[str] = set()
    for release in releases:
        repository = release.get("repository")
        if not isinstance(repository, str) or not repository or repository in seen:
            raise BootstrapError("runtime release repository identity is invalid")
        seen.add(repository)
        assets = release.get("assets")
        if not isinstance(assets, list):
            raise BootstrapError(f"runtime assets must be an array: {repository}")
        matches = [item for item in assets if isinstance(item, dict) and item.get("platform") == platform_name]
        if len(matches) != 1:
            raise BootstrapError(f"runtime release requires one {platform_name} asset: {repository}")
        asset = matches[0]
        digest = asset.get("sha256")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise BootstrapError(f"runtime asset digest is invalid: {repository}")
        selected.append(
            RuntimeAssetSpec(
                repository=repository,
                release_url=release.get("release_url", ""),
                platform=platform_name,
                architecture=asset.get("architecture", ""),
                name=asset.get("name", ""),
                sha256=digest,
            )
        )
    return selected


def download_bounded(
    url: str,
    destination: str | Path,
    expected_sha256: str,
    *,
    opener=urlopen,
    maximum_bytes: int = MAX_ASSET_BYTES,
) -> dict[str, Any]:
    if urlparse(url).scheme != "https":
        raise BootstrapError("download URL must be HTTPS")
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise BootstrapError("download expected digest is invalid")
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        output = target.open("xb")
    except FileExistsError as exc:
        raise BootstrapError(f"download destination already exists: {target.name}") from exc
    digest = hashlib.sha256()
    total = 0
    request = Request(url, headers={"User-Agent": "ao-architecture-baseline-bootstrap/1"})
    try:
        with output:
            with opener(request, timeout=90) as response:
                declared = response.headers.get("Content-Length")
                if declared is not None:
                    try:
                        declared_bytes = int(declared)
                    except ValueError as exc:
                        raise BootstrapError("download Content-Length is invalid") from exc
                    if declared_bytes < 0 or declared_bytes > maximum_bytes:
                        raise BootstrapError(f"download exceeds {maximum_bytes} bytes")
                while True:
                    chunk = response.read(min(1024 * 1024, maximum_bytes + 1 - total))
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > maximum_bytes:
                        raise BootstrapError(f"download exceeds {maximum_bytes} bytes")
                    digest.update(chunk)
                    output.write(chunk)
    except BootstrapError:
        raise
    except OSError as exc:
        raise BootstrapError(f"download failed: {target.name}") from exc
    actual = digest.hexdigest()
    if actual != expected_sha256:
        raise BootstrapError("download digest mismatch")
    return {"sha256": actual, "bytes": total}


def _safe_archive_parts(name: str) -> tuple[str, ...]:
    if not isinstance(name, str) or not name or "\\" in name or "\x00" in name:
        raise BootstrapError("archive member name is unsafe")
    if name.startswith(("/", "//")) or re.match(r"^[A-Za-z]:", name):
        raise BootstrapError("archive member path is absolute")
    path = PurePosixPath(name)
    parts = path.parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise BootstrapError("archive member path traverses or is empty")
    return parts


def _archive_output_path(destination: Path, name: str) -> Path:
    parts = _safe_archive_parts(name)
    output = destination.joinpath(*parts)
    try:
        if os.path.commonpath((os.fspath(destination), os.fspath(output))) != os.fspath(destination):
            raise BootstrapError("archive member escapes destination")
    except ValueError as exc:
        raise BootstrapError("archive member escapes destination") from exc
    return output


def _validate_archive_names(names: Sequence[str], maximum_members: int) -> None:
    if len(names) > maximum_members:
        raise BootstrapError(f"archive member count exceeds {maximum_members}")
    seen: set[str] = set()
    for name in names:
        normalized = "/".join(_safe_archive_parts(name.rstrip("/"))).casefold()
        if normalized in seen:
            raise BootstrapError("archive member name collision")
        seen.add(normalized)


def safe_extract_tar(
    archive_path: str | Path,
    destination: str | Path,
    *,
    maximum_members: int = MAX_ARCHIVE_MEMBERS,
    maximum_member_bytes: int = MAX_ARCHIVE_MEMBER_BYTES,
    maximum_expanded_bytes: int = MAX_ARCHIVE_EXPANDED_BYTES,
) -> dict[str, Any]:
    target = Path(destination)
    target.mkdir(parents=True, exist_ok=False)
    total = 0
    try:
        with tarfile.open(archive_path, "r:*") as archive:
            members = archive.getmembers()
            _validate_archive_names([member.name for member in members], maximum_members)
            for member in members:
                if member.mode & (stat.S_ISUID | stat.S_ISGID):
                    raise BootstrapError("archive member has privileged mode bits")
                if member.isdir():
                    _archive_output_path(target, member.name).mkdir(parents=True, exist_ok=True)
                    continue
                if not member.isreg():
                    raise BootstrapError("tar member must be regular or directory")
                if member.size < 0 or member.size > maximum_member_bytes:
                    raise BootstrapError(f"archive member exceeds {maximum_member_bytes} bytes")
                total += member.size
                if total > maximum_expanded_bytes:
                    raise BootstrapError(f"archive expanded bytes exceed {maximum_expanded_bytes}")
                output = _archive_output_path(target, member.name)
                output.parent.mkdir(parents=True, exist_ok=True)
                source = archive.extractfile(member)
                if source is None:
                    raise BootstrapError("tar member cannot be read")
                with source, output.open("xb") as destination_file:
                    body = source.read(maximum_member_bytes + 1)
                    if len(body) != member.size:
                        raise BootstrapError("tar member size mismatch")
                    destination_file.write(body)
    except (tarfile.TarError, OSError) as exc:
        if isinstance(exc, BootstrapError):
            raise
        raise BootstrapError("tar archive is invalid") from exc
    return {"members": len(members), "expanded_bytes": total, "format": "tar"}


def safe_extract_zip(
    archive_path: str | Path,
    destination: str | Path,
    *,
    maximum_members: int = MAX_ARCHIVE_MEMBERS,
    maximum_member_bytes: int = MAX_ARCHIVE_MEMBER_BYTES,
    maximum_expanded_bytes: int = MAX_ARCHIVE_EXPANDED_BYTES,
) -> dict[str, Any]:
    target = Path(destination)
    target.mkdir(parents=True, exist_ok=False)
    total = 0
    try:
        with zipfile.ZipFile(archive_path) as archive:
            members = archive.infolist()
            _validate_archive_names([member.filename for member in members], maximum_members)
            for member in members:
                mode = (member.external_attr >> 16) & 0xFFFF
                if mode & (stat.S_ISUID | stat.S_ISGID):
                    raise BootstrapError("archive member has privileged mode bits")
                if member.is_dir():
                    _archive_output_path(target, member.filename).mkdir(parents=True, exist_ok=True)
                    continue
                if member.create_system == 3 and mode and not stat.S_ISREG(mode):
                    raise BootstrapError("ZIP member must be regular")
                if member.file_size < 0 or member.file_size > maximum_member_bytes:
                    raise BootstrapError(f"archive member exceeds {maximum_member_bytes} bytes")
                total += member.file_size
                if total > maximum_expanded_bytes:
                    raise BootstrapError(f"archive expanded bytes exceed {maximum_expanded_bytes}")
                output = _archive_output_path(target, member.filename)
                output.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member, "r") as source, output.open("xb") as destination_file:
                    body = source.read(maximum_member_bytes + 1)
                    if len(body) != member.file_size:
                        raise BootstrapError("ZIP member size mismatch")
                    destination_file.write(body)
    except (zipfile.BadZipFile, OSError) as exc:
        if isinstance(exc, BootstrapError):
            raise
        raise BootstrapError("ZIP archive is invalid") from exc
    return {"members": len(members), "expanded_bytes": total, "format": "zip"}


def install_plain_asset(source: str | Path, destination: str | Path) -> dict[str, Any]:
    source_path = Path(source)
    if is_link_or_reparse(source_path) or not source_path.is_file():
        raise BootstrapError("plain runtime asset must be a regular non-link file")
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with source_path.open("rb") as input_file, target.open("xb") as output_file:
            total = 0
            while True:
                chunk = input_file.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_ASSET_BYTES:
                    raise BootstrapError(f"plain runtime asset exceeds {MAX_ASSET_BYTES} bytes")
                output_file.write(chunk)
    except FileExistsError as exc:
        raise BootstrapError("plain runtime destination already exists") from exc
    return {"bytes": total, "format": "plain"}


def materialize_runtime_assets(
    root: str | Path,
    releases: Sequence[dict[str, Any]],
    platform_name: str,
    *,
    opener=urlopen,
) -> list[dict[str, Any]]:
    workspace = validate_materialization_root(root, "verify-existing")
    evidence_root = contained_child(workspace, ".ao-baseline")
    if not evidence_root.is_dir() or is_link_or_reparse(evidence_root):
        raise BootstrapError(".ao-baseline must be a regular non-link directory")
    assets_root = contained_child(evidence_root, "assets")
    runtime_root = contained_child(evidence_root, "runtime")
    assets_root.mkdir(exist_ok=False)
    runtime_root.mkdir(exist_ok=False)
    records: list[dict[str, Any]] = []
    for asset in select_runtime_assets(releases, platform_name):
        asset_directory = contained_child(assets_root, asset.repository)
        runtime_directory = contained_child(runtime_root, asset.repository)
        asset_directory.mkdir(exist_ok=False)
        archive_path = contained_child(asset_directory, asset.name)
        url = asset_download_url(asset.release_url, asset.name)
        downloaded = download_bounded(
            url, archive_path, asset.sha256, opener=opener
        )
        lowered = asset.name.lower()
        if lowered.endswith(".zip"):
            installed = safe_extract_zip(archive_path, runtime_directory)
        elif lowered.endswith((".tar.gz", ".tgz")):
            installed = safe_extract_tar(archive_path, runtime_directory)
        else:
            runtime_directory.mkdir(exist_ok=False)
            installed = install_plain_asset(
                archive_path, contained_child(runtime_directory, asset.name)
            )
        records.append(
            {
                "repository": asset.repository,
                "platform": asset.platform,
                "architecture": asset.architecture,
                "name": asset.name,
                "expected_sha256": asset.sha256,
                "actual_sha256": downloaded["sha256"],
                "bytes": downloaded["bytes"],
                "install_format": installed["format"],
            }
        )
    return records


def parse_version(output: str) -> tuple[int, ...]:
    values = tuple(int(value) for value in re.findall(r"\d+", output))
    if not values:
        raise BootstrapError("toolchain version output has no numeric version")
    return values


def satisfies_constraint(version: Sequence[int], constraint: dict[str, Any]) -> bool:
    kind = constraint.get("kind")
    raw = constraint.get("value")
    if kind not in {"minimum", "exact_major"} or not isinstance(raw, str):
        raise BootstrapError("toolchain constraint is invalid")
    try:
        required = tuple(int(value) for value in raw.split("."))
    except ValueError as exc:
        raise BootstrapError("toolchain constraint value is invalid") from exc
    if not required:
        raise BootstrapError("toolchain constraint value is invalid")
    if kind == "exact_major":
        return version[0] == required[0]
    width = max(len(version), len(required))
    padded_version = tuple(version) + (0,) * (width - len(version))
    padded_required = required + (0,) * (width - len(required))
    return padded_version >= padded_required


def probe_toolchains(
    toolchains: Sequence[dict[str, Any]],
    runner: CommandRunner,
    cwd: str | Path,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    seen: set[str] = set()
    for toolchain in toolchains:
        name = toolchain.get("name")
        argv = toolchain.get("version_argv")
        constraint = toolchain.get("constraint")
        if not isinstance(name, str) or not name or name in seen:
            raise BootstrapError("toolchain name is invalid or duplicate")
        seen.add(name)
        if not isinstance(argv, list) or not argv or not all(
            isinstance(item, str) and item for item in argv
        ):
            raise BootstrapError(f"toolchain version argv is invalid: {name}")
        if not isinstance(constraint, dict):
            raise BootstrapError(f"toolchain constraint is invalid: {name}")
        try:
            record = runner.run(argv, cwd=cwd, timeout=30)
        except BootstrapError as exc:
            raise BootstrapError(f"toolchain probe failed: {name}") from exc
        output = (record.stdout + "\n" + record.stderr).strip()
        version = parse_version(output)
        satisfied = satisfies_constraint(version, constraint)
        if not satisfied:
            raise BootstrapError(f"toolchain constraint is not satisfied: {name}")
        results.append(
            {
                "name": name,
                "version": ".".join(str(value) for value in version),
                "constraint": dict(constraint),
                "constraint_satisfied": True,
                "command": summarize_command(record),
            }
        )
    return results


def native_platform() -> str:
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    if system == "windows":
        return "windows"
    if system == "linux":
        return "linux"
    raise BootstrapError(f"unsupported host platform: {system}")


def _probe_file_locking(path: Path) -> bool:
    with path.open("w+b") as handle:
        handle.write(b"0")
        handle.flush()
        try:
            if os.name == "nt":
                import msvcrt

                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        except OSError:
            return False
    return True


def probe_materialize_capabilities(evidence_root: str | Path) -> dict[str, Any]:
    root = Path(evidence_root)
    if not root.is_dir() or is_link_or_reparse(root):
        raise BootstrapError("capability evidence root must be a regular directory")
    probes = contained_child(root, "capability-probes")
    probes.mkdir(exist_ok=False)
    try:
        case_file = probes / "case-probe"
        case_file.write_bytes(b"case")
        case_sensitive = not (probes / "CASE-PROBE").exists()

        crlf_file = probes / "crlf-probe.txt"
        crlf_file.write_bytes(b"line\r\n")
        crlf_round_trip = crlf_file.read_bytes() == b"line\r\n"

        spaces = probes / "path with spaces"
        spaces.mkdir()
        path_with_spaces = spaces.is_dir()

        symlink_status = "unavailable"
        symlink_target = probes / "symlink-target"
        symlink_link = probes / "symlink-link"
        symlink_target.write_bytes(b"target")
        try:
            symlink_link.symlink_to(symlink_target)
        except (OSError, NotImplementedError):
            pass
        else:
            symlink_status = "available" if is_link_or_reparse(symlink_link) else "misclassified"

        locking = _probe_file_locking(probes / "locking-probe")
        capabilities = {
            "platform": native_platform(),
            "architecture": platform.machine().lower(),
            "case_sensitive": case_sensitive,
            "crlf_round_trip": crlf_round_trip,
            "path_with_spaces": path_with_spaces,
            "symlink": symlink_status,
            "file_locking": locking,
            "executable_suffix": ".exe" if os.name == "nt" else "",
            "powershell_51": shutil.which("powershell") is not None,
            "powershell_7": shutil.which("pwsh") is not None,
            "git_bash": shutil.which("bash") is not None,
            "covenant_rosetta_required": native_platform() == "macos"
            and platform.machine().lower() in {"arm64", "aarch64"},
        }
        return capabilities
    finally:
        for child in sorted(probes.rglob("*"), key=lambda path: len(path.parts), reverse=True):
            if child.is_symlink() or child.is_file():
                child.unlink()
            elif child.is_dir():
                child.rmdir()
        probes.rmdir()


def canonical_bytes(document: Any) -> bytes:
    return json.dumps(
        document, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def write_json_exclusive(path: str | Path, document: Any) -> str:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or is_link_or_reparse(target):
        raise BootstrapError(f"result already exists: {target.name}")
    body = json.dumps(document, sort_keys=True, indent=2, ensure_ascii=False).encode("utf-8") + b"\n"
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.", suffix=".tmp", dir=target.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(body)
            output.flush()
            os.fsync(output.fileno())
        try:
            os.link(temporary, target)
        except FileExistsError as exc:
            raise BootstrapError(f"result already exists: {target.name}") from exc
    finally:
        temporary.unlink(missing_ok=True)
    return "sha256:" + hashlib.sha256(body).hexdigest()


def load_retained_capabilities(path: str | Path) -> dict[str, Any]:
    document = load_json_file(path, 256 * 1024)
    if not isinstance(document, dict):
        raise BootstrapError("retained capabilities must be an object")
    for field in ("platform", "architecture", "symlink", "file_locking"):
        if field not in document:
            raise BootstrapError(f"retained capabilities missing field: {field}")
    return document


def summarize_command(record: CommandRecord) -> dict[str, Any]:
    stdout = record.stdout.encode("utf-8")
    stderr = record.stderr.encode("utf-8")
    return {
        "command": Path(record.argv[0]).name,
        "argv_count": len(record.argv),
        "exit_status": record.returncode,
        "stdout_bytes": len(stdout),
        "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
        "stderr_bytes": len(stderr),
        "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
    }


def build_bootstrap_result(
    *,
    mode: str,
    correlation_id: str,
    controller_commit: str,
    baseline_identity: str,
    repositories: Sequence[dict[str, Any]],
    runtime_assets: Sequence[dict[str, Any]],
    toolchains: Sequence[dict[str, Any]],
    capabilities: dict[str, Any],
    status: str,
) -> dict[str, Any]:
    if mode not in {"materialize", "verify-existing"}:
        raise BootstrapError("result mode is invalid")
    if status not in {"pass", "fail"}:
        raise BootstrapError("result status is invalid")
    if not re.fullmatch(r"[0-9a-f]{40}", controller_commit):
        raise BootstrapError("controller commit is invalid")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", baseline_identity):
        raise BootstrapError("baseline identity is invalid")
    return {
        "schema": "ao.architecture.development-baseline-bootstrap-result.v1",
        "correlation_id": correlation_id,
        "slice": "S02",
        "mode": mode,
        "status": status,
        "controller_source_commit": controller_commit,
        "baseline_identity": baseline_identity,
        "platform": capabilities.get("platform"),
        "architecture": capabilities.get("architecture"),
        "repositories": sorted(
            (dict(item) for item in repositories), key=lambda item: item["repository"]
        ),
        "runtime_assets": sorted(
            (dict(item) for item in runtime_assets), key=lambda item: item["repository"]
        ),
        "toolchains": [dict(item) for item in toolchains],
        "capabilities": dict(capabilities),
        "authority": dict(AUTHORITY),
    }
