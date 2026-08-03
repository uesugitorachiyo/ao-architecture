from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path, PureWindowsPath

from scripts.build_go_supply_chain_candidate import (
    CandidateError,
    parse_module_stream,
    portable_path,
    validate_modules_against_lock,
)
from scripts.go_binary_provenance import (
    BinaryProvenanceError,
    normalize_binary_metadata,
    validate_binary_provenance,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_go_supply_chain_candidate.py"
def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binary_metadata(
    *,
    dependencies: list[dict[str, object]] | None = None,
    goos: str = "linux",
    goarch: str = "amd64",
    revision: str = "a" * 40,
    modified: str = "false",
) -> dict[str, object]:
    return {
        "GoVersion": "go1.26.4",
        "Path": "example.com/ao-demo/cmd/ao-demo",
        "Main": {"Path": "example.com/ao-demo", "Version": "(devel)"},
        "Deps": dependencies if dependencies is not None else [],
        "Settings": [
            {"Key": "GOOS", "Value": goos},
            {"Key": "GOARCH", "Value": goarch},
            {"Key": "vcs", "Value": "git"},
            {"Key": "vcs.revision", "Value": revision},
            {"Key": "vcs.modified", "Value": modified},
        ],
    }


class BuildGoSupplyChainCandidateTests(unittest.TestCase):
    def test_previous_reader_shape_normalizes_to_canonical_metadata(self) -> None:
        previous = {
            "GoVersion": "go1.24.13",
            "Path": "example.com/ao-demo",
            "Main": {
                "Path": "example.com/ao-demo",
                "Version": "(devel)",
                "Sum": "",
                "Replace": None,
            },
            "Deps": [],
            "Settings": [],
        }
        canonical = {
            "GoVersion": "go1.24.13",
            "Path": "example.com/ao-demo",
            "Main": {
                "Path": "example.com/ao-demo",
                "Version": "(devel)",
                "Sum": "",
            },
            "Deps": [],
            "Settings": [],
        }
        self.assertEqual(
            normalize_binary_metadata(previous),
            normalize_binary_metadata(canonical),
        )

    def test_reader_shape_preserves_one_level_module_replacement(self) -> None:
        metadata = binary_metadata(
            dependencies=[
                {
                    "Path": "example.com/alpha",
                    "Version": "v1.2.3",
                    "Sum": "h1:alpha",
                    "Replace": {
                        "Path": "example.com/fork",
                        "Version": "v1.2.4",
                        "Sum": "h1:fork",
                    },
                }
            ]
        )
        self.assertEqual(
            normalize_binary_metadata(metadata)["Deps"][0]["Replace"]["Path"],
            "example.com/fork",
        )

    def test_reader_shape_rejects_unknown_metadata_fields(self) -> None:
        metadata = binary_metadata()
        metadata["Untrusted"] = "claim"
        with self.assertRaisesRegex(BinaryProvenanceError, "unknown fields"):
            normalize_binary_metadata(metadata)

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp.name)
        (self.workspace / "go.mod").write_text(
            "module example.com/ao-demo\n\ngo 1.24\n", encoding="utf-8"
        )
        (self.workspace / "main.go").write_text(
            'package main\n\nimport "fmt"\n\nfunc main() { fmt.Println("demo") }\n',
            encoding="utf-8",
        )
        (self.workspace / "LICENSE").write_text("license\n", encoding="utf-8")
        (self.workspace / "NOTICE").write_text("notice\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=self.workspace, check=True)
        subprocess.run(
            ["git", "config", "user.name", "AO Test"], cwd=self.workspace, check=True
        )
        subprocess.run(
            ["git", "config", "user.email", "ao-test@example.invalid"],
            cwd=self.workspace,
            check=True,
        )
        subprocess.run(["git", "add", "."], cwd=self.workspace, check=True)
        commit_env = os.environ.copy()
        commit_env.update(
            {
                "GIT_AUTHOR_DATE": "2026-08-03T16:00:00Z",
                "GIT_COMMITTER_DATE": "2026-08-03T16:00:00Z",
            }
        )
        subprocess.run(
            ["git", "commit", "-q", "-m", "fixture"],
            cwd=self.workspace,
            env=commit_env,
            check=True,
        )
        self.source_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.workspace,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
        (self.workspace / ".git" / "info" / "exclude").write_text(
            "bin/\ndist/\ngo-modules.json\ngo.sum\n",
            encoding="utf-8",
        )
        self.binary = self.workspace / "bin" / "ao-demo"
        self.binary.parent.mkdir()
        build_env = os.environ.copy()
        build_env.update(
            {"CGO_ENABLED": "0", "GOARCH": "amd64", "GOOS": "linux"}
        )
        subprocess.run(
            ["go", "build", "-trimpath", "-o", str(self.binary), "."],
            cwd=self.workspace,
            env=build_env,
            check=True,
        )
        (self.workspace / "go.sum").write_text(
            "example.com/alpha v1.2.3 h1:alpha\nexample.com/alpha v1.2.3/go.mod h1:mod\n",
            encoding="utf-8",
        )
        self.modules = self.workspace / "go-modules.json"
        metadata = subprocess.run(
            ["go", "run", str(ROOT / "scripts" / "read_go_binary_metadata.go"), str(self.binary)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.modules.write_text(metadata.stdout, encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_builder(
        self,
        output: str = "dist/one",
        dependency_lock: str = "go.mod",
        include_notice: bool = True,
    ) -> subprocess.CompletedProcess:
        command = [
                sys.executable,
                str(SCRIPT),
                "--workspace-root",
                str(self.workspace),
                "--repository",
                "ao-demo",
                "--source-sha",
                self.source_sha,
                "--version",
                f"0.0.0+git.{self.source_sha[:12]}",
                "--target",
                "linux-x86_64",
                "--binary",
                "bin/ao-demo",
                "--module-json",
                "go-modules.json",
                "--dependency-lock",
                dependency_lock,
                "--license",
                "LICENSE",
                "--archive-name",
                f"ao-demo-0.0.0+git.{self.source_sha[:12]}-linux-x86_64.tar.gz",
                "--generated-at-utc",
                "2026-08-03T16:00:00Z",
                "--out",
                output,
            ]
        if include_notice:
            command.extend(["--notice", "NOTICE"])
        return subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_builds_deterministic_bound_candidate(self) -> None:
        first = self.run_builder("dist/one")
        second = self.run_builder("dist/two")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        one = self.workspace / "dist" / "one"
        two = self.workspace / "dist" / "two"
        archive_name = f"ao-demo-0.0.0+git.{self.source_sha[:12]}-linux-x86_64.tar.gz"
        for name in (archive_name, "SBOM.cdx.json", "go.mod"):
            self.assertEqual(sha256(one / name), sha256(two / name), name)

        sbom = json.loads((one / "SBOM.cdx.json").read_text(encoding="utf-8"))
        self.assertEqual(sbom["bomFormat"], "CycloneDX")
        self.assertEqual(sbom["specVersion"], "1.5")
        self.assertEqual(sbom["metadata"]["component"]["name"], "ao-demo")
        self.assertEqual(sbom["components"], [])

        evidence = json.loads((one / "supply-chain-evidence.json").read_text(encoding="utf-8"))
        second_evidence = json.loads(
            (two / "supply-chain-evidence.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            {key: value for key, value in evidence.items() if not key.endswith("_path")},
            {key: value for key, value in second_evidence.items() if not key.endswith("_path")},
        )
        self.assertEqual(evidence["source_sha"], self.source_sha)
        self.assertEqual(evidence["target"], "linux-x86_64")
        self.assertEqual(evidence["generator"]["version"], "1.2.0")
        self.assertEqual(evidence["binary_provenance"]["vcs_revision"], self.source_sha)
        self.assertFalse(evidence["binary_provenance"]["vcs_modified"])
        self.assertEqual(evidence["schema"], "ao.supply-chain.sbom-evidence.v2")
        self.assertEqual(evidence["provenance_strength"], "embedded_build_metadata")
        self.assertFalse(evidence["cryptographic_source_attestation"])
        self.assertEqual(evidence["archive_sha256"], sha256(one / archive_name))
        self.assertEqual(evidence["sbom_sha256"], sha256(one / "SBOM.cdx.json"))
        self.assertEqual(evidence["regeneration_sha256"], evidence["sbom_sha256"])
        self.assertTrue(evidence["deterministic_regeneration"])
        self.assertFalse(evidence["publication_attempted"])

        with tarfile.open(one / archive_name, "r:gz") as archive:
            self.assertEqual(
                archive.getnames(),
                ["LICENSE", "NOTICE", "SBOM.cdx.json", "ao-demo", "go-modules.json", "go.mod"],
            )
            self.assertTrue(all(member.mtime == 0 for member in archive.getmembers()))

    def test_builder_output_is_relocatable(self) -> None:
        result = self.run_builder()
        self.assertEqual(result.returncode, 0, result.stderr)
        inventory = json.loads(
            (ROOT / "stack" / "distributable-inventory.json").read_text(encoding="utf-8")
        )
        inventory["repositories"].append(
            {
                "repository": "ao-demo",
                "distributable_classes": ["executable", "archive"],
                "sbom_policy_applicable": True,
                "supported_targets": ["linux-x86_64"],
            }
        )
        with tempfile.TemporaryDirectory() as download_temp:
            download = Path(download_temp)
            bundle = download / "bundle"
            shutil.copytree(self.workspace / "dist" / "one", bundle)
            inventory_path = download / "inventory.json"
            inventory_path.write_text(
                json.dumps(inventory) + "\n", encoding="utf-8"
            )
            verify = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "verify_supply_chain_policy.py"),
                    "--inventory",
                    str(inventory_path),
                    "--policy",
                    str(ROOT / "stack" / "sbom-policy.json"),
                    "--evidence",
                    str(bundle / "supply-chain-evidence.json"),
                    "--workspace-root",
                    str(bundle),
                    "--expected-source-sha",
                    self.source_sha,
                    "--expected-version",
                    f"0.0.0+git.{self.source_sha[:12]}",
                    "--expected-target",
                    "linux-x86_64",
                    "--now",
                    "2026-08-03T16:00:00Z",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(verify.returncode, 0, verify.stderr)

    def test_evidence_paths_are_portable_across_windows_and_posix(self) -> None:
        self.assertEqual(
            portable_path(PureWindowsPath("target", "native", "SBOM.cdx.json")),
            "target/native/SBOM.cdx.json",
        )

    def test_rejects_symlinked_binary(self) -> None:
        target = self.workspace / "outside"
        target.write_bytes(b"outside\n")
        self.binary.unlink()
        try:
            os.symlink(target, self.binary)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unavailable")
        result = self.run_builder()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("binary must be a regular non-symlink file", result.stderr)

    def test_rejects_duplicate_module_paths(self) -> None:
        metadata = binary_metadata(
            revision=self.source_sha,
            dependencies=[
                {"Path": "example.com/alpha", "Version": "v1.2.3", "Sum": "h1:alpha"},
                {"Path": "example.com/alpha", "Version": "v9.9.9", "Sum": "h1:other"},
            ],
        )
        self.modules.write_text(json.dumps(metadata) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(CandidateError, "duplicate module path"):
            parse_module_stream(self.modules)

    def test_rejects_module_missing_from_dependency_lock(self) -> None:
        modules = [{"path": "example.com/alpha", "version": "v1.2.3", "sum": "h1:alpha"}]
        with self.assertRaisesRegex(CandidateError, "module is absent from dependency lock"):
            validate_modules_against_lock(modules, b"")

    def test_rejects_module_with_wrong_dependency_lock_sum(self) -> None:
        modules = [{"path": "example.com/alpha", "version": "v1.2.3", "sum": "h1:alpha"}]
        with self.assertRaisesRegex(CandidateError, "module is absent from dependency lock"):
            validate_modules_against_lock(
                modules, b"example.com/alpha v1.2.3 h1:altered\n"
            )

    def test_rejects_module_replacement(self) -> None:
        metadata = binary_metadata(
            revision=self.source_sha,
            dependencies=[{
                "Path": "example.com/alpha",
                "Version": "v1.2.3",
                "Sum": "h1:alpha",
                "Replace": {"Path": "../local-alpha"},
            }],
        )
        self.modules.write_text(json.dumps(metadata) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(CandidateError, "module replacements"):
            parse_module_stream(self.modules)

    def test_accepts_go_mod_for_a_zero_dependency_graph(self) -> None:
        result = self.run_builder()
        self.assertEqual(result.returncode, 0, result.stderr)
        output = self.workspace / "dist" / "one"
        evidence = json.loads(
            (output / "supply-chain-evidence.json").read_text(encoding="utf-8")
        )
        self.assertEqual(evidence["dependency_lock_path"], "go.mod")
        with tarfile.open(output / evidence["archive_path"].split("/")[-1], "r:gz") as archive:
            self.assertIn("go.mod", archive.getnames())

    def test_notice_is_optional_but_license_remains_packaged(self) -> None:
        (self.workspace / "NOTICE").unlink()
        result = self.run_builder(include_notice=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = self.workspace / "dist" / "one"
        evidence = json.loads(
            (output / "supply-chain-evidence.json").read_text(encoding="utf-8")
        )
        with tarfile.open(output / evidence["archive_path"].split("/")[-1], "r:gz") as archive:
            self.assertIn("LICENSE", archive.getnames())
            self.assertNotIn("NOTICE", archive.getnames())

    def test_consumes_exact_binary_module_metadata(self) -> None:
        result = self.run_builder()
        self.assertEqual(result.returncode, 0, result.stderr)
        sbom = json.loads(
            (self.workspace / "dist" / "one" / "SBOM.cdx.json").read_text(encoding="utf-8")
        )
        self.assertEqual(sbom["components"], [])

    def test_rejects_incomplete_binary_module_metadata(self) -> None:
        self.modules.write_text(
            json.dumps(
                {
                    "GoVersion": "go1.26.4",
                    "Main": {"Path": "example.com/ao-demo", "Version": "(devel)"},
                }
            )
            + "\n",
            encoding="utf-8",
        )
        result = self.run_builder()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("binary module metadata is incomplete", result.stderr)

    def test_consumes_zero_dependency_binary_module_metadata(self) -> None:
        result = self.run_builder()
        self.assertEqual(result.returncode, 0, result.stderr)
        sbom = json.loads(
            (self.workspace / "dist" / "one" / "SBOM.cdx.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(sbom["components"], [])

    def test_rejects_unsummed_binary_dependency(self) -> None:
        metadata = binary_metadata(
            revision=self.source_sha,
            dependencies=[{"Path": "example.com/alpha", "Version": "v1.2.3"}],
        )
        self.modules.write_text(json.dumps(metadata) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(CandidateError, "dependency module sum is required"):
            parse_module_stream(self.modules)

    def test_rejects_binary_revision_mismatch(self) -> None:
        metadata = json.loads(self.modules.read_text(encoding="utf-8"))
        next(item for item in metadata["Settings"] if item["Key"] == "vcs.revision")["Value"] = "b" * 40
        self.modules.write_text(json.dumps(metadata) + "\n", encoding="utf-8")
        result = self.run_builder()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("module metadata does not match binary", result.stderr)

    def test_rejects_modified_binary_source(self) -> None:
        metadata = json.loads(self.modules.read_text(encoding="utf-8"))
        next(item for item in metadata["Settings"] if item["Key"] == "vcs.modified")["Value"] = "true"
        self.modules.write_text(json.dumps(metadata) + "\n", encoding="utf-8")
        result = self.run_builder()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("module metadata does not match binary", result.stderr)

    def test_rejects_binary_target_mismatch(self) -> None:
        metadata = json.loads(self.modules.read_text(encoding="utf-8"))
        next(item for item in metadata["Settings"] if item["Key"] == "GOOS")["Value"] = "darwin"
        next(item for item in metadata["Settings"] if item["Key"] == "GOARCH")["Value"] = "arm64"
        self.modules.write_text(json.dumps(metadata) + "\n", encoding="utf-8")
        result = self.run_builder()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("module metadata does not match binary", result.stderr)

    def test_rejects_missing_binary_provenance(self) -> None:
        self.modules.write_text(
            json.dumps({"Path": "example.com/ao-demo", "Main": True}) + "\n",
            encoding="utf-8",
        )
        result = self.run_builder()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("exact binary provenance is required", result.stderr)

    def test_rejects_non_go_binary(self) -> None:
        self.binary.write_bytes(b"not a Go executable\n")
        result = self.run_builder()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("read Go build metadata", result.stderr)

    def test_rejects_metadata_from_different_binary(self) -> None:
        (self.workspace / "main.go").write_text(
            'package main\n\nimport "fmt"\n\nfunc main() { fmt.Println("changed") }\n',
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "main.go"], cwd=self.workspace, check=True)
        commit_env = os.environ.copy()
        commit_env.update(
            {
                "GIT_AUTHOR_DATE": "2026-08-03T16:01:00Z",
                "GIT_COMMITTER_DATE": "2026-08-03T16:01:00Z",
            }
        )
        subprocess.run(
            ["git", "commit", "-q", "-m", "changed fixture"],
            cwd=self.workspace,
            env=commit_env,
            check=True,
        )
        build_env = os.environ.copy()
        build_env.update(
            {"CGO_ENABLED": "0", "GOARCH": "amd64", "GOOS": "linux"}
        )
        subprocess.run(
            ["go", "build", "-trimpath", "-o", str(self.binary), "."],
            cwd=self.workspace,
            env=build_env,
            check=True,
        )
        result = self.run_builder()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("module metadata does not match binary", result.stderr)

    def test_accepts_declared_linux_aarch64_target_mapping(self) -> None:
        metadata = binary_metadata(
            goarch="arm64", goos="linux", revision=self.source_sha
        )
        provenance = validate_binary_provenance(
            metadata, self.source_sha, "linux-aarch64"
        )
        self.assertEqual(provenance["goarch"], "arm64")
        self.assertEqual(provenance["goos"], "linux")

    def test_provenance_validator_rejects_wrong_source(self) -> None:
        metadata = binary_metadata(revision="b" * 40)
        with self.assertRaisesRegex(ValueError, "source revision does not match"):
            validate_binary_provenance(metadata, self.source_sha, "linux-x86_64")

    def test_provenance_validator_rejects_modified_source(self) -> None:
        metadata = binary_metadata(modified="true", revision=self.source_sha)
        with self.assertRaisesRegex(ValueError, "source must be unmodified"):
            validate_binary_provenance(metadata, self.source_sha, "linux-x86_64")

    def test_provenance_validator_rejects_wrong_target(self) -> None:
        metadata = binary_metadata(
            goarch="arm64", goos="darwin", revision=self.source_sha
        )
        with self.assertRaisesRegex(ValueError, "target does not match"):
            validate_binary_provenance(metadata, self.source_sha, "linux-x86_64")

    def test_rejects_synthetic_version_mismatch(self) -> None:
        result = self.run_builder()
        self.assertEqual(result.returncode, 0, result.stderr)
        command = result.args.copy()
        version_index = command.index("--version") + 1
        command[version_index] = "0.0.0+git.bbbbbbbbbbbb"
        archive_index = command.index("--archive-name") + 1
        command[archive_index] = "ao-demo-0.0.0+git.bbbbbbbbbbbb-linux-x86_64.tar.gz"
        output_index = command.index("--out") + 1
        command[output_index] = "dist/version-mismatch"
        mismatch = subprocess.run(command, text=True, capture_output=True, check=False)
        self.assertNotEqual(mismatch.returncode, 0, mismatch.stdout)
        self.assertIn("version does not match binary source revision", mismatch.stderr)


if __name__ == "__main__":
    unittest.main()
