import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
import zipfile

from scripts import run_public_stack_canary as canary


class ManifestTests(unittest.TestCase):
    def test_each_target_selects_all_seven_components(self):
        for target in ("linux-x86_64", "macos-aarch64", "windows-x86_64"):
            with self.subTest(target=target):
                assets = canary.select_assets(target)
                self.assertEqual(7, len(assets))
                self.assertEqual(7, len({asset.component for asset in assets}))

    def test_selected_assets_are_pinned_public_release_downloads(self):
        for target in canary.TARGETS:
            for asset in canary.select_assets(target):
                with self.subTest(target=target, component=asset.component):
                    self.assertRegex(asset.sha256, r"^[0-9a-f]{64}$")
                    self.assertTrue(
                        asset.url.startswith("https://github.com/uesugitorachiyo/")
                    )
                    self.assertIn("/releases/download/", asset.url)


class SafeInstallTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.destination = self.root / "install"

    def tearDown(self):
        self.temporary.cleanup()

    def asset(self, archive, binary="tool"):
        return canary.Asset(
            component="example",
            version="v1.0.0",
            source_sha="a" * 40,
            url="https://github.com/uesugitorachiyo/example/releases/download/v1.0.0/tool",
            sha256="0" * 64,
            archive=archive,
            binary=binary,
        )

    def write(self, name, content):
        path = self.root / name
        path.write_bytes(content)
        return path

    def make_tar(self, entries):
        path = self.root / "asset.tar.gz"
        with tarfile.open(path, "w:gz") as archive:
            for name, content in entries:
                info = tarfile.TarInfo(name)
                info.size = len(content)
                info.mode = 0o755
                archive.addfile(info, io.BytesIO(content))
        return path

    def make_zip(self, entries):
        path = self.root / "asset.zip"
        with zipfile.ZipFile(path, "w") as archive:
            for name, content in entries:
                archive.writestr(name, content)
        return path

    def test_verify_digest_rejects_changed_bytes(self):
        path = self.write("asset", b"changed")
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            canary.verify_digest(path, "0" * 64)

    def test_verify_digest_accepts_exact_bytes(self):
        path = self.write("asset", b"exact")
        canary.verify_digest(path, hashlib.sha256(b"exact").hexdigest())

    def test_tar_install_copies_regular_binary(self):
        archive = self.make_tar([("nested/tool", b"binary")])
        installed = canary.install_asset(
            self.asset("tar.gz"), archive, self.destination
        )
        self.assertEqual((self.destination / "tool",), installed)
        self.assertEqual(b"binary", installed[0].read_bytes())

    def test_zip_install_copies_regular_binary(self):
        archive = self.make_zip([("nested/tool.exe", b"binary")])
        installed = canary.install_asset(
            self.asset("zip", "tool.exe"), archive, self.destination
        )
        self.assertEqual((self.destination / "tool.exe",), installed)
        self.assertEqual(b"binary", installed[0].read_bytes())

    def test_raw_install_renames_public_asset_to_binary(self):
        archive = self.write("downloaded-name", b"binary")
        installed = canary.install_asset(
            self.asset("raw"), archive, self.destination
        )
        self.assertEqual((self.destination / "tool",), installed)
        self.assertEqual(b"binary", installed[0].read_bytes())

    def test_bounded_copy_rejects_oversized_content(self):
        destination = io.BytesIO()
        with self.assertRaisesRegex(ValueError, "exceeds 4 bytes"):
            canary.copy_bounded(io.BytesIO(b"12345"), destination, 4)

    def test_tar_install_rejects_parent_traversal(self):
        archive = self.make_tar([("../escape", b"bad")])
        with self.assertRaisesRegex(ValueError, "unsafe archive path"):
            canary.install_asset(self.asset("tar.gz"), archive, self.destination)

    def test_zip_install_rejects_duplicate_binary_names(self):
        archive = self.make_zip(
            [("first/tool.exe", b"one"), ("second/tool.exe", b"two")]
        )
        with self.assertRaisesRegex(ValueError, "duplicate binary"):
            canary.install_asset(
                self.asset("zip", "tool.exe"), archive, self.destination
            )

    def test_tar_install_rejects_links(self):
        path = self.root / "link.tar.gz"
        with tarfile.open(path, "w:gz") as archive:
            info = tarfile.TarInfo("tool")
            info.type = tarfile.SYMTYPE
            info.linkname = "outside"
            archive.addfile(info)
        with self.assertRaisesRegex(ValueError, "link"):
            canary.install_asset(self.asset("tar.gz"), path, self.destination)


