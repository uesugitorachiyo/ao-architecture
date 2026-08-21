#!/usr/bin/env python3
"""Read-only Windows capability preflight with deterministic JSON output."""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

PROFILES = {
    "binary": ("git", "python", "powershell"),
    "ao-source": ("git", "python", "rustc", "cargo", "go", "powershell"),
    "go-node": ("git", "python", "go", "node", "npm", "powershell"),
}
ALIASES = ("\\WindowsApps\\", "/WindowsApps/", "App Installer")
TOOL_NAMES = {
    "python": ("python", "python3"),
    "powershell": ("pwsh", "powershell", "powershell.exe"),
    "git": ("git",),
    "rustc": ("rustc",),
    "cargo": ("cargo",),
    "go": ("go",),
    "node": ("node",),
    "npm": ("npm", "npm.cmd"),
}


def _run(args: list[str], env: dict[str, str]) -> tuple[int, str]:
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=5, env=env)
    except (OSError, subprocess.SubprocessError) as exc:
        return 1, str(exc)
    return result.returncode, (result.stdout or result.stderr).strip()


def _tool(name: str, env: dict[str, str]) -> dict[str, object]:
    path = next((shutil.which(candidate, path=env.get("PATH")) for candidate in TOOL_NAMES[name]), None)
    if not path:
        return {"status": "missing", "required": True, "path": None, "version": None}
    normalized = path.replace("/", "\\")
    alias = any(marker.lower() in normalized.lower() for marker in ALIASES)
    command = [path, "version"] if name == "go" else [path, "--version"]
    if name in {"npm", "node"}:
        command = [path, "--version"]
    code, version = _run(command, env)
    return {
        "status": "alias" if alias else ("present" if code == 0 else "unusable"),
        "required": True,
        "path": path,
        "version": version if code == 0 else None,
    }


def _check(name: str, status: str, detail: str, required: bool = True) -> dict[str, object]:
    return {"name": name, "status": status, "required": required, "detail": detail}


def run(profile: str, root: Path, env: dict[str, str] | None = None) -> dict[str, object]:
    env = dict(os.environ if env is None else env)
    required = set(PROFILES[profile])
    tools = {name: _tool(name, env) for name in TOOL_NAMES}
    checks: list[dict[str, object]] = []
    for name in PROFILES[profile]:
        item = tools[name]
        checks.append(_check(f"tool.{name}", "passed" if item["status"] == "present" else "failed", str(item["status"])))
    for name in sorted(set(TOOL_NAMES) - required):
        if tools[name]["status"] == "missing":
            tools[name]["required"] = False
    arch = platform.machine().lower()
    checks.append(_check("architecture", "passed" if arch in {"amd64", "x86_64", "arm64", "aarch64"} else "failed", arch))
    checks.append(_check("path_with_spaces", "passed" if " " in str(root) else "failed", str(root)))
    checks.append(_check("path_length", "passed" if len(str(root)) <= 240 else "failed", str(len(str(root)))))
    utf8 = env.get("PYTHONUTF8")
    checks.append(_check("python_utf8", "passed" if utf8 == "0" else "failed", f"PYTHONUTF8={utf8!r}"))
    code, autocrlf = _run(["git", "config", "--get", "core.autocrlf"], env)
    checks.append(_check("git_core_autocrlf", "passed" if code == 0 and autocrlf.lower() == "true" else "failed", autocrlf or "missing"))
    failed = [item["name"] for item in checks if item["status"] == "failed"]
    return {
        "schema": "ao.architecture.windows-preflight.v0.1",
        "profile": profile,
        "status": "passed" if not failed else "failed",
        "architecture": arch,
        "tools": tools,
        "checks": checks,
        "failed_checks": failed,
        "read_only": True,
        "system_mutation": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=sorted(PROFILES), default="binary")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = run(args.profile, args.root)
    if args.json:
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    else:
        print(f"windows_preflight={result['status']} profile={args.profile} failed={len(result['failed_checks'])}")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
