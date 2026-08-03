from __future__ import annotations

import json
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.rust_binary_provenance import PREFIX


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_rust_supply_chain_candidate.py"
VERIFIER = ROOT / "scripts" / "verify_supply_chain_policy.py"


class VerifyRustSupplyChainPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = "a" * 40
        lock = 'version = 3\n\n[[package]]\nname = "ao2"\nversion = "0.5.6"\n'
        metadata = {
            "build_profile": "release",
            "cargo_lock_sha256": hashlib.sha256(lock.encode()).hexdigest(),
            "repository": "ao2",
            "source_sha": self.source,
            "source_modified": False,
            "target": "linux-x86_64",
            "version": "0.5.6",
        }
        marker = PREFIX + json.dumps(metadata, sort_keys=True, separators=(",", ":")).encode("ascii") + b"\x00"
        (self.root / "ao2").write_bytes(b"ELF\x00" + marker + b"tail")
        (self.root / "rust-binary-metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
        (self.root / "Cargo.lock").write_text(lock, encoding="utf-8")
        (self.root / "LICENSE").write_text("license\n", encoding="utf-8")
        command = [
            sys.executable, str(BUILDER), "--workspace-root", str(self.root),
            "--repository", "ao2", "--source-sha", self.source, "--version", "0.5.6",
            "--target", "linux-x86_64", "--binary", "ao2",
            "--metadata-json", "rust-binary-metadata.json", "--dependency-lock", "Cargo.lock",
            "--license", "LICENSE", "--archive-name", "ao2-0.5.6-linux-x86_64.tar.gz",
            "--generated-at-utc", "2026-08-03T22:00:00Z", "--out", "dist",
        ]
        built = subprocess.run(command, text=True, capture_output=True, check=False)
        self.assertEqual(built.returncode, 0, built.stderr)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def verify(self, source: str | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable, str(VERIFIER),
                "--inventory", str(ROOT / "stack/distributable-inventory.json"),
                "--policy", str(ROOT / "stack/sbom-policy.json"),
                "--evidence", str(self.root / "dist/supply-chain-evidence.json"),
                "--workspace-root", str(self.root / "dist"),
                "--expected-source-sha", source or self.source,
                "--expected-version", "0.5.6", "--expected-target", "linux-x86_64",
                "--now", "2026-08-03T22:00:00Z",
            ],
            text=True, capture_output=True, check=False,
        )

    def test_rejects_non_rust_inventory_lane(self) -> None:
        inventory = json.loads((ROOT / "stack/distributable-inventory.json").read_text())
        next(item for item in inventory["repositories"] if item["repository"] == "ao2")["sbom_evidence_kind"] = "none"
        path = self.root / "inventory.json"
        path.write_text(json.dumps(inventory), encoding="utf-8")
        command = [sys.executable, str(VERIFIER), "--inventory", str(path), "--policy", str(ROOT / "stack/sbom-policy.json"), "--evidence", str(self.root / "dist/supply-chain-evidence.json"), "--workspace-root", str(self.root / "dist"), "--expected-source-sha", self.source, "--expected-version", "0.5.6", "--expected-target", "linux-x86_64", "--now", "2026-08-03T22:00:00Z"]
        result = subprocess.run(command, text=True, capture_output=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("evidence kind", result.stderr)

    def test_accepts_valid_rust_evidence(self) -> None:
        result = self.verify()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("verified", result.stdout)

    def test_rejects_wrong_source_and_metadata_digest(self) -> None:
        wrong = self.verify("c" * 40)
        self.assertNotEqual(wrong.returncode, 0)
        self.assertIn("source_sha does not match", wrong.stderr)
        evidence_path = self.root / "dist/supply-chain-evidence.json"
        evidence = json.loads(evidence_path.read_text())
        evidence["module_metadata_sha256"] = "f" * 64
        evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
        altered = self.verify()
        self.assertNotEqual(altered.returncode, 0)
        self.assertIn("module_metadata_sha256 mismatch", altered.stderr)

    def test_rejects_tampered_sbom_even_with_rebound_digest(self) -> None:
        sbom_path = self.root / "dist/SBOM.cdx.json"
        sbom = json.loads(sbom_path.read_text())
        sbom["components"] = []
        sbom_path.write_text(json.dumps(sbom), encoding="utf-8")
        evidence_path = self.root / "dist/supply-chain-evidence.json"
        evidence = json.loads(evidence_path.read_text())
        import hashlib
        evidence["sbom_sha256"] = hashlib.sha256(sbom_path.read_bytes()).hexdigest()
        evidence["regeneration_sha256"] = evidence["sbom_sha256"]
        evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
        result = self.verify()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("deterministic Cargo.lock regeneration", result.stderr)

    def test_rejects_rebound_lock_digest_against_embedded_binary(self) -> None:
        lock_path = self.root / "dist/Cargo.lock"
        lock_path.write_text(
            'version = 3\n\n[[package]]\nname = "fabricated-dependency"\nversion = "99.0.0"\n',
            encoding="utf-8",
        )
        evidence_path = self.root / "dist/supply-chain-evidence.json"
        evidence = json.loads(evidence_path.read_text())
        evidence["dependency_lock_sha256"] = hashlib.sha256(lock_path.read_bytes()).hexdigest()
        evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
        result = self.verify()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Cargo.lock digest does not match evidence", result.stderr)


if __name__ == "__main__":
    unittest.main()
