#!/usr/bin/env python3
"""Regression tests for the AO development-baseline manifest verifier."""

from __future__ import annotations

import hashlib
import json
import copy
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from verify_development_baseline import (  # noqa: E402
    EXPECTED_DEVELOPMENT_GATES,
    InputError,
    STABLE_REPOSITORIES,
    canonical_bytes,
    identity_digest,
    load_json_file,
    sha256_file,
    validate_manifest,
    validate_development_gates,
    validate_repository_profile,
)


REPOSITORY_FIXTURES = [
    ("ao-architecture", "3788f991c40310e81c5ab17e4b24f04c78515c78", "architecture_truth"),
    ("ao-mission", "1aeb2cd78c8a7c5df100cdf1bd17d20c478ca47e", "mission_state"),
    ("ao-blueprint", "ec6a80b60b54c0c0ac1822f873c1abf337fe5eb5", "requirements_authorization"),
    ("ao-atlas", "3eec009d7541edd29fb5383d209cfdb480e664bc", "workgraph_context"),
    ("ao-foundry", "028ec4d50847247ee48c1d8d4560a4eda3422550", "portfolio_scheduling"),
    ("ao-forge", "b17a6dc58d4938b3dbe10ec949b6b1008b192379", "goal_run"),
    ("ao-covenant", "7d2af0d3446757f096ebf3ce51e0918716daf7ff", "policy_contract_authority"),
    ("ao2", "880f32ce8d9af5ba6e50aa5885c214c04f23f20d", "execution"),
    ("ao2-control-plane", "4e41da173dc9f1ee37f4ae99b85791e5f05ea453", "evidence_observation"),
    ("ao-command", "ffef6d76306e892c3e7a7f39734433d5a832006a", "operator_presentation"),
    ("ao-arena", "88a52d9a42c5bffe998b45c5046f36be0cf5ea43", "benchmark"),
    ("ao-crucible", "64227e3ee305cc3399063b567e02a548b5bc1855", "adversarial_assurance"),
    ("ao-sentinel", "c301b1192c77a6b1833c49a5c9230491be50a258", "monitoring"),
    ("ao-promoter", "5b103a66476e45bcf0c7fdcf4fffdb82b415ff72", "promotion_decision"),
]

AGENTS_DIGESTS = {
    "ao-mission": "e85e21a7288e92e98bacb9957ba54c87f6c9678c6e5c3167d65e4992cb4afc45",
    "ao-foundry": "2ada1272eef474cd1d8fe162ea28a0d060211b22ed334b5a1846e57bcc3976c2",
    "ao-forge": "2b4abb5c872797b89f3ec410a3ab654cd9898f21a289d8cc19f9da5f0ab24fb2",
    "ao-covenant": "4be243338aadbdd1f04a124ac95ee51e486a44e8ec8becaed3cb0d8fe8926b7b",
    "ao2-control-plane": "8b1739dc1e3e74d4df6332e8b1795387da5c24ee8530ea879e59804cdaa317f0",
    "ao-command": "a50c855a8dcb47b23ac4656633ea8be0a80e0228df9c636135c7c020f0def6ca",
    "ao-crucible": "28839fb5647f15e477026de1de236b2f7ec58538241ad6d9fe348245f3a64e93",
    "ao-sentinel": "63ce5e1685e7cf27acd5114f2ee4f3f5d7ea0b5eb1faf9783cc1ae26a92bd35f",
    "ao-promoter": "2136efca3d324b5ff748b530c59b4c4bccedbf0c063763544d4d2adcdb4d7c9d",
}

AGENTS_GATE_COUNTS = {
    "ao-mission": 4,
    "ao-foundry": 2,
    "ao-forge": 4,
    "ao-covenant": 4,
    "ao2-control-plane": 4,
    "ao-command": 2,
    "ao-crucible": 3,
    "ao-sentinel": 3,
    "ao-promoter": 3,
}

QUALITY_GATES = {
    "ao-architecture": ("2f3c727b1e8343cc373c9d561eb5b9ea953f851ac9f767df2e95b9386d83c655", ["architecture-verifier", "python-regressions"]),
    "ao-blueprint": ("b56d6eb7c0e4636a451b5d3a9139dc992a454967a5adf202273581c236b7eeb8", ["production-readiness"]),
    "ao-atlas": ("5d71e2021944992173e83a1e1c92c1d1eec40a1de85ef0aa3fd072a7feb9a383", ["go-tests", "go-vet", "go-build"]),
    "ao2": ("f6d8d255c77d4876d514dfb84d68956fc2fed1981b41a756da4c11657f740162", ["workspace-verification", "rust-architecture"]),
    "ao-arena": ("c2e2207b5a67e832615534fbffa9792127c01eac468156600bfe3253815d4980", ["go-tests", "go-vet", "go-build"]),
}


