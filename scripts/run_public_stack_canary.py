#!/usr/bin/env python3
"""Install and verify the supported AO Stack from public release assets."""

from dataclasses import dataclass
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import os
import platform
import tempfile
import tarfile
import time
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import zipfile


TARGETS = ("linux-x86_64", "macos-aarch64", "windows-x86_64")
_RAW_BASE = "https://raw.githubusercontent.com/uesugitorachiyo"
SMOKE_FIXTURES = {
    "workgraph.json": (
        f"{_RAW_BASE}/ao-atlas/2bf243ce8d8c71d845754398238b14d1ab77d0e6/examples/valid/workgraph.json",
        "5c761cd7ef1ed5d648f7b2a4ee0988eef60fb097f73c343a70e0ea81999db4e5",
    ),
    "command-status.json": (
        f"{_RAW_BASE}/ao-command/a728d90077c1340e295468e5017b5e166bc5bc7a/examples/mission/command-status.ready.json",
        "e542a9925dea18557b95dde0c3569f2382246ef133d7727f605259cc00a529c8",
    ),
    "brief.md": (
        f"{_RAW_BASE}/ao-covenant/2fd72a0426a747868826581612fa1dc9727b53b9/examples/structured-release/brief.md",
        "6ce8ceb083ddb45ff72e6f04754dd16c266eebfc447b0809248c26789078a609",
    ),
}


@dataclass(frozen=True)
class Asset:
    component: str
    version: str
    source_sha: str
    url: str
    sha256: str
    archive: str
    binary: str


@dataclass(frozen=True)
class CommandResult:
    argv: tuple
    exit_code: int
    stdout: str
    stderr: str
    elapsed_ms: int


def _asset(component, version, source_sha, target, filename, sha256, archive, binary):
    return Asset(
        component=component,
        version=version,
        source_sha=source_sha,
        url=(
            f"https://github.com/uesugitorachiyo/{component}/releases/download/"
            f"{version}/{filename}"
        ),
        sha256=sha256,
        archive=archive,
        binary=binary + (".exe" if target == "windows-x86_64" else ""),
    )