class CommandTests(unittest.TestCase):
    def result(self, stdout):
        return canary.CommandResult(("tool",), 0, stdout, "", 1)

    def test_run_command_records_real_process_result(self):
        result = canary.run_command(
            [sys.executable, "-c", "print('ok')"], env={}, expected_exit={0}
        )
        self.assertEqual(0, result.exit_code)
        self.assertEqual("ok\n", result.stdout)
        self.assertEqual("", result.stderr)
        self.assertGreaterEqual(result.elapsed_ms, 0)

    def test_run_command_rejects_unexpected_exit(self):
        with self.assertRaisesRegex(ValueError, "unexpected exit 3"):
            canary.run_command(
                [sys.executable, "-c", "raise SystemExit(3)"],
                env={},
                expected_exit={0},
            )

    def test_run_command_uses_explicit_working_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            result = canary.run_command(
                [sys.executable, "-c", "import pathlib; print(pathlib.Path.cwd())"],
                env={},
                expected_exit={0},
                cwd=Path(directory),
            )
        self.assertEqual(str(Path(directory).resolve()) + "\n", result.stdout)

    def test_identity_accepts_all_pinned_release_shapes(self):
        outputs = {
            "ao2": "ao2 0.5.11\ntarget=macos-aarch64\ngit_commit=8307795b3434af920f6cef088e56ca8fcc76775b\n",
            "ao2-control-plane": "ao2-cp-server 0.1.19\n",
            "ao-mission": "ao-mission version=0.1.5 source_sha=5d4562578a4751d56910ef108b930fbb8dc91e7d\n",
            "ao-atlas": "ao-atlas version=v0.2.1 source_sha=3603a2bb8af5adafcd9ff17b807ab89f32283d18\n",
            "ao-command": json.dumps(
                {
                    "schema_version": "ao.command.version.v0.1",
                    "version": "0.1.3",
                    "source_commit": "ffef6d76306e892c3e7a7f39734433d5a832006a",
                    "provider_calls": False,
                }
            ),
            "ao-forge": "ao-forge version=0.1.5 source_sha=d1723769949269dcd0589916d83769dcb7275f98\n",
            "ao-covenant": json.dumps(
                {
                    "schema_version": "covenant.version-result.v1",
                    "version": "v0.1.1",
                    "commit": "2fd72a0426a747868826581612fa1dc9727b53b9",
                    "date": "2026-08-05T07:05:07Z",
                    "go_version": "go1.26.4",
                    "os": "darwin",
                    "arch": "amd64",
                }
            ),
        }
        assets = {asset.component: asset for asset in canary.select_assets("macos-aarch64")}
        for component, output in outputs.items():
            with self.subTest(component=component):
                canary.verify_identity(assets[component], self.result(output))

    def test_identity_rejects_wrong_version(self):
        asset = canary.select_assets("macos-aarch64")[0]
        with self.assertRaisesRegex(ValueError, "AO2 identity mismatch"):
            canary.verify_identity(asset, self.result("ao2 0.5.10\n"))

    def test_command_record_redacts_temporary_paths_from_all_fields(self):
        root = "/var/folders/x/T/ao-public-stack-canary-private"
        result = canary.CommandResult(
            (root + "/bin/tool", root + "/input.json"),
            0,
            root + "/stdout\n",
            root + "/stderr\n",
            1,
        )
        record = canary.command_record(result)
        self.assertNotIn(root, json.dumps(record))
        self.assertEqual("$CANARY_ROOT/stdout\n", record["stdout"])
        self.assertEqual("$CANARY_ROOT/stderr\n", record["stderr"])


