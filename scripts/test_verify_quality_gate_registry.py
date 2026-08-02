from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("verify_quality_gate_registry.py")
REPO_ROOT = Path(__file__).resolve().parents[1]


def valid_manifest(repository: str, lifecycle: str = "active_hosted") -> dict[str, object]:
    return {
        "schema_version": "ao.quality-gates.v1",
        "repository": repository,
        "lifecycle": lifecycle,
        "supported_platforms": ["linux", "macos", "windows"],
        "required_tools": ["python3"],
        "generated_paths": ["tmp/**"],
        "protected_paths": [".git/**"],
        "compatibility": {
            "minimum_consumer_version": "1.0.0",
            "owner": repository,
        },
        "evidence": {
            "public_safe": True,
            "local_artifact_root": "tmp/quality-gates",
            "maximum_result_bytes": 262144,
        },
        "levels": {
            "commit": {
                "snapshot": "staged_tree",
                "maximum_duration_seconds": 10,
                "network_allowed": False,
                "mutates_source": False,
                "steps": [
                    {
                        "id": "diff-check",
                        "argv": ["git", "diff", "--cached", "--check"],
                        "timeout_seconds": 5,
                        "path_triggers": ["**"],
                    }
                ],
            },
            "push": {
                "snapshot": "outgoing_commits",
                "maximum_duration_seconds": 120,
                "network_allowed": False,
                "mutates_source": False,
                "steps": [
                    {
                        "id": "focused-tests",
                        "argv": ["python3", "-m", "unittest"],
                        "timeout_seconds": 90,
                        "path_triggers": ["scripts/**", "docs/**"],
                    }
                ],
            },
            "full": {
                "snapshot": "source_head",
                "maximum_duration_seconds": 1800,
                "network_allowed": False,
                "mutates_source": False,
                "steps": [
                    {
                        "id": "architecture",
                        "argv": ["python3", "scripts/verify_architecture.py"],
                        "timeout_seconds": 300,
                        "path_triggers": ["**"],
                    }
                ],
            },
        },
    }


