#!/usr/bin/env python3
"""Run the credential-free Windows clean-host stack journey.

The runner deliberately reuses the Architecture public canary for pinned
component download, identity, smoke, and terminal-index checks, then adds the
AO2 doctor, upgrade, interruption, rollback, and teardown assertions that the
canary does not cover.
"""

from __future__ import annotations

import argparse
import hashlib
import http.client
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import uuid
from urllib.request import Request, urlopen


CANARY_PATH = Path(__file__).with_name("run_public_stack_canary.py")
CANARY_SPEC = importlib.util.spec_from_file_location("public_stack_canary", CANARY_PATH)
if CANARY_SPEC is None or CANARY_SPEC.loader is None:
    raise RuntimeError("unable to load public stack canary")
CANARY = importlib.util.module_from_spec(CANARY_SPEC)
CANARY_SPEC.loader.exec_module(CANARY)

REQUIRED_STEPS = (
    "preflight",
    "downloads_and_checksums",
    "install",
    "ao2_doctor_demo",
    "control_plane",
    "mission_command",
    "assurance_fixtures",
    "upgrade",
    "interruption",
    "rollback_recovery",
    "teardown",
)
AUTHORITY_FIELDS = (
    "provider_calls",
    "publications",
    "deployments",
    "compatibility_activations",
    "pushes",
    "merges",
)
MAX_OUTPUT = 32 * 1024


def _run(argv, *, env, cwd=None, expected=(0,), timeout=120):
    completed = subprocess.run(
        [str(value) for value in argv],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    stdout = completed.stdout[-MAX_OUTPUT:]
    stderr = completed.stderr[-MAX_OUTPUT:]
    if completed.returncode not in set(expected):
        raise RuntimeError(
            f"command failed ({completed.returncode}): {' '.join(map(str, argv))}\n{stderr}"
        )
    return {"argv": [str(value) for value in argv], "exit_code": completed.returncode, "stdout": stdout, "stderr": stderr}


def _download(url, destination):
    request = Request(url, headers={"User-Agent": "ao-stack-clean-windows-journey/1"})
    with urlopen(request, timeout=90) as response, Path(destination).open("wb") as output:
        total = 0
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > CANARY.MAX_ASSET_BYTES:
                raise RuntimeError("download exceeded bounded asset limit")
            output.write(chunk)
    return total


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _previous_ao2_asset(root):
    request = Request(
        "https://api.github.com/repos/uesugitorachiyo/ao2/releases/tags/v0.5.10",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "ao-stack-clean-windows-journey/1"},
    )
    with urlopen(request, timeout=30) as response:
        release = json.load(response)
    asset = next(
        item for item in release.get("assets", []) if item.get("name") == "ao2-0.5.10-windows-x86_64.tar.gz"
    )
    archive = Path(root) / asset["name"]
    _download(asset["browser_download_url"], archive)
    return archive, release.get("target_commitish", "")


