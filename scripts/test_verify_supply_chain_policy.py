import hashlib
import io
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

from scripts.verify_supply_chain_policy import (
    PolicyError,
    validate_modules_against_lock,
    validate_sbom_identity,
)


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
        self.lock = self.root / "go.mod"
        self.license = self.root / "LICENSE"
        self.license.write_text("Test license\n", encoding="utf-8")
        self.sbom = self.root / "SBOM.cdx.json"
        self.write_sbom([])
        self.write_archive()
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

    def write_archive(self, extra_members: Optional[dict[str, bytes]] = None) -> None:
        with tarfile.open(self.archive, "w:gz") as archive:
            archive.add(self.binary, arcname="ao-demo")
            archive.add(self.module_metadata, arcname="go-modules.json")
            archive.add(self.sbom, arcname="SBOM.cdx.json")
            archive.add(self.lock, arcname="go.mod")
            archive.add(self.license, arcname="LICENSE")
            for name, value in (extra_members or {}).items():
                info = tarfile.TarInfo(name)
                info.size = len(value)
                archive.addfile(info, io.BytesIO(value))

    def write_sbom(self, components: list[str]) -> None:
        self.write_json(
            self.sbom,
            {
                "bomFormat": "CycloneDX",
                "specVersion": "1.5",
                "version": 1,
                "metadata": {
                    "component": {
                        "bom-ref": "pkg:golang/example.com/ao-demo@1.2.3",
                        "type": "application",
                        "name": "ao-demo",
                        "purl": "pkg:golang/example.com/ao-demo@1.2.3",
                        "version": "1.2.3",
                    },
                    "tools": {
                        "components": [
                            {
                                "name": "ao-test-generator",
                                "type": "application",
                                "version": "1.0.0",
                            }
                        ]
                    },
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
                    "cryptographic_source_attestation",
                    "module_metadata_sha256",
                    "binary_provenance",
                    "provenance_strength",
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
            "schema": "ao.supply-chain.sbom-evidence.v2",
            "repository": "ao-demo",
            "source_sha": self.source_sha,
            "version": "1.2.3",
            "target": "linux-x86_64",
            "archive_path": self.archive.name,
            "archive_sha256": sha256(self.archive),
            "binary_name": self.binary.name,
            "binary_sha256": sha256(self.binary),
            "cryptographic_source_attestation": False,
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
            "expected_components": [],
            "generator": {"name": "ao-test-generator", "version": "1.0.0"},
            "generated_at_utc": "2026-08-03T15:30:00Z",
            "regeneration_sha256": sha256(self.sbom),
            "deterministic_regeneration": True,
            "publication_attempted": False,
            "provenance_strength": "embedded_build_metadata",
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

    def test_v1_evidence_is_rejected(self) -> None:
        self.write_evidence(schema="ao.supply-chain.sbom-evidence.v1")
        self.assert_rejected("evidence schema mismatch")

    def test_cryptographic_attestation_must_not_be_claimed(self) -> None:
        self.write_evidence(cryptographic_source_attestation=True)
        self.assert_rejected("cryptographic_source_attestation must be false")

    def test_provenance_strength_must_be_scoped(self) -> None:
        self.write_evidence(provenance_strength="cryptographic")
        self.assert_rejected("provenance_strength mismatch")

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

    def test_archive_member_count_is_bounded_early(self) -> None:
        with tarfile.open(self.archive, "w:gz") as archive:
            for index in range(17):
                path = self.root / f"member-{index}"
                path.write_bytes(b"x")
                archive.add(path, arcname=path.name)
        self.write_evidence(archive_sha256=sha256(self.archive))
        self.assert_rejected("archive member count exceeds limit")

    def test_archive_module_metadata_size_is_bounded(self) -> None:
        oversized = self.root / "oversized-metadata"
        oversized.write_bytes(b"x" * ((8 << 20) + 1))
        with tarfile.open(self.archive, "w:gz") as archive:
            archive.add(self.binary, arcname="ao-demo")
            archive.add(oversized, arcname="go-modules.json")
        self.write_evidence(archive_sha256=sha256(self.archive))
        self.assert_rejected("archive module metadata exceeds size limit")

    def test_archive_rejects_unexpected_payload(self) -> None:
        self.write_archive({"unexpected.txt": b"surprise\n"})
        self.write_evidence(archive_sha256=sha256(self.archive))
        self.assert_rejected("archive member set is invalid")

    def test_archive_sbom_must_match_downloaded_sbom(self) -> None:
        original = self.sbom.read_bytes()
        self.sbom.write_bytes(original.replace(b'"version": 1', b'"version": 2'))
        self.write_archive()
        self.sbom.write_bytes(original)
        self.write_evidence(archive_sha256=sha256(self.archive))
        self.assert_rejected("archive SBOM does not match evidence")

    def test_dependency_lock_must_bind_binary_modules(self) -> None:
        lock = self.root / "go.sum"
        lock.write_text(
            "example.com/required v1.2.3 h1:altered\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(
            PolicyError, "binary module is absent from dependency lock"
        ):
            validate_modules_against_lock(
                [
                    {
                        "path": "example.com/required",
                        "version": "v1.2.3",
                        "sum": "h1:required",
                    }
                ],
                lock,
            )

    def test_sbom_dependency_purl_must_match_binary_metadata(self) -> None:
        module = {
            "path": "example.com/required",
            "version": "v1.2.3",
            "sum": "h1:required",
        }
        generator = {"name": "ao-test-generator", "version": "1.0.0"}
        main_purl = "pkg:golang/example.com/ao-demo@1.2.3"
        sbom = {
            "metadata": {
                "component": {
                    "bom-ref": main_purl,
                    "name": "ao-demo",
                    "purl": main_purl,
                    "type": "application",
                    "version": "1.2.3",
                },
                "tools": {"components": [{"type": "application", **generator}]},
            },
            "components": [
                {
                    "bom-ref": "pkg:golang/example.com/required@v1.2.3",
                    "name": module["path"],
                    "purl": "pkg:golang/example.com/other@v1.2.3",
                    "properties": [
                        {"name": "ao:go-module-sum", "value": module["sum"]}
                    ],
                    "type": "library",
                    "version": module["version"],
                }
            ],
        }
        with self.assertRaisesRegex(
            PolicyError, "SBOM component identity does not match binary metadata"
        ):
            validate_sbom_identity(
                sbom,
                "ao-demo",
                "1.2.3",
                {"Main": {"Path": "example.com/ao-demo"}},
                [module],
                [module["path"]],
                generator,
            )

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
            '{"schema":"ao.supply-chain.sbom-evidence.v2",'
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

    def test_symlinked_evidence_document_is_rejected(self) -> None:
        target = self.root / "actual-evidence.json"
        self.evidence.replace(target)
        try:
            os.symlink(target, self.evidence)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unavailable")
        result = self.run_verifier()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("evidence must reference a regular file", result.stderr)

    def test_expected_components_must_match_binary_metadata(self) -> None:
        self.write_evidence(expected_components=["invented.example/module"])
        self.assert_rejected("expected components do not match binary metadata")

    def test_sbom_application_purl_must_match_binary_metadata(self) -> None:
        sbom = json.loads(self.sbom.read_text(encoding="utf-8"))
        sbom["metadata"]["component"]["purl"] = "pkg:golang/example.com/other@1.2.3"
        self.write_json(self.sbom, sbom)
        self.write_archive()
        digest = sha256(self.sbom)
        self.write_evidence(sbom_sha256=digest, regeneration_sha256=digest)
        self.assert_rejected("SBOM application identity does not match binary metadata")

    def test_sbom_generator_must_match_evidence(self) -> None:
        sbom = json.loads(self.sbom.read_text(encoding="utf-8"))
        sbom["metadata"]["tools"]["components"][0]["version"] = "9.9.9"
        self.write_json(self.sbom, sbom)
        self.write_archive()
        digest = sha256(self.sbom)
        self.write_evidence(sbom_sha256=digest, regeneration_sha256=digest)
        self.assert_rejected("SBOM generator identity does not match evidence")

    def test_unexpected_components_are_rejected(self) -> None:
        self.write_sbom(["surprise"])
        self.write_archive()
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
