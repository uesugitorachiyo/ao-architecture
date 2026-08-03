from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from scripts.rust_binary_provenance import PREFIX
from scripts import build_rust_supply_chain_candidate as rust_builder


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_rust_supply_chain_candidate.py"


class BuildRustSupplyChainCandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = "a" * 40
        lock = (
            'version = 3\n\n[[package]]\nname = "ao2"\nversion = "0.5.6"\n\n'
            '[[package]]\nname = "serde"\nversion = "1.0.0"\nsource = "registry+https://github.com/rust-lang/crates.io-index"\n'
            f'checksum = "{"b" * 64}"\n'
        )
        (self.root / "Cargo.lock").write_text(lock, encoding="utf-8")
        self.metadata = {
            "build_profile": "release",
            "cargo_lock_sha256": hashlib.sha256(lock.encode()).hexdigest(),
            "repository": "ao2",
            "source_sha": self.source,
            "source_modified": False,
            "target": "linux-x86_64",
            "version": "0.5.6",
        }
        marker = PREFIX + json.dumps(self.metadata, sort_keys=True, separators=(",", ":")).encode("ascii") + b"\x00"
        (self.root / "ao2").write_bytes(b"ELF fixture\x00" + marker + b"tail")
        (self.root / "rust-binary-metadata.json").write_text(
            json.dumps(self.metadata), encoding="utf-8"
        )
        (self.root / "LICENSE").write_text("license\n", encoding="utf-8")
        (self.root / "NOTICE").write_text("notice\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_builder(self, out: str, **changes: str) -> subprocess.CompletedProcess[str]:
        values = {
            "repository": "ao2",
            "source_sha": self.source,
            "version": "0.5.6",
            "target": "linux-x86_64",
            "binary": "ao2",
            "metadata_json": "rust-binary-metadata.json",
            "dependency_lock": "Cargo.lock",
            "license": "LICENSE",
            "notice": "NOTICE",
            "archive_name": "ao2-0.5.6-linux-x86_64.tar.gz",
            "generated_at_utc": "2026-08-03T22:00:00Z",
            "out": out,
        }
        values.update(changes)
        command = [sys.executable, str(SCRIPT), "--workspace-root", str(self.root)]
        for key, value in values.items():
            command.extend([f"--{key.replace('_', '-')}", value])
        return subprocess.run(command, text=True, capture_output=True, check=False)

    def test_builds_deterministic_bound_rust_candidate(self) -> None:
        first = self.run_builder("dist/one")
        second = self.run_builder("dist/two")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        one = self.root / "dist/one"
        two = self.root / "dist/two"
        archive = "ao2-0.5.6-linux-x86_64.tar.gz"
        self.assertEqual(hashlib.sha256((one / archive).read_bytes()).digest(), hashlib.sha256((two / archive).read_bytes()).digest())
        evidence = json.loads((one / "supply-chain-evidence.json").read_text())
        self.assertEqual(evidence["schema"], "ao.supply-chain.sbom-evidence.v2")
        self.assertEqual(evidence["binary_provenance"], self.metadata)
        self.assertEqual(evidence["module_metadata_path"], "rust-binary-metadata.json")
        self.assertFalse(evidence["publication_attempted"])
        sbom = json.loads((one / "SBOM.cdx.json").read_text())
        self.assertEqual(sbom["bomFormat"], "CycloneDX")
        self.assertEqual(len(sbom["components"]), 1)
        refs = [sbom["metadata"]["component"]["bom-ref"]] + [item["bom-ref"] for item in sbom["components"]]
        self.assertEqual(len(refs), len(set(refs)))
        with tarfile.open(one / archive, "r:gz") as candidate:
            self.assertEqual(
                sorted(candidate.getnames()),
                ["Cargo.lock", "LICENSE", "NOTICE", "SBOM.cdx.json", "ao2", "rust-binary-metadata.json"],
            )

    def test_rejects_mismatched_binary_identity_and_lock(self) -> None:
        wrong = self.run_builder("dist/wrong", source_sha="c" * 40)
        self.assertNotEqual(wrong.returncode, 0)
        self.assertIn("does not match expected identity", wrong.stderr)
        (self.root / "Cargo.lock").write_text("version = 3\n", encoding="utf-8")
        malformed = self.run_builder("dist/malformed")
        self.assertNotEqual(malformed.returncode, 0)
        self.assertIn("package list", malformed.stderr)

    def test_rejects_lock_rebinding_and_dirty_source(self) -> None:
        (self.root / "Cargo.lock").write_text(
            'version = 3\n\n[[package]]\nname = "fabricated"\nversion = "99.0.0"\n',
            encoding="utf-8",
        )
        rebound = self.run_builder("dist/rebound")
        self.assertNotEqual(rebound.returncode, 0)
        self.assertIn("Cargo.lock", rebound.stderr)
        dirty = dict(self.metadata)
        dirty["source_modified"] = True
        marker = PREFIX + json.dumps(dirty, sort_keys=True, separators=(",", ":")).encode("ascii") + b"\x00"
        (self.root / "ao2").write_bytes(b"ELF fixture\x00" + marker + b"tail")
        (self.root / "rust-binary-metadata.json").write_text(json.dumps(dirty), encoding="utf-8")
        rejected = self.run_builder("dist/dirty")
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("clean source", rejected.stderr)

    def test_missing_toml_parser_fails_closed_without_breaking_import(self) -> None:
        with mock.patch.object(rust_builder, "tomllib", None):
            with self.assertRaisesRegex(rust_builder.CandidateError, "requires Python 3.11"):
                rust_builder.cargo_packages((self.root / "Cargo.lock").read_bytes())


if __name__ == "__main__":
    unittest.main()
