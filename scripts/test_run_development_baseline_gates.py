#!/usr/bin/env python3
"""Offline tests for the sequential development-baseline gate runner."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "run_development_baseline_gates.py"
SPEC = importlib.util.spec_from_file_location("run_development_baseline_gates", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load run_development_baseline_gates")
gates = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gates)


class GateRunnerTests(unittest.TestCase):
    def run_git(self, cwd: Path, *argv: str) -> str:
        completed = subprocess.run(
            ["git", *argv], cwd=cwd, text=True, capture_output=True, check=True
        )
        return completed.stdout.strip()

    def fixture(self, directory: str) -> tuple[Path, list[dict[str, object]]]:
        root = Path(directory) / "workspace with spaces"
        checkout = root / "fixture-repo"
        checkout.mkdir(parents=True)
        self.run_git(checkout, "init")
        self.run_git(checkout, "config", "user.name", "AO Fixture")
        self.run_git(checkout, "config", "user.email", "fixture@example.invalid")
        (checkout / "tracked.txt").write_text("stable\n", encoding="utf-8")
        (checkout / "pass_gate.py").write_text("print('pass')\n", encoding="utf-8")
        (checkout / "fail_gate.py").write_text("raise SystemExit(7)\n", encoding="utf-8")
        (checkout / "drift_gate.py").write_text(
            "from pathlib import Path\nPath('tracked.txt').write_text('drift\\n')\n",
            encoding="utf-8",
        )
        (checkout / "slow_gate.py").write_text("import time\ntime.sleep(5)\n", encoding="utf-8")
        (checkout / "large_gate.py").write_text("print('x' * 4096)\n", encoding="utf-8")
        self.run_git(checkout, "add", ".")
        self.run_git(checkout, "commit", "-m", "fixture")
        commit = self.run_git(checkout, "rev-parse", "HEAD")
        self.run_git(checkout, "remote", "add", "origin", str(checkout))
        self.run_git(checkout, "checkout", "--detach", commit)
        (root / ".ao-baseline").mkdir()
        repository = {
            "name": "fixture-repo",
            "path": "fixture-repo",
            "commit": commit,
            "upstream_url": str(checkout),
            "development_gates": [],
        }
        return root, [repository]

    def gate(
        self,
        identifier: str,
        script: str,
        *,
        timeout: int = 10,
        success_stdout: str = "any",
    ) -> dict[str, object]:
        return {
            "id": identifier,
            "argv": [sys.executable, script],
            "timeout_seconds": timeout,
            "shell": "direct",
            "required": True,
            "environment": {},
            "success_stdout": success_stdout,
        }

    def test_resolves_native_shells_without_command_strings(self) -> None:
        direct = gates.resolve_gate_argv(
            {"argv": ["npm", "--version"], "shell": "direct"},
            operating_system="nt",
            which=lambda command: rf"C:\tools\{command}.CMD",
        )
        self.assertEqual(direct[0], r"C:\tools\npm.CMD")
        windows_shell = gates.resolve_gate_argv(
            {"argv": ["scripts/check.sh", "--flag"], "shell": "posix-script"},
            operating_system="nt",
            which=lambda _command: r"C:\Program Files\Git\bin\bash.exe",
        )
        self.assertEqual(windows_shell, [r"C:\Program Files\Git\bin\bash.exe", "scripts/check.sh", "--flag"])
        macos_shell = gates.resolve_gate_argv(
            {"argv": ["scripts/check.sh"], "shell": "posix-script"},
            operating_system="posix",
        )
        self.assertEqual(macos_shell, ["/bin/sh", "scripts/check.sh"])
        with self.assertRaisesRegex(gates.GateError, "Git for Windows Bash"):
            gates.resolve_gate_argv(
                {"argv": ["scripts/check.sh"], "shell": "posix-script"},
                operating_system="nt",
                which=lambda _command: r"C:\Windows\System32\bash.exe",
            )

    def test_runs_in_manifest_order_with_bounded_hashed_logs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, repositories = self.fixture(directory)
            repositories[0]["development_gates"] = [
                self.gate("first", "pass_gate.py"),
                self.gate("second", "pass_gate.py"),
            ]
            output = Path(directory) / "gate logs"
            result = gates.run_gate_inventory(
                root, repositories, output, max_output_bytes=1024
            )
            self.assertEqual(result["status"], "pass")
            self.assertEqual([item["gate_id"] for item in result["gates"]], ["first", "second"])
            self.assertTrue(all(item["stdout_sha256"].startswith("sha256:") for item in result["gates"]))
            self.assertTrue(all("workspace" not in json.dumps(item) for item in result["gates"]))

    def test_preserves_failing_prefix_and_stops(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, repositories = self.fixture(directory)
            repositories[0]["development_gates"] = [
                self.gate("pass", "pass_gate.py"),
                self.gate("fail", "fail_gate.py"),
                self.gate("never", "pass_gate.py"),
            ]
            result = gates.run_gate_inventory(root, repositories, Path(directory) / "logs")
            self.assertEqual(result["status"], "fail")
            self.assertEqual([item["gate_id"] for item in result["gates"]], ["pass", "fail"])
            self.assertEqual(result["gates"][-1]["exit_status"], 7)

    def test_timeout_output_limit_format_output_and_drift_fail_closed(self) -> None:
        cases = (
            ("timeout", self.gate("timeout", "slow_gate.py", timeout=1), "timeout"),
            ("bounded", self.gate("bounded", "large_gate.py"), "output_limit"),
            ("format", self.gate("format", "pass_gate.py", success_stdout="empty"), "stdout_policy"),
            ("drift", self.gate("drift", "drift_gate.py"), "tracked_state_drift"),
        )
        for name, gate, category in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root, repositories = self.fixture(directory)
                repositories[0]["development_gates"] = [gate]
                result = gates.run_gate_inventory(
                    root,
                    repositories,
                    Path(directory) / "logs",
                    max_output_bytes=1024,
                )
                self.assertEqual(result["status"], "fail")
                self.assertEqual(result["gates"][0]["failure_category"], category)

    def test_rejects_unknown_gate_and_unsafe_output_reuse(self) -> None:
        repositories = [{"name": "fixture", "development_gates": [self.gate("known", "pass_gate.py")]}]
        with self.assertRaisesRegex(gates.GateError, "unknown gate"):
            gates.select_gate(repositories, "fixture", "missing")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "logs"
            output.mkdir()
            with self.assertRaisesRegex(gates.GateError, "output root must be absent"):
                gates.prepare_output_root(output)


if __name__ == "__main__":
    unittest.main()
