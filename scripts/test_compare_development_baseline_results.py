#!/usr/bin/env python3
import base64
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).with_name("compare_development_baseline_results.py")
SPEC = importlib.util.spec_from_file_location("comparator", MODULE_PATH)
comparator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(comparator)


def retained(value):
    data = value if isinstance(value, bytes) else value.encode("utf-8")
    return {
        "encoding": "base64",
        "bytes": len(data),
        "sha256": "sha256:" + hashlib.sha256(data).hexdigest(),
        "data": base64.b64encode(data).decode("ascii"),
    }


def metadata(platform):
    windows = platform == "windows"
    return {
        "absolute_roots": ["C:\\native root" if windows else "/native/root"],
        "path_separator": "\\" if windows else "/",
        "executable_suffix": ".exe" if windows else "",
        "shell_names": ["pwsh", "powershell.exe"] if windows else ["bash", "sh"],
        "archive_suffixes": [".zip"] if windows else [".tar.gz", ".tar"],
    }


def document(platform):
    environment = metadata(platform)
    root = environment["absolute_roots"][0]
    shell = environment["shell_names"][0]
    suffix = environment["executable_suffix"]
    archive = environment["archive_suffixes"][0]
    stages = []
    for stage_id, repository, outcome in comparator.REQUIRED_STAGES:
        artifact = json.dumps({
            "id": stage_id,
            "path": root + environment["path_separator"] + "evidence" + environment["path_separator"] + "result.json",
            "command": "tool" + suffix,
            "shell": shell,
            "generated_at_utc": "2026-08-23T01:02:03Z" if platform == "macos" else "2026-08-23T04:05:06Z",
            "duration_ms": 10 if platform == "macos" else 20,
            "process_id": 111 if platform == "macos" else 222,
            "archive": "bundle" + archive,
            "semantic": "same",
        }, sort_keys=True).encode()
        stages.append({
            "id": stage_id,
            "repository": repository,
            "source_commit": "a" * 40,
            "status": "pass",
            "outcome": outcome,
            "consumes": [] if not stages else [stages[-1]["id"]],
            "artifact_sha256": "sha256:" + hashlib.sha256(artifact).hexdigest(),
            "artifact_evidence": retained(artifact),
            "stdout_sha256": retained(b"")["sha256"],
            "stdout_evidence": retained(b""),
            "stderr_sha256": retained(b"")["sha256"],
            "stderr_evidence": retained(b""),
            "exit_code": 0,
            "elapsed_ms": 10 if platform == "macos" else 20,
        })
    return {
        "schema": comparator.RESULT_SCHEMA,
        "status": "pass",
        "correlation_id": "ao-cross-platform-development-baseline-20260822-r2",
        "baseline_identity": "sha256:" + "b" * 64,
        "normalization": environment,
        "stages": stages,
        "authority": {name: False for name in comparator.AUTHORITY_FIELDS},
        "cleanup": {"run_owned_processes": 0, "run_owned_listeners": 0, "temporary_root": "removed"},
    }


class NormalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = comparator.load_profile(Path(__file__).parents[1] / "stack" / "development-baseline-normalization-v1.json")

    def pair(self, key, macos, windows):
        left = comparator.normalize_value(macos, key, metadata("macos"), self.profile)
        right = comparator.normalize_value(windows, key, metadata("windows"), self.profile)
        return left, right

    def test_absolute_root_positive_and_negative(self):
        self.assertEqual(*self.pair("path", "/native/root/evidence", "C:\\native root\\evidence"))
        self.assertNotEqual(*self.pair("path", "/other/evidence", "C:\\other\\evidence"))

    def test_path_separator_positive_and_negative(self):
        self.assertEqual(*self.pair("path", "relative/evidence", "relative\\evidence"))
        self.assertNotEqual(*self.pair("path", "relative/evidence", "different\\evidence"))

    def test_executable_suffix_positive_and_negative(self):
        self.assertEqual(*self.pair("command", "tool", "tool.exe"))
        self.assertNotEqual(*self.pair("command", "tool", "tool.dll"))

    def test_shell_name_positive_and_negative(self):
        self.assertEqual(*self.pair("shell", "bash", "pwsh"))
        self.assertNotEqual(*self.pair("shell", "bash -c safe", "pwsh -c unsafe"))

    def test_timestamp_positive_and_negative(self):
        self.assertEqual(*self.pair("generated_at_utc", "2026-08-23T01:02:03Z", "2026-08-23T04:05:06Z"))
        self.assertNotEqual(*self.pair("status", "pass-at-one", "pass-at-two"))

    def test_duration_positive_and_negative(self):
        self.assertEqual(*self.pair("duration_ms", 1, 99))
        self.assertNotEqual(*self.pair("completed_nodes", 1, 99))

    def test_process_id_positive_and_negative(self):
        self.assertEqual(*self.pair("process_id", 1, 99))
        self.assertNotEqual(*self.pair("mission_id", 1, 99))

    def test_archive_format_positive_and_negative(self):
        self.assertEqual(*self.pair("archive", "bundle.tar.gz", "bundle.zip"))
        self.assertNotEqual(*self.pair("archive", "bundle.tar.gz", "other.zip"))


class ComparatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = comparator.load_profile(Path(__file__).parents[1] / "stack" / "development-baseline-normalization-v1.json")

    def compare(self, macos=None, windows=None):
        return comparator.compare_documents(macos or document("macos"), windows or document("windows"), self.profile, "sha256:" + "1" * 64, "sha256:" + "2" * 64)

    def test_equivalent_results_pass(self):
        verdict = self.compare()
        self.assertEqual(verdict["parity"], "pass")
        self.assertEqual(verdict["differences"], [])

    def test_undeclared_field_drift_fails(self):
        windows = document("windows")
        artifact = json.loads(base64.b64decode(windows["stages"][4]["artifact_evidence"]["data"]))
        artifact["semantic"] = "changed"
        body = json.dumps(artifact, sort_keys=True).encode()
        windows["stages"][4]["artifact_evidence"] = retained(body)
        windows["stages"][4]["artifact_sha256"] = windows["stages"][4]["artifact_evidence"]["sha256"]
        with self.assertRaisesRegex(ValueError, "semantic parity"):
            self.compare(windows=windows)

    def test_missing_and_extra_evidence_fail(self):
        for mutation in ("missing", "extra"):
            windows = document("windows")
            if mutation == "missing":
                del windows["stages"][0]["artifact_evidence"]
            else:
                windows["stages"][0]["undeclared"] = True
            with self.assertRaises(ValueError):
                self.compare(windows=windows)

    def test_manifest_mismatch_and_reused_input_fail(self):
        windows = document("windows")
        windows["baseline_identity"] = "sha256:" + "c" * 64
        with self.assertRaisesRegex(ValueError, "baseline"):
            self.compare(windows=windows)
        with self.assertRaisesRegex(ValueError, "distinct"):
            comparator.compare_documents(document("macos"), document("windows"), self.profile, "sha256:" + "1" * 64, "sha256:" + "1" * 64)

    def test_invalid_self_pass_fails(self):
        windows = document("windows")
        windows["stages"][0]["artifact_evidence"]["sha256"] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(ValueError, "digest"):
            self.compare(windows=windows)

    def test_cleanup_disagreement_fails(self):
        windows = document("windows")
        windows["cleanup"]["temporary_root"] = "present"
        with self.assertRaisesRegex(ValueError, "cleanup"):
            self.compare(windows=windows)

    def test_authority_widening_fails(self):
        windows = document("windows")
        windows["authority"]["promotion"] = True
        with self.assertRaisesRegex(ValueError, "authority"):
            self.compare(windows=windows)


if __name__ == "__main__":
    unittest.main()
