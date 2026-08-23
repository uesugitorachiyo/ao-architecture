#!/usr/bin/env python3
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).with_name("verify_development_baseline_evidence.py")
SPEC = importlib.util.spec_from_file_location("evidence", MODULE_PATH)
evidence = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evidence)

COMMIT = "c" * 40
BASELINE = "sha256:" + "b" * 64
CORRELATION = "ao-cross-platform-development-baseline-20260822-r2"
AUTHORITY = {name: False for name in evidence.AUTHORITY_FIELDS}
REPOSITORIES = [{"repository": name, "commit": "a" * 40, "clean": True, "detached": True, "submodules_clean": True} for name in evidence.REPOSITORIES]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")


def build_fixture(root):
    paths = {}
    for platform, architecture, runner in (("macos", "arm64", "macos-26"), ("windows", "amd64", "windows-2025")):
        prefix = f"{runner}-{COMMIT}"
        host = root / "host" / f"{prefix}-host.json"
        gate = root / "gates" / runner / f"{prefix}-gates.json"
        workflow = root / "workflow" / f"{prefix}-workflow.json"
        cleanup = root / "cleanup" / f"{prefix}-cleanup.json"
        write_json(host, {"schema": "ao.architecture.development-baseline-bootstrap-result.v1", "status": "pass", "platform": platform, "architecture": architecture, "controller_source_commit": COMMIT, "baseline_identity": BASELINE, "correlation_id": CORRELATION, "repositories": REPOSITORIES, "authority": AUTHORITY})
        write_json(gate, {"schema": "ao.architecture.development-baseline-gate-result.v1", "status": "pass", "controller_source_commit": COMMIT, "baseline_identity": BASELINE, "declared_gate_count": 59, "completed_gate_count": 59, "authority": AUTHORITY})
        write_json(workflow, {"schema": "ao.architecture.development-baseline-workflow-result.v1", "status": "pass", "correlation_id": CORRELATION, "baseline_identity": BASELINE, "stages": [{"id": item[0], "repository": item[1], "source_commit": "a" * 40, "status": "pass", "outcome": item[2]} for item in evidence.REQUIRED_STAGES], "authority": AUTHORITY, "cleanup": {"run_owned_processes": 0, "run_owned_listeners": 0, "temporary_root": "removed"}})
        write_json(cleanup, {"schema": "ao.architecture.development-baseline-cleanup.v1", "cleanup_status": "root_absent", "platform": runner, "source_commit": COMMIT})
        paths[platform] = {"host": host, "gate": gate, "workflow": workflow, "cleanup": cleanup}
    rehash = root / "rehash" / f"development-baseline-{COMMIT}-rehash.json"
    write_json(rehash, {"schema": "ao.architecture.development-baseline-rehash.v1", "status": "pass", "source_commit": COMMIT, "baseline_identity": BASELINE, "missing": 0, "extra": 0, "size_mismatches": 0, "digest_mismatches": 0, "gate_log_mismatches": 0})
    parity = root / "parity" / "parity.json"
    write_json(parity, {"schema": "ao.architecture.development-baseline-parity.v1", "parity": "pass", "baseline_identity": BASELINE, "correlation_id": CORRELATION, "inputs": {"macos_sha256": "sha256:" + digest(paths["macos"]["workflow"]), "windows_sha256": "sha256:" + digest(paths["windows"]["workflow"])}, "differences": [], "authority": AUTHORITY})
    return paths


class EvidenceTests(unittest.TestCase):
    def verify(self, mutation=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = build_fixture(root)
            if mutation:
                mutation(root, paths)
            return evidence.verify_evidence(root, COMMIT, BASELINE)

    def test_complete_fixture_passes(self):
        result = self.verify()
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["counts"]["workflow_results"], 2)

    def test_duplicate_and_absolute_paths_fail(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            evidence.validate_relative_paths(["A/file.json", "a/FILE.json"])
        with self.assertRaisesRegex(ValueError, "relative"):
            evidence.validate_relative_paths(["C:/private/file.json"])

    def test_missing_and_extra_files_fail(self):
        with self.assertRaisesRegex(ValueError, "missing"):
            self.verify(lambda root, paths: paths["macos"]["cleanup"].unlink())
        with self.assertRaisesRegex(ValueError, "extra"):
            self.verify(lambda root, paths: (root / "extra.txt").write_text("extra"))

    def test_size_and_digest_drift_fail(self):
        with self.assertRaisesRegex(ValueError, "size"):
            self.verify(lambda root, paths: paths["macos"]["host"].write_bytes(b"x" * (evidence.MAX_FILE_BYTES + 1)))
        def drift(root, paths):
            parity = root / "parity" / "parity.json"
            value = json.loads(parity.read_text())
            value["inputs"]["macos_sha256"] = "sha256:" + "0" * 64
            write_json(parity, value)
        with self.assertRaisesRegex(ValueError, "digest"):
            self.verify(drift)

    def test_authority_and_runner_drift_fail(self):
        def widen(root, paths):
            value = json.loads(paths["windows"]["host"].read_text())
            value["authority"]["promotion"] = True
            write_json(paths["windows"]["host"], value)
        with self.assertRaisesRegex(ValueError, "authority"):
            self.verify(widen)
        def runner(root, paths):
            value = json.loads(paths["windows"]["cleanup"].read_text())
            value["platform"] = "ubuntu-latest"
            write_json(paths["windows"]["cleanup"], value)
        with self.assertRaisesRegex(ValueError, "runner"):
            self.verify(runner)

    def test_identity_residue_and_host_set_drift_fail(self):
        def identity(root, paths):
            value = json.loads(paths["macos"]["host"].read_text())
            value["baseline_identity"] = "sha256:" + "0" * 64
            write_json(paths["macos"]["host"], value)
        with self.assertRaisesRegex(ValueError, "baseline"):
            self.verify(identity)
        def residue(root, paths):
            value = json.loads(paths["windows"]["workflow"].read_text())
            value["cleanup"]["run_owned_processes"] = 1
            write_json(paths["windows"]["workflow"], value)
            parity = root / "parity" / "parity.json"
            p = json.loads(parity.read_text())
            p["inputs"]["windows_sha256"] = "sha256:" + digest(paths["windows"]["workflow"])
            write_json(parity, p)
        with self.assertRaisesRegex(ValueError, "residue"):
            self.verify(residue)
        def host_set(root, paths):
            value = json.loads(paths["windows"]["host"].read_text())
            value["repositories"][0]["commit"] = "d" * 40
            write_json(paths["windows"]["host"], value)
        with self.assertRaisesRegex(ValueError, "repository set"):
            self.verify(host_set)


if __name__ == "__main__":
    unittest.main()