class ReportTests(unittest.TestCase):
    def valid_report(self):
        components = [
            ("ao2", "v0.5.11"),
            ("ao2-control-plane", "v0.1.19"),
            ("ao-mission", "v0.1.5"),
            ("ao-atlas", "v0.2.1"),
            ("ao-command", "v0.1.3"),
            ("ao-forge", "v0.1.5"),
            ("ao-covenant", "v0.1.1"),
        ]
        views = {
            name: {
                "index_digest": "sha256:" + "1" * 64,
                "state_digest": "sha256:" + str(index) * 64,
                "canonical": {"mission_id": "mission-public-stack-canary"},
            }
            for index, name in enumerate(
                ("inspect", "checkpoint", "event-index", "command-readback"), 2
            )
        }
        return {
            "schema": "ao.architecture.public-stack-canary.v0.1",
            "status": "passed",
            "target": "macos-aarch64",
            "runner": {"system": "Darwin", "machine": "arm64", "python": "3.13.0"},
            "components": [
                {
                    "component": component,
                    "version": version,
                    "url": f"https://github.com/uesugitorachiyo/{component}/releases/download/{version}/asset",
                    "sha256": "a" * 64,
                    "bytes": 1,
                    **(
                        {"execution_mode": "rosetta-2", "binary_arch": "amd64"}
                        if component == "ao-covenant"
                        else {"execution_mode": "native"}
                    ),
                }
                for component, version in components
            ],
            "commands": [{"argv": ["tool"], "exit_code": 0}],
            "reconciliation": {
                "views": views,
                "command_status": {
                    "mission_id": "mission-public-stack-canary",
                    "operator_mode": "read_only",
                    "safe_to_execute": False,
                },
            },
            "provider_calls": 0,
            "credential_uses": 0,
            "publications": 0,
            "deployments": 0,
            "external_mutations": 0,
            "cleanup_succeeded": True,
        }

    def test_valid_report_accepts_distinct_surface_state_digests(self):
        canary.validate_report(self.valid_report())

    def test_report_requires_all_seven_components(self):
        report = self.valid_report()
        report["components"].pop()
        with self.assertRaisesRegex(ValueError, "seven components"):
            canary.validate_report(report)

    def test_report_denies_external_mutations(self):
        report = self.valid_report()
        report["external_mutations"] = 1
        with self.assertRaisesRegex(ValueError, "external_mutations must be zero"):
            canary.validate_report(report)

    def test_report_rejects_terminal_index_disagreement(self):
        report = self.valid_report()
        report["reconciliation"]["views"]["checkpoint"]["index_digest"] = (
            "sha256:" + "9" * 64
        )
        with self.assertRaisesRegex(ValueError, "index digest disagreement"):
            canary.validate_report(report)

    def test_report_requires_command_status_for_same_mission(self):
        report = self.valid_report()
        report["reconciliation"]["command_status"] = {
            "mission_id": "different-mission",
            "operator_mode": "read_only",
            "safe_to_execute": False,
        }
        with self.assertRaisesRegex(ValueError, "Command status mission disagreement"):
            canary.validate_report(report)

    def test_report_requires_distinct_surface_state_digests(self):
        report = self.valid_report()
        report["reconciliation"]["views"]["checkpoint"]["state_digest"] = (
            report["reconciliation"]["views"]["inspect"]["state_digest"]
        )
        with self.assertRaisesRegex(ValueError, "state digests must be distinct"):
            canary.validate_report(report)

    def test_report_rejects_wrong_runner_architecture(self):
        report = self.valid_report()
        report["runner"]["machine"] = "x86_64"
        with self.assertRaisesRegex(ValueError, "runner does not match target"):
            canary.validate_report(report)

    def test_macos_report_requires_declared_covenant_translation(self):
        report = self.valid_report()
        covenant = next(item for item in report["components"] if item["component"] == "ao-covenant")
        covenant["execution_mode"] = "native"
        with self.assertRaisesRegex(ValueError, "Covenant translation"):
            canary.validate_report(report)


class TerminalFixtureTests(unittest.TestCase):
    def test_fixture_binds_four_ordered_artifacts_by_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path = canary.write_terminal_fixture(root)
            manifest = json.loads(manifest_path.read_text())
            self.assertEqual("ao.canonical-terminal-index-input.v1", manifest["contract_version"])
            self.assertEqual("ao-stack-public-canary-v0.1", manifest["mission_id"])
            self.assertEqual(
                ["lease", "root", "duration", "terminal"],
                [artifact["role"] for artifact in manifest["artifacts"]],
            )
            for sequence, artifact in enumerate(manifest["artifacts"]):
                path = root / artifact["path"]
                self.assertEqual(sequence, artifact["sequence"])
                self.assertEqual(
                    "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest(),
                    artifact["sha256"],
                )

    def test_command_status_fixture_uses_exact_v01_input_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            path = canary.write_command_status_fixture(Path(directory))
            document = json.loads(path.read_text())
        self.assertEqual("ao.command.mission-status.v0.1", document["schema"])
        self.assertEqual("ao-stack-public-canary-v0.1", document["mission_id"])
        self.assertNotIn("command_schema_version", document)


