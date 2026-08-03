from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path, PureWindowsPath

from scripts.build_go_supply_chain_candidate import portable_path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_go_supply_chain_candidate.py"
SOURCE_SHA = "a" * 40


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binary_metadata(
    *,
    dependencies: list[dict[str, object]] | None = None,
    goos: str = "linux",
    goarch: str = "amd64",
    revision: str = SOURCE_SHA,
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
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp.name)
        self.binary = self.workspace / "bin" / "ao-demo"
        self.binary.parent.mkdir()
        self.binary.write_bytes(b"bounded executable\n")
        self.binary.chmod(0o755)
        (self.workspace / "LICENSE").write_text("license\n", encoding="utf-8")
        (self.workspace / "NOTICE").write_text("notice\n", encoding="utf-8")
        (self.workspace / "go.sum").write_text(
            "example.com/alpha v1.2.3 h1:alpha\nexample.com/alpha v1.2.3/go.mod h1:mod\n",
            encoding="utf-8",
        )
        self.modules = self.workspace / "go-modules.json"
        self.modules.write_text(
            json.dumps(
                binary_metadata(
                    dependencies=[{
                    "Path": "example.com/alpha",
                    "Version": "v1.2.3",
                    "Sum": "h1:alpha",
                    }]
                )
            )
            + "\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_builder(
        self,
        output: str = "dist/one",
        dependency_lock: str = "go.sum",
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
                SOURCE_SHA,
                "--version",
                "0.0.0+git.aaaaaaaaaaaa",
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
                "ao-demo-0.0.0+git.aaaaaaaaaaaa-linux-x86_64.tar.gz",
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
        archive_name = "ao-demo-0.0.0+git.aaaaaaaaaaaa-linux-x86_64.tar.gz"
        for name in (archive_name, "SBOM.cdx.json", "go.sum"):
            self.assertEqual(sha256(one / name), sha256(two / name), name)

        sbom = json.loads((one / "SBOM.cdx.json").read_text(encoding="utf-8"))
        self.assertEqual(sbom["bomFormat"], "CycloneDX")
        self.assertEqual(sbom["specVersion"], "1.5")
        self.assertEqual(sbom["metadata"]["component"]["name"], "ao-demo")
        self.assertEqual([item["name"] for item in sbom["components"]], ["example.com/alpha"])

        evidence = json.loads((one / "supply-chain-evidence.json").read_text(encoding="utf-8"))
        second_evidence = json.loads(
            (two / "supply-chain-evidence.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            {key: value for key, value in evidence.items() if not key.endswith("_path")},
            {key: value for key, value in second_evidence.items() if not key.endswith("_path")},
        )
        self.assertEqual(evidence["source_sha"], SOURCE_SHA)
        self.assertEqual(evidence["target"], "linux-x86_64")
        self.assertEqual(evidence["generator"]["version"], "1.1.0")
        self.assertEqual(evidence["binary_provenance"]["vcs_revision"], SOURCE_SHA)
        self.assertFalse(evidence["binary_provenance"]["vcs_modified"])
        self.assertEqual(evidence["archive_sha256"], sha256(one / archive_name))
        self.assertEqual(evidence["sbom_sha256"], sha256(one / "SBOM.cdx.json"))
        self.assertEqual(evidence["regeneration_sha256"], evidence["sbom_sha256"])
        self.assertTrue(evidence["deterministic_regeneration"])
        self.assertFalse(evidence["publication_attempted"])

        with tarfile.open(one / archive_name, "r:gz") as archive:
            self.assertEqual(
                archive.getnames(),
                ["LICENSE", "NOTICE", "SBOM.cdx.json", "ao-demo", "go.sum"],
            )
            self.assertTrue(all(member.mtime == 0 for member in archive.getmembers()))

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
        metadata = json.loads(self.modules.read_text(encoding="utf-8"))
        metadata["Deps"].append(
            {"Path": "example.com/alpha", "Version": "v9.9.9", "Sum": "h1:other"}
        )
        self.modules.write_text(json.dumps(metadata) + "\n", encoding="utf-8")
        result = self.run_builder()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("duplicate module path", result.stderr)

    def test_rejects_module_missing_from_dependency_lock(self) -> None:
        (self.workspace / "go.sum").write_text("", encoding="utf-8")
        result = self.run_builder()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("module is absent from dependency lock", result.stderr)

    def test_rejects_module_replacement(self) -> None:
        metadata = json.loads(self.modules.read_text(encoding="utf-8"))
        metadata["Deps"][0]["Replace"] = {"Path": "../local-alpha"}
        self.modules.write_text(json.dumps(metadata) + "\n", encoding="utf-8")
        result = self.run_builder()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("module replacements require an explicit producer contract", result.stderr)

    def test_accepts_go_mod_for_a_zero_dependency_graph(self) -> None:
        self.modules.write_text(
            json.dumps(binary_metadata()) + "\n",
            encoding="utf-8",
        )
        (self.workspace / "go.mod").write_text(
            "module example.com/ao-demo\n\ngo 1.24\n",
            encoding="utf-8",
        )
        result = self.run_builder(dependency_lock="go.mod")
        self.assertEqual(result.returncode, 0, result.stderr)
        output = self.workspace / "dist" / "one"
        evidence = json.loads(
            (output / "supply-chain-evidence.json").read_text(encoding="utf-8")
        )
        self.assertEqual(evidence["dependency_lock_path"], "dist/one/go.mod")
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
        self.modules.write_text(
            json.dumps(
                binary_metadata(
                    dependencies=[
                        {
                            "Path": "example.com/alpha",
                            "Version": "v1.2.3",
                            "Sum": "h1:alpha",
                        }
                    ]
                )
            )
            + "\n",
            encoding="utf-8",
        )
        result = self.run_builder()
        self.assertEqual(result.returncode, 0, result.stderr)
        sbom = json.loads(
            (self.workspace / "dist" / "one" / "SBOM.cdx.json").read_text(encoding="utf-8")
        )
        self.assertEqual([component["name"] for component in sbom["components"]], ["example.com/alpha"])

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
        self.modules.write_text(
            json.dumps(binary_metadata()) + "\n",
            encoding="utf-8",
        )
        (self.workspace / "go.mod").write_text(
            "module example.com/ao-demo\n\ngo 1.24\n",
            encoding="utf-8",
        )
        result = self.run_builder(dependency_lock="go.mod")
        self.assertEqual(result.returncode, 0, result.stderr)
        sbom = json.loads(
            (self.workspace / "dist" / "one" / "SBOM.cdx.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(sbom["components"], [])

    def test_rejects_unsummed_binary_dependency(self) -> None:
        self.modules.write_text(
            json.dumps(
                binary_metadata(
                    dependencies=[
                        {
                            "Path": "example.com/alpha",
                            "Version": "v1.2.3",
                        }
                    ]
                )
            )
            + "\n",
            encoding="utf-8",
        )
        result = self.run_builder()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("dependency module sum is required", result.stderr)

    def test_rejects_binary_revision_mismatch(self) -> None:
        self.modules.write_text(
            json.dumps(binary_metadata(revision="b" * 40)) + "\n",
            encoding="utf-8",
        )
        result = self.run_builder(dependency_lock="go.sum")
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("binary source revision does not match source SHA", result.stderr)

    def test_rejects_modified_binary_source(self) -> None:
        self.modules.write_text(
            json.dumps(binary_metadata(modified="true")) + "\n",
            encoding="utf-8",
        )
        result = self.run_builder(dependency_lock="go.sum")
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("binary source must be unmodified", result.stderr)

    def test_rejects_binary_target_mismatch(self) -> None:
        self.modules.write_text(
            json.dumps(binary_metadata(goos="darwin", goarch="arm64")) + "\n",
            encoding="utf-8",
        )
        result = self.run_builder(dependency_lock="go.sum")
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("binary target does not match target", result.stderr)

    def test_rejects_missing_binary_provenance(self) -> None:
        self.modules.write_text(
            json.dumps({"Path": "example.com/ao-demo", "Main": True}) + "\n",
            encoding="utf-8",
        )
        result = self.run_builder(dependency_lock="go.sum")
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("exact binary provenance is required", result.stderr)

    def test_rejects_synthetic_version_mismatch(self) -> None:
        result = self.run_builder(dependency_lock="go.sum")
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