def valid_repositories() -> list[dict[str, object]]:
    repositories = []
    for name, commit, role in REPOSITORY_FIXTURES:
        if name in QUALITY_GATES:
            digest, ids = QUALITY_GATES[name]
            gate_source = {
                "path": "ao-quality-gates.json",
                "sha256": digest,
                "gate_refs": [
                    f"ao-quality-gates.json#levels.full.steps.{gate_id}"
                    for gate_id in ids
                ],
            }
        else:
            gate_source = {
                "path": "AGENTS.md",
                "sha256": AGENTS_DIGESTS[name],
                "gate_refs": [
                    f"AGENTS.md#Verification:{ordinal}"
                    for ordinal in range(1, AGENTS_GATE_COUNTS[name] + 1)
                ],
            }
        repositories.append(
            {
                "name": name,
                "path": name,
                "upstream_url": f"https://github.com/uesugitorachiyo/{name}.git",
                "commit": commit,
                "branch_metadata": "main",
                "source_role": role,
                "gate_source": gate_source,
                "development_gates": copy.deepcopy(EXPECTED_DEVELOPMENT_GATES[name]),
            }
        )
    return repositories


class StrictLoaderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def write_bytes(self, body: bytes, name: str = "input.json") -> Path:
        path = self.root / name
        path.write_bytes(body)
        return path

    def test_duplicate_key_is_rejected(self) -> None:
        path = self.write_bytes(b'{"schema":"one","schema":"two"}')
        with self.assertRaisesRegex(InputError, "duplicate key: schema"):
            load_json_file(path, 1024)

    def test_oversized_input_is_rejected_before_decode(self) -> None:
        path = self.write_bytes(b"{} " * 1024)
        with self.assertRaisesRegex(InputError, "exceeds 32 bytes"):
            load_json_file(path, 32)

    def test_non_utf8_input_is_rejected(self) -> None:
        path = self.write_bytes(b'{"schema":"\xff"}')
        with self.assertRaisesRegex(InputError, "UTF-8"):
            load_json_file(path, 1024)

    def test_non_regular_input_is_rejected(self) -> None:
        with self.assertRaisesRegex(InputError, "not a regular file"):
            load_json_file(self.root / "missing.json", 1024)

    def test_identity_uses_sorted_compact_utf8_json(self) -> None:
        left = {"z": 1, "a": ["é", True]}
        right = {"a": ["é", True], "z": 1}
        self.assertEqual(canonical_bytes(left), canonical_bytes(right))
        expected = "sha256:" + hashlib.sha256(canonical_bytes(left)).hexdigest()
        self.assertEqual(identity_digest(left), expected)
        self.assertTrue(re.fullmatch(r"sha256:[0-9a-f]{64}", expected))

    def test_json_formatting_does_not_change_identity(self) -> None:
        compact = json.loads('{"a":1,"b":[2,3]}')
        spaced = json.loads('{\n  "b": [2, 3],\n  "a": 1\n}')
        self.assertEqual(identity_digest(compact), identity_digest(spaced))