class RegistryFixture:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.layout = root / "layout.json"
        self.registry = root / "registry.json"
        self.repositories = [
            {"name": "ao-architecture", "lifecycle": "active_hosted"},
            {"name": "ao-local", "lifecycle": "active_local_only"},
        ]
        for entry in self.repositories:
            (root / entry["name"]).mkdir()
        self.write_layout()
        self.write_manifest("ao-architecture")
        self.write_registry(
            [
                {
                    "repository": "ao-architecture",
                    "lifecycle": "active_hosted",
                    "manifest_path": "ao-quality-gates.json",
                    "adoption_status": "adopted",
                    "command_owner": "ao-architecture",
                },
                {
                    "repository": "ao-local",
                    "lifecycle": "active_local_only",
                    "manifest_path": "ao-quality-gates.json",
                    "adoption_status": "planned",
                    "command_owner": "ao-local",
                },
            ]
        )

    def write_layout(self) -> None:
        self.layout.write_text(
            json.dumps({"schema_version": "1.0.0", "repositories": self.repositories}, indent=2) + "\n",
            encoding="utf-8",
        )

    def write_manifest(self, repository: str, document: dict[str, object] | None = None) -> Path:
        path = self.root / repository / "ao-quality-gates.json"
        path.write_text(
            json.dumps(document or valid_manifest(repository), indent=2) + "\n",
            encoding="utf-8",
        )
        return path

    def write_registry(self, repositories: list[dict[str, object]]) -> None:
        self.registry.write_text(
            json.dumps(
                {
                    "schema_version": "ao.stack.quality-gate-registry.v1",
                    "manifest_schema_version": "ao.quality-gates.v1",
                    "lifecycle_source": "docs/agent-instructions/layout-v1.json",
                    "repositories": repositories,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )


class VerifyQualityGateRegistryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.fixture = RegistryFixture(Path(self.temp.name))

    def run_validator(self, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--workspace-root",
                str(self.fixture.root),
                "--layout",
                str(self.fixture.layout),
                "--registry",
                str(self.fixture.registry),
                *extra,
            ],
            text=True,
            capture_output=True,
            check=False,
        )

    def assert_rejected(self, code: str, *extra: str) -> None:
        result = self.run_validator(*extra)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(code, result.stderr)

    def test_accepts_adopted_and_planned_repositories(self) -> None:
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "passed")
        self.assertEqual(payload["repository_count"], 2)
        self.assertEqual(payload["adopted_count"], 1)

    def test_require_adopted_rejects_planned_repository(self) -> None:
        self.assert_rejected("REGISTRY_ADOPTION_INCOMPLETE", "--require-adopted")

    def test_rejects_duplicate_json_keys(self) -> None:
        path = self.fixture.root / "ao-architecture" / "ao-quality-gates.json"
        raw = path.read_text(encoding="utf-8")
        path.write_text(raw.replace('"repository":', '"repository": "duplicate", "repository":', 1), encoding="utf-8")
        self.assert_rejected("MANIFEST_DUPLICATE_KEY")

    def test_rejects_unknown_manifest_schema(self) -> None:
        document = valid_manifest("ao-architecture")
        document["schema_version"] = "ao.quality-gates.v2"
        self.fixture.write_manifest("ao-architecture", document)
        self.assert_rejected("MANIFEST_SCHEMA_UNSUPPORTED")

    def test_rejects_repository_identity_mismatch(self) -> None:
        self.fixture.write_manifest("ao-architecture", valid_manifest("ao-local"))
        self.assert_rejected("MANIFEST_REPOSITORY_MISMATCH")

    def test_rejects_string_command_instead_of_argv(self) -> None:
        document = valid_manifest("ao-architecture")
        document["levels"]["commit"]["steps"][0]["argv"] = "git diff --cached --check"
        self.fixture.write_manifest("ao-architecture", document)
        self.assert_rejected("STEP_ARGV_REQUIRED")

    def test_rejects_shell_evaluation(self) -> None:
        document = valid_manifest("ao-architecture")
        document["levels"]["commit"]["steps"][0]["argv"] = ["sh", "-c", "git diff --cached --check"]
        self.fixture.write_manifest("ao-architecture", document)
        self.assert_rejected("SHELL_EVALUATION_FORBIDDEN")

    def test_rejects_network_or_mutation_in_fast_gate(self) -> None:
        document = valid_manifest("ao-architecture")
        document["levels"]["commit"]["network_allowed"] = True
        document["levels"]["push"]["mutates_source"] = True
        self.fixture.write_manifest("ao-architecture", document)
        self.assert_rejected("FAST_GATE_NETWORK_FORBIDDEN")
        self.assert_rejected("FAST_GATE_MUTATION_FORBIDDEN")

    def test_rejects_result_limit_too_small_for_consumer_evidence(self) -> None:
        document = valid_manifest("ao-architecture")
        document["evidence"]["maximum_result_bytes"] = 4095
        self.fixture.write_manifest("ao-architecture", document)
        self.assert_rejected("EVIDENCE_SIZE_LIMIT_INVALID")

    def test_rejects_unsafe_path_pattern(self) -> None:
        document = valid_manifest("ao-architecture")
        document["generated_paths"] = ["../outside/**"]
        self.fixture.write_manifest("ao-architecture", document)
        self.assert_rejected("PATH_PATTERN_UNSAFE")

    @unittest.skipIf(os.name == "nt", "symlink creation requires elevated Windows privileges")
    def test_rejects_symlinked_manifest(self) -> None:
        path = self.fixture.root / "ao-architecture" / "ao-quality-gates.json"
        target = self.fixture.root / "manifest-target.json"
        target.write_text(json.dumps(valid_manifest("ao-architecture")), encoding="utf-8")
        path.unlink()
        path.symlink_to(target)
        self.assert_rejected("MANIFEST_SYMLINK")

    def test_rejects_oversized_manifest(self) -> None:
        path = self.fixture.root / "ao-architecture" / "ao-quality-gates.json"
        path.write_text(" " * (256 * 1024 + 1), encoding="utf-8")
        self.assert_rejected("MANIFEST_SIZE_LIMIT")

    def test_rejects_missing_registry_repository(self) -> None:
        registry = json.loads(self.fixture.registry.read_text(encoding="utf-8"))
        registry["repositories"] = registry["repositories"][:1]
        self.fixture.registry.write_text(json.dumps(registry), encoding="utf-8")
        self.assert_rejected("REGISTRY_MISSING_REPOSITORY")

    def test_rejects_missing_adopted_manifest(self) -> None:
        (self.fixture.root / "ao-architecture" / "ao-quality-gates.json").unlink()
        self.assert_rejected("MANIFEST_REQUIRED")

    def test_repository_contract_validates(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--workspace-root",
                str(REPO_ROOT.parent),
                "--repository",
                "ao-architecture",
                "--repository-root",
                str(REPO_ROOT),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