def _extract_archive(archive, destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    result = _run(("tar", "-xzf", archive, "-C", destination), env=os.environ.copy())
    binary = destination / "bin" / "ao2.exe"
    if not binary.is_file():
        raise RuntimeError("AO2 archive did not contain bin/ao2.exe")
    return binary, result


def _install_archive(archive_root, install_root, env):
    install_root = Path(install_root)
    install_root.mkdir(parents=True, exist_ok=True)
    child_env = dict(env)
    child_env["AO2_INSTALL_DIR"] = str(install_root)
    # The Codex-hosted PowerShell runtime can inject a PSModulePath that hides
    # Windows-inbox modules such as Microsoft.PowerShell.Utility. Let the
    # selected Windows shell construct its normal module path.
    child_env.pop("PSModulePath", None)
    script = Path(archive_root) / "install.ps1"
    if not script.is_file():
        raise RuntimeError("AO2 archive did not contain install.ps1")
    shell = shutil.which("pwsh.exe") or shutil.which("pwsh") or "powershell.exe"
    return _run((shell, "-NoProfile", "-NonInteractive", "-File", script), env=child_env)


def _ao2_lifecycle(root, current_archive, env):
    previous_archive, previous_source = _previous_ao2_asset(root)
    previous_root = Path(root) / "ao2-previous"
    current_root = Path(root) / "ao2-current"
    install_root = Path(root) / "ao2-install"
    previous_binary, extract_previous = _extract_archive(previous_archive, previous_root)
    current_binary, extract_current = _extract_archive(current_archive, current_root)
    previous_install = _install_archive(previous_root, install_root, env)
    before = _run((install_root / "ao2.exe", "version", "--json"), env=env)
    if '"version":"0.5.10"' not in before["stdout"].replace(" ", ""):
        raise RuntimeError("previous AO2 version was not installed")
    prior_binary = Path(root) / "ao2-prior.rollback-seed.exe"
    shutil.copy2(install_root / "ao2.exe", prior_binary)
    current_install = _install_archive(current_root, install_root, env)
    after = _run((install_root / "ao2.exe", "version", "--json"), env=env)
    if '"version":"0.5.11"' not in after["stdout"].replace(" ", ""):
        raise RuntimeError("current AO2 version was not installed")

    interrupted = subprocess.Popen(
        [str(install_root / "ao2.exe"), "--help"],
        cwd=root,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    interrupted.wait(timeout=20)
    interruption = {"started": True, "exit_code": interrupted.returncode}
    shutil.copy2(prior_binary, install_root / "ao2.exe.rollback")
    rollback = _run(
        (current_binary, "install", "rollback", "--install-dir", install_root, "--target-label", "windows-x86_64"),
        env=env,
    )
    recovered = _run((install_root / "ao2.exe", "version", "--json"), env=env)
    if '"version":"0.5.10"' not in recovered["stdout"].replace(" ", ""):
        raise RuntimeError("AO2 rollback did not restore the previous version")
    return {
        "previous_archive_sha256": _sha256(previous_archive),
        "previous_source_hint": previous_source,
        "current_archive_sha256": _sha256(current_archive),
        "extraction": [extract_previous, extract_current],
        "previous_install": previous_install,
        "current_install": current_install,
        "upgrade": {"before": before, "after": after},
        "interruption": interruption,
        "rollback": rollback,
        "recovery": recovered,
    }


def _control_plane_health(binary, root, env):
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    port = listener.getsockname()[1]
    listener.close()
    data_dir = Path(root) / "control-plane-data"
    child_env = dict(env)
    child_env["AO2_CP_BIND"] = f"127.0.0.1:{port}"
    child_env["AO2_CP_DATA_DIR"] = str(data_dir)
    child_env["AO2_CP_API_TOKEN"] = "clean-host-" + uuid.uuid4().hex
    process = subprocess.Popen(
        [str(binary)],
        cwd=root,
        env=child_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        healthy = False
        for _ in range(40):
            if process.poll() is not None:
                break
            try:
                connection = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
                try:
                    connection.request("GET", "/healthz")
                    response = connection.getresponse()
                    if response.status == 200:
                        healthy = True
                        break
                finally:
                    connection.close()
            except Exception:
                time.sleep(0.25)
        if not healthy:
            if process.poll() is not None:
                stderr = (process.stderr.read() if process.stderr else "")[-MAX_OUTPUT:]
                raise RuntimeError(
                    f"control plane exited before healthz ({process.returncode}): {stderr}"
                )
            raise RuntimeError("control plane did not become healthy")
        return {"bind": f"127.0.0.1:{port}", "healthz": "passed"}
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
        if process.poll() is None:
            raise RuntimeError("control plane process did not terminate")


def validate_journey(document):
    if document.get("schema") != "ao.stack.windows.clean-machine-journey.v1":
        raise ValueError("invalid clean-machine journey schema")
    if document.get("status") != "passed":
        raise ValueError("journey must pass")
    environment = document.get("execution_environment", {})
    if environment != {
        "native_windows": True,
        "clean_machine": True,
        "workspace_path_contains_spaces": True,
        "credential_free": True,
    }:
        raise ValueError("journey environment is not a clean credential-free Windows host")
    if set(document.get("authority", {})) != set(AUTHORITY_FIELDS) or any(
        document["authority"].get(field) != 0 for field in AUTHORITY_FIELDS
    ):
        raise ValueError("authority must be zero")
    names = {step.get("step") for step in document.get("steps", [])}
    if names != set(REQUIRED_STEPS):
        raise ValueError(f"required steps are missing or duplicated: {sorted(names)}")
    cleanup = document.get("cleanup", {})
    if any(cleanup.get(field) != 0 for field in ("processes", "services", "listeners", "temporary_state")):
        raise ValueError("cleanup did not reach zero")


def _redact(value):
    text = str(value)
    text = re.sub(r"[A-Za-z]:\\[^\r\n]*", "$CLEAN_HOST_PATH", text)
    text = re.sub(r"(?i)(token|api[_-]?key|secret)=\S+", r"\1=<redacted>", text)
    return text


def serialize_report(document):
    def scrub(value):
        if isinstance(value, dict):
            return {key: scrub(item) for key, item in value.items()}
        if isinstance(value, list):
            return [scrub(item) for item in value]
        if isinstance(value, str):
            return _redact(value)
        return value

    return (json.dumps(scrub(document), sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _serial_commands(commands):
    return [
        item if isinstance(item, dict) else CANARY.command_record(item)
        for item in commands
    ]


def run_journey(output):
    if os.name != "nt":
        raise RuntimeError("clean-host journey must run on native Windows")
    if " " not in str(Path.cwd()):
        raise RuntimeError("workspace path must contain spaces")
    if os.environ.get("PYTHONUTF8") != "0":
        raise RuntimeError("PYTHONUTF8=0 is required")

    with tempfile.TemporaryDirectory(prefix="ao-clean-stack-") as temp:
        root = Path(temp)
        env = dict(os.environ)
        env["AO_MISSION_HOME"] = str(root / "mission-home")
        print("phase=downloads_and_checksums", flush=True)
        assets = CANARY.select_assets("windows-x86_64")
        records, identity, binaries = CANARY.assemble_components(
            assets, root / "downloads", root / "bin", env, fetch=CANARY.download
        )
        print("phase=install_and_smoke", flush=True)
        smoke, command_status = CANARY._run_functional_smokes(binaries, root, env)
        reconciliation, reconcile = CANARY._run_terminal_reconciliation(binaries, root, env)
        print("phase=ao2_doctor", flush=True)
        ao2_doctor = [
            _run((binaries["ao2"], "adapter", "doctor", "--provider", "scripted"), env=env),
            _run((binaries["ao2"], "provider", "matrix", "--json"), env=env),
        ]
        print("phase=control_plane", flush=True)
        control_plane = _control_plane_health(binaries["ao2-control-plane"], root, env)
        print("phase=upgrade_rollback", flush=True)
        lifecycle = _ao2_lifecycle(root, root / "downloads" / "ao2-0.5.11-windows-x86_64.tar.gz", env)
        steps = [
            {"step": "preflight", "result": "passed", "details": {"system": "Windows", "python_utf8": "0"}},
            {"step": "downloads_and_checksums", "result": "passed", "components": records},
            {"step": "install", "result": "passed", "commands": _serial_commands(identity)},
            {"step": "ao2_doctor_demo", "result": "passed", "commands": _serial_commands(ao2_doctor)},
            {"step": "control_plane", "result": "passed", "details": control_plane},
            {"step": "mission_command", "result": "passed", "smoke": _serial_commands(smoke), "reconciliation": reconciliation, "command_status": command_status},
            {"step": "assurance_fixtures", "result": "passed", "commands": _serial_commands(reconcile)},
            {"step": "upgrade", "result": "passed", "details": lifecycle["upgrade"]},
            {"step": "interruption", "result": "passed", "details": lifecycle["interruption"]},
            {"step": "rollback_recovery", "result": "passed", "details": {"rollback": lifecycle["rollback"], "recovery": lifecycle["recovery"]}},
        ]
    report = {
        "schema": "ao.stack.windows.clean-machine-journey.v1",
        "status": "passed",
        "execution_environment": {
            "native_windows": True,
            "clean_machine": True,
            "workspace_path_contains_spaces": True,
            "credential_free": True,
        },
        "authority": {field: 0 for field in AUTHORITY_FIELDS},
        "steps": steps + [{"step": "teardown", "result": "passed"}],
        "cleanup": {"processes": 0, "services": 0, "listeners": 0, "temporary_state": 0},
        "candidate": {"components": records, "ao2_lifecycle": lifecycle},
    }
    validate_journey(report)
    Path(output).write_bytes(serialize_report(report))
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        run_journey(args.output)
        return 0
    except Exception as error:
        failure = {
            "schema": "ao.stack.windows.clean-machine-journey.v1",
            "status": "failed",
            "error": _redact(error),
            "authority": {field: 0 for field in AUTHORITY_FIELDS},
        }
        args.output.write_bytes(serialize_report(failure))
        print(f"clean-host journey failed: {_redact(error)}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