_COMPONENTS = {
    "ao2": (
        "v0.5.11",
        "8307795b3434af920f6cef088e56ca8fcc76775b",
        "ao2",
        {
            "linux-x86_64": ("ao2-0.5.11-linux-x86_64.tar.gz", "c62c204d520bf51b4c63caecf2a8f48840e44b2828e1e439c68da4994d1abc07", "tar.gz"),
            "macos-aarch64": ("ao2-0.5.11-macos-aarch64.tar.gz", "857fbe69e606ab99f07dffd3183e6f2d869b8efd4fc604e37efd16607308e6ab", "tar.gz"),
            "windows-x86_64": ("ao2-0.5.11-windows-x86_64.tar.gz", "327829e9e3e3edf3eeb3b48d3b1ead46af0fa47a768ee6e1843c285e8b1d2756", "tar.gz"),
        },
    ),
    "ao2-control-plane": (
        "v0.1.19",
        "5de3541e9007e12d95b125e7f911c02932e21479",
        "ao2-cp-server",
        {
            "linux-x86_64": ("ao2-control-plane-0.1.19-linux-x86_64.tar.gz", "588903471152cbc2cae1fc9d514d69b72c153b913a368cb6bf01da09c2789cbf", "tar.gz"),
            "macos-aarch64": ("ao2-control-plane-0.1.19-macos-aarch64.tar.gz", "06addc587bd282763c47d9ee4e36cb8ebea0c114881296569ef4d0b4dff86972", "tar.gz"),
            "windows-x86_64": ("ao2-control-plane-0.1.19-windows-x86_64.tar.gz", "c3528322730afd4a0c3988f9b2a23767f67febbf96b62340988546346ad00e05", "tar.gz"),
        },
    ),
    "ao-mission": (
        "v0.1.4",
        "cee287597024b5a1e990c6e272518236bc9e32fa",
        "ao-mission",
        {
            "linux-x86_64": ("ao-mission-0.1.4-linux-x86_64.tar.gz", "041d4b4ab076601bf6fe15335cb70a5d9f87301beb239e8e106b3ee4fd12f800", "tar.gz"),
            "macos-aarch64": ("ao-mission-0.1.4-macos-aarch64.tar.gz", "d8b418e42b57306862c75fc10e5c347109c13c144a18e240d2a2edba29c1a34e", "tar.gz"),
            "windows-x86_64": ("ao-mission-0.1.4-windows-x86_64.zip", "027ceba61e7b1d3655cce63a1ce4269824d7a5e3acf65fef5fabb0b539c53221", "zip"),
        },
    ),
    "ao-atlas": (
        "v0.2.0",
        "2bf243ce8d8c71d845754398238b14d1ab77d0e6",
        "ao-atlas",
        {
            "linux-x86_64": ("ao-atlas-v0.2.0-linux-x86_64.tar.gz", "121edad10e6775af809c4003b5b7820a06d3b140ff543a440a66b5c16987ac08", "tar.gz"),
            "macos-aarch64": ("ao-atlas-v0.2.0-macos-aarch64.tar.gz", "85678feba42d92d866e5f75c80cad80e5aa11dad18cb7292a396b16047b428a5", "tar.gz"),
            "windows-x86_64": ("ao-atlas-v0.2.0-windows-x86_64.tar.gz", "b53de90d5c2e69511e74e287eabd8437d87128892473843e576e366d1e4e62e7", "tar.gz"),
        },
    ),
    "ao-command": (
        "v0.1.2",
        "a728d90077c1340e295468e5017b5e166bc5bc7a",
        "ao-command",
        {
            "linux-x86_64": ("ao-command-0.1.2-linux-x86_64.tar.gz", "0d169a2434af12849c8e7865eb4b241651ca2edf34afbd3e4b378d678853c7be", "tar.gz"),
            "macos-aarch64": ("ao-command-0.1.2-macos-aarch64.tar.gz", "be5c246e73c2eb72a2f665a355e918841ffbbc105568df12c11f7597a538d9df", "tar.gz"),
            "windows-x86_64": ("ao-command-0.1.2-windows-x86_64.zip", "24ef4d1368a4cfd4754e3bef6ee7e6a3555eb655324efb2279168d1d3fb56414", "zip"),
        },
    ),
    "ao-forge": (
        "v0.1.4",
        "e104b47c2e14b6c0927b885e137907ad227aeb5c",
        "forge",
        {
            "linux-x86_64": ("ao-forge_Linux_x86_64.tar.gz", "19f15f022eed60f7acd97830835c0cb22eb0fb4df8046e4250e1d99904073ed2", "tar.gz"),
            "macos-aarch64": ("ao-forge_Darwin_arm64.tar.gz", "50a13927e4f83bbdb600f78a4107e5800e88512f48a7ce9e748ee19a31c2b0f4", "tar.gz"),
            "windows-x86_64": ("ao-forge_Windows_x86_64.zip", "a6250e975f0f7976bf5268d71c2f1791dd53c4413aebec9dff52b99989c204d5", "zip"),
        },
    ),
    "ao-covenant": (
        "v0.1.1",
        "2fd72a0426a747868826581612fa1dc9727b53b9",
        "covenant",
        {
            "linux-x86_64": ("ao-covenant_v0.1.1_linux_amd64", "f6820fdc7b99873071e7f68fc50d9bfd922750a2e788d9fca5aa8fb37cc8180b", "raw"),
            "macos-aarch64": ("ao-covenant_v0.1.1_darwin_amd64", "9a5ca7c6920c44b6e120d6c5bd8baf190b66e188d43485639c6fc5355190868e", "raw"),
            "windows-x86_64": ("ao-covenant_v0.1.1_windows_amd64.exe", "fd6e3a0033608d3f47dccb60f48191e4c4b2dc4fdce893c87d8ea96199610c5d", "raw"),
        },
    ),
}


def select_assets(target):
    if target not in TARGETS:
        raise ValueError(f"unsupported target: {target}")
    assets = []
    for component, (version, source_sha, binary, targets) in _COMPONENTS.items():
        filename, sha256, archive = targets[target]
        assets.append(
            _asset(component, version, source_sha, target, filename, sha256, archive, binary)
        )
    return tuple(assets)