class AssemblyTests(unittest.TestCase):
    def test_assembly_downloads_verifies_installs_and_reads_seven_identities(self):
        script = b"""#!/usr/bin/env python3
import json, pathlib, sys
name = pathlib.Path(sys.argv[0]).name
outputs = {
  'ao2': 'ao2 0.5.11\\ntarget=macos-aarch64\\ngit_commit=8307795b3434af920f6cef088e56ca8fcc76775b\\n',
  'ao2-cp-server': 'ao2-cp-server 0.1.19\\n',
  'ao-mission': 'ao-mission version=0.1.5 source_sha=5d4562578a4751d56910ef108b930fbb8dc91e7d\\n',
  'ao-atlas': 'ao-atlas version=v0.2.1 source_sha=3603a2bb8af5adafcd9ff17b807ab89f32283d18\\n',
  'ao-command': json.dumps({'schema_version':'ao.command.version.v0.1','version':'0.1.3','source_commit':'ffef6d76306e892c3e7a7f39734433d5a832006a','provider_calls':False}) + '\\n',
  'forge': 'ao-forge version=0.1.5 source_sha=d1723769949269dcd0589916d83769dcb7275f98\\n',
  'covenant': json.dumps({'schema_version':'covenant.version-result.v1','version':'v0.1.1','commit':'2fd72a0426a747868826581612fa1dc9727b53b9','date':'2026-08-05T07:05:07Z','go_version':'go1.26.4','os':'darwin','arch':'amd64'}) + '\\n',
}
sys.stdout.write(outputs[name])
"""
        digest = hashlib.sha256(script).hexdigest()
        specifications = (
            ("ao2", "v0.5.11", "8307795b3434af920f6cef088e56ca8fcc76775b", "ao2"),
            ("ao2-control-plane", "v0.1.19", "5de3541e9007e12d95b125e7f911c02932e21479", "ao2-cp-server"),
            ("ao-mission", "v0.1.5", "5d4562578a4751d56910ef108b930fbb8dc91e7d", "ao-mission"),
            ("ao-atlas", "v0.2.1", "3603a2bb8af5adafcd9ff17b807ab89f32283d18", "ao-atlas"),
            ("ao-command", "v0.1.3", "ffef6d76306e892c3e7a7f39734433d5a832006a", "ao-command"),
            ("ao-forge", "v0.1.5", "d1723769949269dcd0589916d83769dcb7275f98", "forge"),
            ("ao-covenant", "v0.1.1", "2fd72a0426a747868826581612fa1dc9727b53b9", "covenant"),
        )
        assets = tuple(
            canary.Asset(
                component=component,
                version=version,
                source_sha=source,
                url=f"https://github.com/uesugitorachiyo/{component}/releases/download/{version}/{binary}",
                sha256=digest,
                archive="raw",
                binary=binary,
            )
            for component, version, source, binary in specifications
        )

        def fetch(_url, destination):
            destination.write_bytes(script)
            return len(script)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            records, commands, binaries = canary.assemble_components(
                assets,
                root / "downloads",
                root / "bin",
                os.environ.copy(),
                fetch=fetch,
            )
        self.assertEqual(7, len(records))
        self.assertEqual(7, len(commands))
        self.assertEqual(set(record["component"] for record in records), set(binaries))
        self.assertTrue(all(command.exit_code == 0 for command in commands))

    def test_sanitized_environment_removes_credentials_and_provider_values(self):
        environment = canary.sanitized_environment(
            {
                "PATH": "/bin",
                "SYSTEMROOT": "C:\\Windows",
                "GITHUB_TOKEN": "secret",
                "OPENAI_" + "API_" + "KEY": "secret",
                "AO_PROVIDER": "live",
                "SSH_AUTH_SOCK": "/tmp/socket",
                "AWS_ACCESS_KEY_ID": "secret",
                "CI_JOB_JWT": "secret",
                "HOME": "/private/home",
            }
        )
        self.assertEqual({"PATH": "/bin", "SYSTEMROOT": "C:\\Windows"}, environment)

    def test_canary_environment_routes_mission_state_to_temporary_root(self):
        environment = canary.canary_environment(
            {"PATH": "/bin", "GITHUB_TOKEN": "secret"}, Path("temporary")
        )
        self.assertEqual("/bin", environment["PATH"])
        self.assertEqual(str(Path("temporary/mission-home")), environment["AO_MISSION_HOME"])
        self.assertNotIn("GITHUB_TOKEN", environment)


class WorkflowTests(unittest.TestCase):
    def test_workflow_runs_three_read_only_native_targets_and_uploads_results(self):
        workflow = (Path(__file__).parents[1] / ".github/workflows/public-stack-canary.yml").read_text()
        for runner, target in (
            ("ubuntu-latest", "linux-x86_64"),
            ("macos-15", "macos-aarch64"),
            ("windows-latest", "windows-x86_64"),
        ):
            self.assertEqual(1, workflow.count(f"runner: {runner}"))
            self.assertEqual(1, workflow.count(f"target: {target}"))
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertIn("--target ${{ matrix.target }}", workflow)
        self.assertIn("actions/upload-artifact@", workflow)
        self.assertNotIn("secrets.", workflow)
        self.assertNotIn("contents: write", workflow)


if __name__ == "__main__":
    unittest.main()
