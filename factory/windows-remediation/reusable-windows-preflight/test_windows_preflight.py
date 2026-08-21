import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import windows_preflight  # noqa: E402


class WindowsPreflightTests(unittest.TestCase):
    def test_machine_readable_binary_profile_reports_schema_and_read_only(self):
        result = windows_preflight.run("binary", Path("C:/AO spaced root"), {**os.environ, "PYTHONUTF8": "0"})
        self.assertEqual(result["schema"], "ao.architecture.windows-preflight.v0.1")
        self.assertTrue(result["read_only"])
        self.assertFalse(result["system_mutation"])
        json.dumps(result)

    def test_missing_required_tool_is_failed_with_remediation_classification(self):
        with tempfile.TemporaryDirectory() as directory:
            env = {**os.environ, "PATH": directory, "PYTHONUTF8": "0"}
            result = windows_preflight.run("go-node", Path("C:/AO spaced root"), env)
        self.assertEqual(result["status"], "failed")
        self.assertIn("tool.go", result["failed_checks"])
        self.assertEqual(result["tools"]["go"]["status"], "missing")

    def test_cli_json_exit_is_nonzero_for_missing_profile_capability(self):
        with tempfile.TemporaryDirectory() as directory:
            process = subprocess.run(
                [sys.executable, str(HERE / "windows_preflight.py"), "--profile", "go-node", "--json", "--root", "C:/AO spaced root"],
                env={**os.environ, "PATH": directory, "PYTHONUTF8": "0"},
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(process.returncode, 0)
        self.assertEqual(json.loads(process.stdout)["status"], "failed")

    def test_profiles_have_declared_tool_sets(self):
        self.assertEqual(windows_preflight.PROFILES["binary"], ("git", "python", "powershell"))
        self.assertIn("npm", windows_preflight.PROFILES["go-node"])
        self.assertIn("cargo", windows_preflight.PROFILES["ao-source"])

    def test_go_profile_uses_valid_go_version_probe(self):
        result = windows_preflight.run("go-node", Path("C:/AO spaced root"), {**os.environ, "PYTHONUTF8": "0"})
        self.assertNotEqual(result["tools"]["go"]["status"], "unusable")


if __name__ == "__main__":
    unittest.main()
