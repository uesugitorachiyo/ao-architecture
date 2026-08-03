import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "scripts" / "verify_supply_chain_policy.py"
NOW = "2026-08-03T16:00:00Z"
def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SupplyChainPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "go.mod").write_text(
            "module example.com/ao-demo\n\ngo 1.24\n", encoding="utf-8"
        )
        (self.root / "main.go").write_text(
            "package main\n\nfunc main() {}\n", encoding="utf-8"
        )
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(
            ["git", "config", "user.name", "AO Test"], cwd=self.root, check=True
        )
        subprocess.run(
            ["git", "config", "user.email", "ao-test@example.invalid"],
            cwd=self.root,
            check=True,
        )
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        commit_env = os.environ.copy()
        commit_env.update(
            {
                "GIT_AUTHOR_DATE": "2026-08-03T16:00:00Z",
                "GIT_COMMITTER_DATE": "2026-08-03T16:00:00Z",
            }
        )
        subprocess.run(
            ["git", "commit", "-q", "-m", "fixture"],
            cwd=self.root,
            env=commit_env,
            check=True,
        )
        self.source_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
        self.archive = self.root / "ao-demo-1.2.3-linux-x86_64.tar.gz"
        self.binary = self.root / "ao-demo"
        build_env = os.environ.copy()
        build_env.update(
            {"CGO_ENABLED": "0", "GOARCH": "amd64", "GOOS": "linux"}
        )
        subprocess.run(
            ["go", "build", "-trimpath", "-o", str(self.binary), "."],
            cwd=self.root,
            env=build_env,
            check=True,
        )
        self.module_metadata = self.root / "go-modules.json"
        metadata = subprocess.run(
            ["go", "run", str(ROOT / "scripts" / "read_go_binary_metadata.go"), str(self.binary)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.module_metadata.write_text(metadata.stdout, encoding="utf-8")
        self.write_archive()
        self.lock = self.root / "dependencies.lock"
        self.lock.write_text("alpha=1.0.0\nbeta=2.0.0\n", encoding="utf-8")
        self.sbom = self.root / "SBOM.cdx.json"
        self.write_sbom(["alpha", "beta"])
        self.inventory = self.root / "inventory.json"
        self.policy = self.root / "policy.json"
        self.evidence = self.root / "evidence.json"
        self.write_inventory()
        self.write_policy()
        self.write_evidence()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_json(self, path: Path, value: object) -> None:
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

    def write_archive(self) -> None:
        with tarfile.open(self.archive, "w:gz") as archive:
            archive.add(self.binary, arcname="ao-demo")
            archive.add(self.module_metadata, arcname="go-modules.json")

    def write_sbom(self, components: list[str]) -> None:
        self.write_json(
            self.sbom,
            {
                "bomFormat": "CycloneDX",
                "specVersion": "1.5",
                "version": 1,
                "metadata": {
                    "component": {
                        "type": "application",
                        "name": "ao-demo",
                        "version": "1.2.3",
                    }
                },
                "components": [
                    {"type": "library", "name": name, "version": "1.0.0"}
                    for name in components
                ],
            },
        )

    def write_inventory(self, **overrides: object) -> None:
        entry = {
            "repository": "ao-demo",
            "lifecycle": "active_hosted",
            "distributable_classes": ["executable", "archive", "public_release"],
            "supported_targets": ["linux-x86_64"],
            "root_license": "LICENSE",
            "sbom_policy_applicable": True,
        }
        entry.update(overrides)
        self.write_json(
            self.inventory,
            {
                "schema": "ao.architecture.distributable-inventory.v1",
                "status": "active",
                "repositories": [entry],
                "boundaries": {
                    "excluded_repositories_included": False,
                    "lifecycle_reclassification_allowed": False,
                    "release_or_publication_authorized": False,
                },
            },
        )

    def write_policy(self) -> None:
        self.write_json(
            self.policy,
            {
                "schema": "ao.architecture.sbom-policy.v1",
                "status": "active",
                "format": "CycloneDX",
                "spec_version": "1.5",
                "required_for_classes": ["archive", "container", "public_release"],
                "maximum_evidence_bytes": 1048576,
                "freshness_window_seconds": 86400,
                "require_archive_sha256": True,
                "require_dependency_lock_sha256": True,
                "require_deterministic_regeneration": True,
                "reject_unexpected_components": True,
                "required_bindings": [
                    "repository",
                    "source_sha",
                    "version",
                    "target",
                    "archive_sha256",
                    "binary_name",
                    "binary_sha256",
                    "module_metadata_sha256",
                    "binary_provenance",
                    "sbom_sha256",
                    "generator_name",
                    "generator_version",
                    "dependency_lock_sha256",
                    "generated_at_utc",
                    "regeneration_sha256",
                ],
                "release_or_publication_authorized": False,
            },
        )

    def write_evidence(self, **overrides: object) -> None:
        value = {
            "schema": "ao.supply-chain.sbom-evidence.v1",
            "repository": "ao-demo",
            "source_sha": self.source_sha,
            "version": "1.2.3",
            "target": "linux-x86_64",
            "archive_path": self.archive.name,
            "archive_sha256": sha256(self.archive),
            "binary_name": self.binary.name,
            "binary_sha256": sha256(self.binary),
            "binary_provenance": {
                "goarch": "amd64",
                "goos": "linux",
                "vcs": "git",
                "vcs_modified": False,
                "vcs_revision": self.source_sha,
            },
            "module_metadata_path": self.module_metadata.name,
            "module_metadata_sha256": sha256(self.module_metadata),
            "sbom_path": self.sbom.name,
            "sbom_sha256": sha256(self.sbom),
            "dependency_lock_path": self.lock.name,
            "dependency_lock_sha256": sha256(self.lock),
            "expected_components": ["alpha", "beta"],
            "generator": {"name": "ao-test-generator", "version": "1.0.0"},
            "generated_at_utc": "2026-08-03T15:30:00Z",
            "regeneration_sha256": sha256(self.sbom),
            "deterministic_regeneration": True,
            "publication_attempted": False,
        }
        value.update(overrides)
        self.write_json(self.evidence, value)

    def run_verifier(self, evidence: Optional[Path] = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                sys.executable,
                str(VERIFIER),
                "--inventory",
                str(self.inventory),
                "--policy",
                str(self.policy),
                "--evidence",
                str(evidence or self.evidence),
                "--workspace-root",
                str(self.root),
                "--expected-source-sha",
                self.source_sha,
                "--expected-version",
                "1.2.3",
                "--expected-target",
                "linux-x86_64",
                "--now",
                NOW,
            ],
            text=True,
            capture_output=True,
            check=False,
        )

    def assert_rejected(self, message: str) -> None:
        result = self.run_verifier()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(message, result.stderr)

    def test_valid_bound_cyclonedx_evidence_passes(self) -> None:
        result = self.run_verifier()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("supply-chain policy verified", result.stdout)

    def test_exact_candidate_binding_is_required(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(VERIFIER),
                "--inventory",
                str(self.inventory),
                "--policy",
                str(self.policy),
                "--evidence",
                str(self.evidence),
                "--workspace-root",
                str(self.root),
                "--now",
                NOW,
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("exact source, version, and target bindings are required", result.stderr)

    def test_binary_digest_mismatch_is_rejected(self) -> None:
        self.write_evidence(binary_sha256="f" * 64)
        self.assert_rejected("binary_sha256 mismatch")

    def test_module_metadata_digest_mismatch_is_rejected(self) -> None:
        self.write_evidence(module_metadata_sha256="f" * 64)
        self.assert_rejected("module_metadata_sha256 mismatch")

    def test_module_metadata_source_mismatch_is_rejected(self) -> None:
        metadata = json.loads(self.module_metadata.read_text(encoding="utf-8"))
        next(item for item in metadata["Settings"] if item["Key"] == "vcs.revision")[
            "Value"
        ] = "b" * 40
        self.write_json(self.module_metadata, metadata)
        self.write_archive()
        self.write_evidence(
            archive_sha256=sha256(self.archive),
            module_metadata_sha256=sha256(self.module_metadata),
        )
        self.assert_rejected("module metadata does not match binary")

    def test_modified_binary_source_is_rejected(self) -> None:
        metadata = json.loads(self.module_metadata.read_text(encoding="utf-8"))
        next(item for item in metadata["Settings"] if item["Key"] == "vcs.modified")[
            "Value"
        ] = "true"
        self.write_json(self.module_metadata, metadata)
        self.write_archive()
        self.write_evidence(
            archive_sha256=sha256(self.archive),
            module_metadata_sha256=sha256(self.module_metadata),
        )
        self.assert_rejected("module metadata does not match binary")

    def test_binary_target_mismatch_is_rejected(self) -> None:
        metadata = json.loads(self.module_metadata.read_text(encoding="utf-8"))
        next(item for item in metadata["Settings"] if item["Key"] == "GOOS")[
            "Value"
        ] = "darwin"
        next(item for item in metadata["Settings"] if item["Key"] == "GOARCH")[
            "Value"
        ] = "arm64"
        self.write_json(self.module_metadata, metadata)
        self.write_archive()
        self.write_evidence(
            archive_sha256=sha256(self.archive),
            module_metadata_sha256=sha256(self.module_metadata),
        )
        self.assert_rejected("module metadata does not match binary")

    def test_downloaded_bundle_is_self_contained(self) -> None:
        bundle = self.root / "downloaded"
        bundle.mkdir()
        for path in (
            self.archive,
            self.module_metadata,
            self.lock,
            self.sbom,
            self.inventory,
            self.policy,
            self.evidence,
        ):
            shutil.copy2(path, bundle / path.name)
        result = subprocess.run(
            [
                sys.executable,
                str(VERIFIER),
                "--inventory",
                str(bundle / self.inventory.name),
                "--policy",
                str(bundle / self.policy.name),
                "--evidence",
                str(bundle / self.evidence.name),
                "--workspace-root",
                str(bundle),
                "--expected-source-sha",
                self.source_sha,
                "--expected-version",
                "1.2.3",
                "--expected-target",
                "linux-x86_64",
                "--now",
                NOW,
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_binary_provenance_summary_mismatch_is_rejected(self) -> None:
        provenance = {
            "goarch": "amd64",
            "goos": "linux",
            "vcs": "git",
            "vcs_modified": False,
            "vcs_revision": "b" * 40,
        }
        self.write_evidence(binary_provenance=provenance)
        self.assert_rejected("binary_provenance does not match module metadata")

    def test_missing_binary_required_binding_is_rejected(self) -> None:
        policy = json.loads(self.policy.read_text(encoding="utf-8"))
        policy["required_bindings"].remove("binary_provenance")
        self.write_json(self.policy, policy)
        self.assert_rejected("policy.required_bindings mismatch")

    def test_repository_contracts_validate(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(VERIFIER),
                "--inventory",
                str(ROOT / "stack" / "distributable-inventory.json"),
                "--policy",
                str(ROOT / "stack" / "sbom-policy.json"),
                "--release-classification",
                str(ROOT / "stack" / "component-release-classification.json"),
                "--validate-contracts",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("supply-chain contracts verified", result.stdout)

    def test_release_classification_drift_is_rejected(self) -> None:
        classification = json.loads(
            (ROOT / "stack" / "component-release-classification.json").read_text(encoding="utf-8")
        )
        next(
            entry
            for entry in classification["repositories"]
            if entry["repository"] == "ao-atlas"
        )["publication_allowed"] = False
        classification_path = self.root / "release-classification.json"
        self.write_json(classification_path, classification)
        result = subprocess.run(
            [
                sys.executable,
                str(VERIFIER),
                "--inventory",
                str(ROOT / "stack" / "distributable-inventory.json"),
                "--policy",
                str(ROOT / "stack" / "sbom-policy.json"),
                "--release-classification",
                str(classification_path),
                "--validate-contracts",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("ao-atlas public release classification mismatch", result.stderr)

    def test_architecture_verifier_consumes_supply_chain_contracts(self) -> None:
        verifier = (ROOT / "scripts" / "verify_architecture.py").read_text(encoding="utf-8")
        self.assertIn("validate_supply_chain_contracts", verifier)
        self.assertIn('ROOT / "stack" / "distributable-inventory.json"', verifier)
        self.assertIn('ROOT / "stack" / "sbom-policy.json"', verifier)

    def test_missing_evidence_is_rejected(self) -> None:
        self.evidence.unlink()
        self.assert_rejected("evidence")

    def test_altered_sbom_digest_is_rejected(self) -> None:
        self.sbom.write_text("{}\n", encoding="utf-8")
        self.assert_rejected("sbom_sha256 mismatch")

    def test_wrong_source_head_is_rejected(self) -> None:
        self.write_evidence(source_sha="b" * 40)
        self.assert_rejected("source_sha does not match expected source")

    def test_wrong_target_is_rejected(self) -> None:
        self.write_evidence(target="windows-x86_64")
        self.assert_rejected("target does not match expected target")

    def test_wrong_version_is_rejected(self) -> None:
        self.write_evidence(version="9.9.9")
        self.assert_rejected("version does not match expected version")

    def test_stale_generation_metadata_is_rejected(self) -> None:
        self.write_evidence(generated_at_utc="2026-07-01T00:00:00Z")
        self.assert_rejected("evidence is stale")

    def test_unbound_archive_is_rejected(self) -> None:
        self.write_evidence(archive_sha256="")
        self.assert_rejected("archive_sha256 is required")

    def test_duplicate_json_keys_are_rejected(self) -> None:
        self.evidence.write_text(
            '{"schema":"ao.supply-chain.sbom-evidence.v1",'
            '"repository":"ao-demo","repository":"other"}\n',
            encoding="utf-8",
        )
        self.assert_rejected("duplicate JSON key")

    def test_unsafe_path_is_rejected(self) -> None:
        self.write_evidence(sbom_path="../SBOM.cdx.json")
        self.assert_rejected("unsafe path")

    def test_symlink_evidence_is_rejected(self) -> None:
        target = self.root / "outside-sbom.json"
        target.write_text(self.sbom.read_text(encoding="utf-8"), encoding="utf-8")
        self.sbom.unlink()
        try:
            os.symlink(target, self.sbom)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unavailable")
        self.write_evidence(sbom_sha256=sha256(target))
        self.assert_rejected("regular file")

    def test_unexpected_components_are_rejected(self) -> None:
        self.write_sbom(["alpha", "beta", "surprise"])
        self.write_evidence(sbom_sha256=sha256(self.sbom), regeneration_sha256=sha256(self.sbom))
        self.assert_rejected("component set does not match")

    def test_nondeterministic_regeneration_is_rejected(self) -> None:
        self.write_evidence(regeneration_sha256="f" * 64)
        self.assert_rejected("regeneration_sha256 does not match")

    def test_oversized_evidence_is_rejected(self) -> None:
        self.evidence.write_text(" " * 1048577, encoding="utf-8")
        self.assert_rejected("evidence exceeds size limit")


if __name__ == "__main__":
    unittest.main()