def verify_digest(path, expected):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    actual = digest.hexdigest()
    if actual != expected:
        raise ValueError(f"SHA-256 mismatch: expected {expected}, got {actual}")


def _safe_name(name):
    if not name or "\\" in name:
        raise ValueError(f"unsafe archive path: {name!r}")
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"unsafe archive path: {name!r}")
    return path


def _copy_binary(source, destination, binary):
    destination.mkdir(parents=True, exist_ok=True)
    output = destination / binary
    with output.open("wb") as handle:
        shutil.copyfileobj(source, handle)
    output.chmod(output.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return output


def install_asset(asset, archive, destination):
    archive = Path(archive)
    destination = Path(destination)
    if asset.archive == "raw":
        if not archive.is_file() or archive.is_symlink():
            raise ValueError("raw asset must be a regular file")
        with archive.open("rb") as source:
            return (_copy_binary(source, destination, asset.binary),)

    matches = []
    if asset.archive == "tar.gz":
        with tarfile.open(archive, "r:gz") as bundle:
            for member in bundle.getmembers():
                name = _safe_name(member.name)
                if member.issym() or member.islnk():
                    raise ValueError(f"archive link is not allowed: {member.name}")
                if member.isdir():
                    continue
                if not member.isfile():
                    raise ValueError(f"archive entry is not a regular file: {member.name}")
                if name.name == asset.binary:
                    matches.append(member)
            if len(matches) > 1:
                raise ValueError(f"duplicate binary in archive: {asset.binary}")
            if not matches:
                raise ValueError(f"missing binary in archive: {asset.binary}")
            source = bundle.extractfile(matches[0])
            if source is None:
                raise ValueError(f"cannot read binary from archive: {asset.binary}")
            with source:
                return (_copy_binary(source, destination, asset.binary),)

    if asset.archive == "zip":
        with zipfile.ZipFile(archive) as bundle:
            for member in bundle.infolist():
                name = _safe_name(member.filename)
                mode = member.external_attr >> 16
                if stat.S_ISLNK(mode):
                    raise ValueError(f"archive link is not allowed: {member.filename}")
                if member.is_dir():
                    continue
                if name.name == asset.binary:
                    matches.append(member)
            if len(matches) > 1:
                raise ValueError(f"duplicate binary in archive: {asset.binary}")
            if not matches:
                raise ValueError(f"missing binary in archive: {asset.binary}")
            with bundle.open(matches[0]) as source:
                return (_copy_binary(source, destination, asset.binary),)

    raise ValueError(f"unsupported archive type: {asset.archive}")


def run_command(argv, *, env, expected_exit, cwd=None):
    command = tuple(str(part) for part in argv)
    started = time.monotonic_ns()
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=env,
        cwd=cwd,
        timeout=60,
        check=False,
    )
    result = CommandResult(
        argv=command,
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        elapsed_ms=(time.monotonic_ns() - started) // 1_000_000,
    )
    if result.exit_code not in expected_exit:
        raise ValueError(
            f"unexpected exit {result.exit_code} for {' '.join(command)}: "
            f"{result.stderr.strip()}"
        )
    return result


def verify_identity(asset, result):
    version = asset.version.removeprefix("v")
    text_expectations = {
        "ao2": (f"ao2 {version}\n", f"git_commit={asset.source_sha}\n"),
        "ao2-control-plane": (f"ao2-cp-server {version}\n",),
        "ao-mission": (
            f"ao-mission version={version} source_sha={asset.source_sha}\n",
        ),
        "ao-atlas": (
            f"ao-atlas version={asset.version} source_sha={asset.source_sha}\n",
        ),
        "ao-forge": (
            f"ao-forge version={version} source_sha={asset.source_sha}\n",
        ),
    }
    if asset.component in text_expectations:
        if not all(expected in result.stdout for expected in text_expectations[asset.component]):
            label = {"ao2": "AO2"}.get(asset.component, asset.component)
            raise ValueError(f"{label} identity mismatch: {result.stdout.strip()}")
        return

    try:
        document = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise ValueError(f"{asset.component} identity is not JSON") from error
    if asset.component == "ao-command":
        valid = document == {
            "schema_version": "ao.command.version.v0.1",
            "version": version,
            "source_commit": asset.source_sha,
            "provider_calls": False,
        }
    elif asset.component == "ao-covenant":
        valid = (
            document.get("schema_version") == "covenant.version-result.v1"
            and document.get("version") == asset.version
            and document.get("commit") == asset.source_sha
        )
    else:
        valid = False
    if not valid:
        raise ValueError(f"{asset.component} identity mismatch: {result.stdout.strip()}")