class RepositoryProfileTests(unittest.TestCase):
    def assert_profile_error(self, expected: str, repositories: list[dict[str, object]]) -> None:
        self.assertIn(expected, validate_repository_profile(repositories))

    def test_exact_stable_profile_is_valid(self) -> None:
        self.assertEqual(tuple(name for name, _, _ in REPOSITORY_FIXTURES), STABLE_REPOSITORIES)
        self.assertEqual(validate_repository_profile(valid_repositories()), [])

    def test_duplicate_repository_is_rejected(self) -> None:
        repositories = valid_repositories()
        repositories.append(copy.deepcopy(repositories[0]))
        self.assert_profile_error("duplicate repository: ao-architecture", repositories)

    def test_missing_stable_member_is_rejected(self) -> None:
        repositories = [item for item in valid_repositories() if item["name"] != "ao-mission"]
        self.assert_profile_error("missing stable member: ao-mission", repositories)

    def test_ao_next_in_stable_profile_is_rejected(self) -> None:
        repositories = valid_repositories()
        extra = copy.deepcopy(repositories[0])
        extra.update(name="ao-next", path="ao-next", upstream_url="https://github.com/uesugitorachiyo/ao-next.git")
        repositories.append(extra)
        self.assert_profile_error("unexpected stable member: ao-next", repositories)

    def test_malformed_commit_is_rejected(self) -> None:
        repositories = valid_repositories()
        repositories[0]["commit"] = "main"
        self.assert_profile_error(
            "ao-architecture repository commit must be lowercase 40-character hex",
            repositories,
        )

    def test_moving_branch_only_identity_is_rejected(self) -> None:
        repositories = valid_repositories()
        del repositories[0]["commit"]
        self.assert_profile_error(
            "ao-architecture repository identity cannot use only a moving branch",
            repositories,
        )

    def test_unsafe_relative_path_is_rejected(self) -> None:
        repositories = valid_repositories()
        repositories[0]["path"] = "../ao-architecture"
        self.assert_profile_error("ao-architecture unsafe repository path", repositories)

    def test_noncanonical_upstream_is_rejected(self) -> None:
        repositories = valid_repositories()
        repositories[0]["upstream_url"] = "git@github.com:uesugitorachiyo/ao-architecture.git"
        self.assert_profile_error("ao-architecture repository upstream must be canonical HTTPS", repositories)

    def test_unknown_repository_property_is_rejected(self) -> None:
        repositories = valid_repositories()
        repositories[0]["unknown"] = True
        self.assert_profile_error("ao-architecture repository unknown property: unknown", repositories)

    def test_gate_source_requires_safe_exact_locator(self) -> None:
        repositories = valid_repositories()
        repositories[0]["gate_source"]["gate_refs"] = ["../README.md"]
        self.assert_profile_error("ao-architecture invalid gate ref: ../README.md", repositories)

    def test_development_gate_contract_is_closed_and_fail_closed(self) -> None:
        gate = {
            "id": "unit-tests",
            "argv": ["go", "test", "./..."],
            "timeout_seconds": 300,
            "shell": "direct",
            "required": True,
            "environment": {},
        }
        self.assertEqual(validate_development_gates("fixture", [gate]), [])
        duplicate = [copy.deepcopy(gate), copy.deepcopy(gate)]
        self.assertIn("fixture duplicate development gate: unit-tests", validate_development_gates("fixture", duplicate))
        cases = (
            (lambda item: item.update(argv="go test ./..."), "argv is invalid"),
            (lambda item: item.update(shell="powershell-string"), "shell is invalid"),
            (lambda item: item.update(timeout_seconds=0), "timeout is invalid"),
            (lambda item: item.update(required=False), "must be required"),
            (lambda item: item.update(environment={"TOKEN": "value"}), "environment is unsafe"),
            (lambda item: item.update(argv=["gh", "release", "create"]), "authority-bearing argv"),
            (lambda item: item.update(skip="windows"), "unknown property: skip"),
        )
        for mutate, expected in cases:
            candidate = copy.deepcopy(gate)
            mutate(candidate)
            self.assertTrue(
                any(expected in error for error in validate_development_gates("fixture", [candidate])),
                expected,
            )

    def test_schema_closes_all_contract_objects(self) -> None:
        schema_path = Path(__file__).resolve().parents[1] / "docs" / "contracts" / "development-baseline-manifest-v1.schema.json"
        schema = load_json_file(schema_path, 256 * 1024)
        self.assertFalse(schema["additionalProperties"])
        for name in (
            "repository",
            "gateSource",
            "developmentGate",
            "releaseInput",
            "runtimeRelease",
            "toolchain",
            "platformOverride",
            "authority",
        ):
            self.assertFalse(schema["$defs"][name]["additionalProperties"], name)


class RuntimeReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repository_root = Path(__file__).resolve().parents[1]
        cls.manifest_path = cls.repository_root / "stack" / "development-baseline-manifest.json"
        cls.release_path = cls.repository_root / "stack" / "current-release-manifest.json"
        cls.manifest = load_json_file(cls.manifest_path, 1024 * 1024)
        cls.release_input = load_json_file(cls.release_path, 1024 * 1024)

    def errors_after(self, mutate) -> list[str]:
        document = copy.deepcopy(self.manifest)
        mutate(document)
        return validate_manifest(document, self.release_input, self.release_path)

    def test_real_release_input_has_frozen_digest(self) -> None:
        self.assertEqual(
            sha256_file(self.release_path),
            "903061a5983068040d19c05adb5e6d0d29f0bf15a59f1bfbf533ac448f0f4e8d",
        )

    def test_exact_manifest_release_binding_is_valid(self) -> None:
        self.assertEqual(validate_manifest(self.manifest, self.release_input, self.release_path), [])

    def test_release_input_digest_drift_is_rejected(self) -> None:
        errors = self.errors_after(lambda doc: doc["release_input"].update(sha256="0" * 64))
        self.assertIn("release input digest drift", errors)

    def test_runtime_release_count_is_exact(self) -> None:
        errors = self.errors_after(lambda doc: doc["runtime_releases"].pop())
        self.assertIn("runtime release count must be 7", errors)

    def test_runtime_release_tag_drift_is_rejected(self) -> None:
        errors = self.errors_after(lambda doc: doc["runtime_releases"][2].update(tag="v9.9.9"))
        self.assertIn("ao-mission runtime release tag drift", errors)

    def test_runtime_release_tag_target_drift_is_rejected(self) -> None:
        errors = self.errors_after(lambda doc: doc["runtime_releases"][4].update(tag_target="0" * 40))
        self.assertIn("ao-atlas runtime release tag target drift", errors)

    def test_runtime_platform_digest_drift_is_rejected(self) -> None:
        def mutate(document):
            document["runtime_releases"][0]["assets"][2]["sha256"] = "0" * 64

        self.assertIn("ao2 runtime platform digest drift: windows", self.errors_after(mutate))

    def test_supplemental_digest_source_is_required(self) -> None:
        def mutate(document):
            del document["runtime_releases"][1]["supplemental_digest_source"]

        self.assertIn("ao2-control-plane supplemental digest source is required", self.errors_after(mutate))

    def test_unknown_release_input_property_is_rejected(self) -> None:
        self.assertIn(
            "release input unknown property: mutable_ref",
            self.errors_after(lambda doc: doc["release_input"].update(mutable_ref="main")),
        )

    def test_unknown_runtime_release_property_is_rejected(self) -> None:
        self.assertIn(
            "ao2 runtime release unknown property: mutable",
            self.errors_after(lambda doc: doc["runtime_releases"][0].update(mutable=True)),
        )

    def test_unknown_runtime_asset_property_is_rejected(self) -> None:
        self.assertIn(
            "ao2 linux runtime asset unknown property: url",
            self.errors_after(
                lambda doc: doc["runtime_releases"][0]["assets"][0].update(
                    url="https://example.invalid"
                )
            ),
        )

    def test_covenant_macos_asset_requires_rosetta_override(self) -> None:
        def mutate(document):
            document["platform_overrides"] = [
                item for item in document["platform_overrides"] if item["id"] != "covenant-rosetta2"
            ]

        self.assertIn("Covenant macOS asset requires Rosetta 2", self.errors_after(mutate))


class PolicyValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.release_path = root / "stack" / "current-release-manifest.json"
        cls.release_input = load_json_file(cls.release_path, 1024 * 1024)
        cls.manifest = load_json_file(root / "stack" / "development-baseline-manifest.json", 1024 * 1024)

    def errors_after(self, mutate) -> list[str]:
        document = copy.deepcopy(self.manifest)
        mutate(document)
        return validate_manifest(document, self.release_input, self.release_path)

    def test_unknown_top_level_property_is_rejected(self) -> None:
        self.assertIn(
            "manifest unknown property: controller_source_commit",
            self.errors_after(lambda doc: doc.update(controller_source_commit="0" * 40)),
        )

    def test_unknown_toolchain_is_rejected(self) -> None:
        self.assertIn(
            "unexpected toolchain: ruby",
            self.errors_after(lambda doc: doc["toolchains"][0].update(name="ruby")),
        )

    def test_duplicate_toolchain_is_rejected(self) -> None:
        def mutate(document):
            document["toolchains"][1] = copy.deepcopy(document["toolchains"][0])

        self.assertIn("duplicate toolchain: git", self.errors_after(mutate))

    def test_shell_metacharacter_in_version_argv_is_rejected(self) -> None:
        def mutate(document):
            document["toolchains"][0]["version_argv"] = ["git", "--version; whoami"]

        self.assertIn("git toolchain version argv contains shell metacharacters", self.errors_after(mutate))

    def test_undeclared_platform_override_is_rejected(self) -> None:
        def mutate(document):
            document["platform_overrides"].append(
                {"id": "skip-tests", "platform": "windows", "repository": "all", "behavior": "Skip tests."}
            )

        self.assertIn("undeclared platform override: skip-tests", self.errors_after(mutate))

    def test_duplicate_platform_override_is_rejected(self) -> None:
        def mutate(document):
            document["platform_overrides"].append(copy.deepcopy(document["platform_overrides"][0]))

        self.assertIn("duplicate platform override: windows-git-bash", self.errors_after(mutate))

    def test_authority_widening_is_rejected(self) -> None:
        self.assertIn(
            "authority must remain false: provider_calls",
            self.errors_after(lambda doc: doc["authority"].update(provider_calls=True)),
        )

    def test_unknown_authority_property_is_rejected(self) -> None:
        self.assertIn(
            "authority unknown property: deploy_anyway",
            self.errors_after(lambda doc: doc["authority"].update(deploy_anyway=False)),
        )

    def test_exclusion_list_is_exact(self) -> None:
        self.assertIn(
            "excluded repositories must contain only ao-next",
            self.errors_after(lambda doc: doc.update(excluded_repositories=[])),
        )

    def test_profile_and_schema_are_exact(self) -> None:
        self.assertIn(
            "manifest profile must be stable",
            self.errors_after(lambda doc: doc.update(profile="experimental")),
        )
        self.assertIn(
            "manifest schema drift",
            self.errors_after(lambda doc: doc.update(schema="v2")),
        )

    def test_unknown_nested_toolchain_property_is_rejected(self) -> None:
        self.assertIn(
            "git toolchain unknown property: install",
            self.errors_after(lambda doc: doc["toolchains"][0].update(install=True)),
        )


class CommandLineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[1]
        cls.verifier = cls.root / "scripts" / "verify_development_baseline.py"
        cls.manifest = cls.root / "stack" / "development-baseline-manifest.json"
        cls.schema = cls.root / "docs" / "contracts" / "development-baseline-manifest-v1.schema.json"
        cls.release = cls.root / "stack" / "current-release-manifest.json"

    def run_cli(self, manifest: Path, controller: str = "1" * 40) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(self.verifier),
                "--manifest",
                str(manifest),
                "--schema",
                str(self.schema),
                "--release-manifest",
                str(self.release),
                "--controller-commit",
                controller,
            ],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_valid_cli_prints_stable_summary(self) -> None:
        result = self.run_cli(self.manifest)
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.splitlines()
        self.assertEqual(len(lines), 5, lines)
        self.assertEqual(lines[0], f"controller_source_commit={'1' * 40}")
        self.assertRegex(lines[1], r"^baseline_identity=sha256:[0-9a-f]{64}$")
        self.assertEqual(lines[2:], ["repositories=14", "runtime_releases=7", "errors=0"])
        self.assertNotIn(str(self.root), result.stdout)

    def test_controller_commit_is_not_part_of_baseline_identity(self) -> None:
        first = self.run_cli(self.manifest, "1" * 40)
        second = self.run_cli(self.manifest, "2" * 40)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(first.stdout.splitlines()[1], second.stdout.splitlines()[1])

    def test_invalid_manifest_prints_sorted_errors_and_returns_one(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            document = load_json_file(self.manifest, 1024 * 1024)
            document["authority"]["provider_calls"] = True
            invalid = Path(directory) / "invalid.json"
            invalid.write_text(json.dumps(document), encoding="utf-8")
            result = self.run_cli(invalid)
        self.assertEqual(result.returncode, 1)
        errors = result.stderr.splitlines()
        self.assertEqual(errors, sorted(errors))
        self.assertIn("error=authority must remain false: provider_calls", errors)
        self.assertEqual(result.stdout, "")

    def test_invalid_controller_commit_fails_before_validation(self) -> None:
        result = self.run_cli(self.manifest, "main")
        self.assertEqual(result.returncode, 2)
        self.assertIn("controller commit must be lowercase 40-character hex", result.stderr)

    def test_schema_contract_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            schema = Path(directory) / "schema.json"
            schema.write_text("{}", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(self.verifier),
                    "--manifest",
                    str(self.manifest),
                    "--schema",
                    str(schema),
                    "--release-manifest",
                    str(self.release),
                    "--controller-commit",
                    "1" * 40,
                ],
                cwd=self.root,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr.strip(), "error=schema contract drift")


if __name__ == "__main__":
    unittest.main()