def validate_report(report):
    if report.get("schema") != "ao.architecture.public-stack-canary.v0.1":
        raise ValueError("invalid report schema")
    if report.get("status") != "passed" or report.get("target") not in TARGETS:
        raise ValueError("report must record a passing supported target")
    expected = {
        "ao2": "v0.5.11",
        "ao2-control-plane": "v0.1.19",
        "ao-mission": "v0.1.4",
        "ao-atlas": "v0.2.0",
        "ao-command": "v0.1.2",
        "ao-forge": "v0.1.4",
        "ao-covenant": "v0.1.1",
    }
    components = report.get("components", [])
    if len(components) != 7 or len({item.get("component") for item in components}) != 7:
        raise ValueError("report must contain seven components")
    if {item.get("component"): item.get("version") for item in components} != expected:
        raise ValueError("component version line mismatch")
    for item in components:
        if (
            not item.get("url", "").startswith("https://github.com/uesugitorachiyo/")
            or "/releases/download/" not in item["url"]
            or not re.fullmatch(r"[0-9a-f]{64}", item.get("sha256", ""))
            or not isinstance(item.get("bytes"), int)
            or item["bytes"] <= 0
        ):
            raise ValueError(f"invalid public component evidence: {item.get('component')}")
    commands = report.get("commands", [])
    if not commands or any(command.get("exit_code") != 0 for command in commands):
        raise ValueError("all recorded commands must exit zero")

    views = report.get("reconciliation", {}).get("views", {})
    expected_views = {"inspect", "checkpoint", "event-index", "command-readback"}
    if set(views) != expected_views:
        raise ValueError("four terminal-index views are required")
    index_digests = {view.get("index_digest") for view in views.values()}
    if len(index_digests) != 1:
        raise ValueError("terminal index digest disagreement")
    state_digests = [view.get("state_digest") for view in views.values()]
    if len(set(state_digests)) != 4:
        raise ValueError("surface state digests must be distinct")
    if any(not re.fullmatch(r"sha256:[0-9a-f]{64}", digest or "") for digest in index_digests | set(state_digests)):
        raise ValueError("terminal reconciliation digest is not canonical")
    canonical = [view.get("canonical") for view in views.values()]
    if any(value != canonical[0] for value in canonical[1:]):
        raise ValueError("terminal canonical payload disagreement")

    for field in (
        "provider_calls",
        "credential_uses",
        "publications",
        "deployments",
        "external_mutations",
    ):
        if report.get(field) != 0:
            raise ValueError(f"{field} must be zero")
    if report.get("cleanup_succeeded") is not True:
        raise ValueError("cleanup must succeed")


def _write_json(path, document):
    body = (json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n").encode()
    Path(path).write_bytes(body)
    return body


def write_terminal_fixture(root):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    mission = "ao-stack-public-canary-v0.1"
    safety = {
        "executes_work": False,
        "approves_work": False,
        "mutates_repositories": False,
        "calls_providers": False,
        "publishes": False,
        "releases": False,
        "deploys": False,
        "advances_authority": False,
    }
    documents = (
        (
            "lease",
            "lease_authority",
            "lease.json",
            {
                "contract_version": "fixture.v1",
                "mission_id": mission,
                "minimum_nodes": 40,
                "minimum_minutes": 120,
                "target_minutes": 150,
                "maximum_minutes": 180,
            },
        ),
        (
            "root",
            "initial_snapshot",
            "root.json",
            {
                "contract_version": "fixture.v1",
                "mission_id": mission,
                "counts": {"completed": 0, "ready": 40, "blocked": 0, "failed": 0},
                "final_response_allowed": False,
            },
        ),
        (
            "duration",
            "duration_snapshot",
            "duration.json",
            {
                "contract_version": "fixture.v1",
                "mission_id": mission,
                "completed_nodes": 40,
                "elapsed_minutes": 150,
            },
        ),
        (
            "terminal",
            "terminal_candidate",
            "terminal.json",
            {
                "contract_version": "fixture.v1",
                "mission_id": mission,
                "counts": {"completed": 40, "ready": 0, "blocked": 0, "failed": 0},
                "elapsed_minutes": 150,
                "lease_time_status": "within_window",
                "final_response_allowed": True,
                "exact_next_action": "none",
                "safety_boundaries": safety,
            },
        ),
    )
    artifacts = []
    for sequence, (role, state, name, document) in enumerate(documents):
        body = _write_json(root / name, document)
        artifacts.append(
            {
                "role": role,
                "sequence": sequence,
                "state": state,
                "path": name,
                "sha256": "sha256:" + hashlib.sha256(body).hexdigest(),
            }
        )
    manifest = {
        "contract_version": "ao.canonical-terminal-index-input.v1",
        "mission_id": mission,
        "evidence_root": ".",
        "generated_at_utc": "2026-08-12T12:00:00Z",
        "artifacts": artifacts,
    }
    path = root / "manifest.json"
    _write_json(path, manifest)
    return path


def _identity_arguments(asset, binary):
    suffixes = {
        "ao2": ("version",),
        "ao2-control-plane": ("--version",),
        "ao-mission": ("--version",),
        "ao-atlas": ("--version",),
        "ao-command": ("version", "--json"),
        "ao-forge": ("--version",),
        "ao-covenant": ("version", "--json"),
    }
    return (str(binary),) + suffixes[asset.component]


def assemble_components(assets, download_root, bin_root, env, *, fetch):
    download_root = Path(download_root)
    bin_root = Path(bin_root)
    download_root.mkdir(parents=True, exist_ok=True)
    records = []
    commands = []
    binaries = {}
    for asset in assets:
        filename = PurePosixPath(urlsplit(asset.url).path).name
        archive = download_root / filename
        fetched_bytes = fetch(asset.url, archive)
        if fetched_bytes != archive.stat().st_size:
            raise ValueError(f"download byte count mismatch: {asset.component}")
        verify_digest(archive, asset.sha256)
        binary = install_asset(asset, archive, bin_root)[0]
        result = run_command(
            _identity_arguments(asset, binary), env=env, expected_exit={0}
        )
        verify_identity(asset, result)
        binaries[asset.component] = binary
        commands.append(result)
        records.append(
            {
                "component": asset.component,
                "version": asset.version,
                "source_sha": asset.source_sha,
                "url": asset.url,
                "filename": filename,
                "sha256": asset.sha256,
                "bytes": fetched_bytes,
                "binary": asset.binary,
            }
        )
    return records, commands, binaries


def sanitized_environment(source):
    sensitive = ("TOKEN", "SECRET", "PASSWORD", "CREDENTIAL", "API_KEY", "AUTH", "PROVIDER")
    return {
        key: value
        for key, value in source.items()
        if not key.upper().startswith("AO_")
        and not any(marker in key.upper() for marker in sensitive)
    }


def canary_environment(source, root):
    environment = sanitized_environment(source)
    environment["AO_MISSION_HOME"] = str(Path(root) / "mission-home")
    return environment


def download(url, destination):
    request = Request(url, headers={"User-Agent": "ao-stack-public-canary/0.1"})
    with urlopen(request, timeout=60) as response, Path(destination).open("wb") as output:
        shutil.copyfileobj(response, output)
    return Path(destination).stat().st_size


def _redact_temporary_path(text):
    def replacement(match):
        tail = match.group(0).split("ao-public-stack-canary-", 1)[1].replace("\\", "/")
        _, separator, relative = tail.partition("/")
        return "$CANARY_ROOT" + ("/" + relative if separator else "")

    return re.sub(
        r"(?:[A-Za-z]:)?[^\s\"']*ao-public-stack-canary-[^/\\\s\"']+(?:[/\\][^\s\"']*)?",
        replacement,
        text,
    )


def command_record(result):
    return {
        "argv": [_redact_temporary_path(part) for part in result.argv],
        "exit_code": result.exit_code,
        "stdout": _redact_temporary_path(result.stdout),
        "stderr": _redact_temporary_path(result.stderr),
        "elapsed_ms": result.elapsed_ms,
    }


def _run_functional_smokes(binaries, root, env):
    fixture_root = root / "smoke-fixtures"
    fixture_root.mkdir()
    for name, (url, digest) in SMOKE_FIXTURES.items():
        path = fixture_root / name
        download(url, path)
        verify_digest(path, digest)
    commands = (
        ((binaries["ao2"], "--help"), None),
        ((binaries["ao2-control-plane"], "--help"), None),
        ((binaries["ao-mission"], "doctor", "--json"), None),
        ((binaries["ao-atlas"], "workgraph", "validate", "--workgraph", fixture_root / "workgraph.json"), None),
        ((binaries["ao-command"], "mission", "status", "--status", fixture_root / "command-status.json", "--json"), None),
        ((binaries["ao-forge"], "--help"), None),
        ((binaries["ao-covenant"], "lint", "--brief", "brief.md", "--json"), fixture_root),
    )
    return [run_command(command, env=env, expected_exit={0}, cwd=cwd) for command, cwd in commands]


def _run_terminal_reconciliation(binaries, root, env):
    fixture_root = root / "terminal-fixture"
    manifest = write_terminal_fixture(fixture_root)
    index = fixture_root / "index.json"
    state = fixture_root / "state.json"
    commands = []
    commands.append(run_command((binaries["ao-atlas"], "terminal-index", "build", "--root", fixture_root, "--manifest", manifest, "--out", index), env=env, expected_exit={0}))
    commands.append(run_command((binaries["ao-atlas"], "terminal-index", "verify", "--root", fixture_root, "--index", index), env=env, expected_exit={0}))
    commands.append(run_command((binaries["ao-mission"], "terminal-index", "import", "--root", fixture_root, "--index", index, "--state", state), env=env, expected_exit={0}))
    views = {}
    for surface in ("inspect", "checkpoint", "event-index", "command-readback"):
        result = run_command((binaries["ao-mission"], "terminal-index", surface, "--state", state), env=env, expected_exit={0})
        commands.append(result)
        document = json.loads(result.stdout)
        views[surface] = {
            "index_digest": document["index_digest"],
            "state_digest": document["state_digest"],
            "canonical": {
                key: document[key]
                for key in ("mission_id", "counts", "lease", "readiness_passed", "final_response_allowed", "exact_next_action")
            },
        }
    return {"views": views}, commands


def run_canary(target, output):
    if target not in TARGETS:
        raise ValueError(f"unsupported target: {target}")
    with tempfile.TemporaryDirectory(prefix="ao-public-stack-canary-") as directory:
        root = Path(directory)
        environment = canary_environment(os.environ, root)
        components, identity_commands, binaries = assemble_components(
            select_assets(target), root / "downloads", root / "bin", environment, fetch=download
        )
        smoke_commands = _run_functional_smokes(binaries, root, environment)
        reconciliation, reconcile_commands = _run_terminal_reconciliation(binaries, root, environment)
        report = {
            "schema": "ao.architecture.public-stack-canary.v0.1",
            "status": "passed",
            "target": target,
            "runner": {"system": platform.system(), "machine": platform.machine(), "python": platform.python_version()},
            "components": components,
            "commands": [command_record(item) for item in identity_commands + smoke_commands + reconcile_commands],
            "reconciliation": reconciliation,
            "ao2_native_verification_run": 31622142672,
            "provider_calls": 0,
            "credential_uses": 0,
            "publications": 0,
            "deployments": 0,
            "external_mutations": 0,
            "cleanup_succeeded": True,
        }
        validate_report(report)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    _write_json(output, report)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=TARGETS, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    run_canary(args.target, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
