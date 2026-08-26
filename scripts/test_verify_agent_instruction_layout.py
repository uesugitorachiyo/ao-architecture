from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from verify_agent_instruction_layout import (  # noqa: E402
    ManifestError,
    content_fingerprint,
    load_manifest,
    validate_workspace,
)


REPOSITORIES = [
    ("ao-architecture", "active_hosted", "hosted"),
    ("ao-arena", "active_hosted", "hosted"),
    ("ao-atlas", "active_hosted", "hosted"),
    ("ao-blueprint", "active_hosted", "hosted"),
    ("ao-command", "active_hosted", "hosted"),
    ("ao-conductor", "excluded_legacy_hosted", "hosted"),
    ("ao-control-plane", "excluded_legacy_hosted", "hosted"),
    ("ao-covenant", "active_hosted", "hosted"),
    ("ao-covenant-stub-20260617", "excluded_local_stub", "none"),
    ("ao-crucible", "active_hosted", "hosted"),
    ("ao-forge", "active_hosted", "hosted"),
    ("ao-foundry", "active_hosted", "hosted"),
    ("ao-hardening-runner", "active_local_only", "none"),
    ("ao-mission", "active_hosted", "hosted"),
    ("ao-next", "active_hosted", "hosted"),
    ("ao-operator", "excluded_legacy_hosted", "hosted"),
    ("ao-promoter", "active_hosted", "hosted"),
    ("ao-runtime", "excluded_legacy_hosted", "hosted"),
    ("ao-sentinel", "active_hosted", "hosted"),
    ("ao-stack-evaluation", "active_local_only", "none"),
    ("ao2", "active_hosted", "hosted"),
    ("ao2-control-plane", "active_hosted", "hosted"),
]


class LayoutFixture:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.manifest_path = root / "layout.json"
        repositories = []
        for name, lifecycle, remote in REPOSITORIES:
            repo = root / name
            repo.mkdir()
            entry = {
                "name": name,
                "lifecycle": lifecycle,
                "remote": remote,
                "required_root_files": (
                    []
                    if lifecycle in {"excluded_local_stub", "excluded_legacy_hosted"}
                    else ["AGENTS.md", "CLAUDE.md"]
                ),
                "allowed_nested_scopes": [],
            }
            if lifecycle == "excluded_local_stub":
                (repo / "README.md").write_text("Historical fixture.\n", encoding="utf-8")
                entry["exclusion_reason"] = "Historical local stub excluded from rollout."
                entry["content_sha256"] = content_fingerprint(repo)
            elif lifecycle == "excluded_legacy_hosted":
                (repo / "README.md").write_text("Legacy repository fixture.\n", encoding="utf-8")
                (repo / "AGENTS.md").write_text("# Legacy instructions\n", encoding="utf-8")
                subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
                subprocess.run(["git", "config", "user.email", "fixture@example.invalid"], cwd=repo, check=True)
                subprocess.run(["git", "config", "user.name", "Fixture"], cwd=repo, check=True)
                subprocess.run(["git", "add", "README.md", "AGENTS.md"], cwd=repo, check=True)
                subprocess.run(["git", "commit", "-q", "-m", "fixture"], cwd=repo, check=True)
                entry["exclusion_reason"] = "Hosted legacy repository outside the maintained AO Stack."
                entry["expected_head"] = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=repo,
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
            else:
                (repo / "AGENTS.md").write_text(f"# {name} Agent Instructions\n\nRepository guidance.\n", encoding="utf-8")
                (repo / "CLAUDE.md").write_bytes(b"@AGENTS.md\n")
                (repo / ".gitignore").write_text(
                    "CLAUDE.local.md\n.claude/settings.local.json\n",
                    encoding="utf-8",
                )
                if name == "ao-next":
                    entry["allowed_nested_scopes"] = ["mission"]
                    nested = repo / "mission"
                    nested.mkdir()
                    (nested / "AGENTS.md").write_text("# Mission Instructions\n", encoding="utf-8")
                    (nested / "CLAUDE.md").write_bytes(b"@AGENTS.md\n")
            repositories.append(entry)
        self.manifest = {"schema_version": "1.0.0", "repositories": repositories}
        self.write_manifest()

    def repo(self, name: str) -> Path:
        return self.root / name

    def entry(self, name: str) -> dict[str, object]:
        return next(item for item in self.manifest["repositories"] if item["name"] == name)

    def write_manifest(self) -> None:
        self.manifest_path.write_text(
            json.dumps(self.manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def allow_nested(self, repository: str, scope: str) -> Path:
        entry = self.entry(repository)
        entry["allowed_nested_scopes"] = [*entry["allowed_nested_scopes"], scope]
        nested = self.repo(repository) / scope
        nested.mkdir(parents=True, exist_ok=True)
        (nested / "AGENTS.md").write_text("# Scoped Instructions\n\nScoped guidance.\n", encoding="utf-8")
        (nested / "CLAUDE.md").write_bytes(b"@AGENTS.md\n")
        self.write_manifest()
        return nested


class AgentInstructionLayoutTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.fixture = LayoutFixture(Path(self.temp.name))

    def codes(self, *, repository: str | None = None) -> set[str]:
        result = validate_workspace(self.fixture.root, self.fixture.manifest_path, repository=repository)
        return {conflict["code"] for conflict in result["conflicts"]}

    def assert_code(self, expected: str, *, repository: str | None = None) -> None:
        self.assertIn(expected, self.codes(repository=repository))

    def test_accepts_active_local_only_and_excluded_roots(self) -> None:
        result = validate_workspace(self.fixture.root, self.fixture.manifest_path)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["conflicts"], [])
        statuses = {item["name"]: item["status"] for item in result["repositories"]}
        self.assertEqual(statuses["ao-architecture"], "ok")
        self.assertEqual(statuses["ao-conductor"], "excluded_unchanged")
        self.assertEqual(statuses["ao-control-plane"], "excluded_unchanged")
        self.assertEqual(statuses["ao-hardening-runner"], "ok")
        self.assertEqual(statuses["ao-covenant-stub-20260617"], "excluded_unchanged")
        self.assertEqual(statuses["ao-runtime"], "excluded_unchanged")
        self.assertEqual(statuses["ao-operator"], "excluded_unchanged")

    def test_accepts_ao_next_mission_instruction_pair(self) -> None:
        self.assertEqual(self.codes(repository="ao-next"), set())

    def test_accepts_generic_allowed_nested_pair(self) -> None:
        self.fixture.allow_nested("ao2", "crates/ao2-runtime")
        self.assertEqual(self.codes(repository="ao2"), set())

    def test_rejects_ao_next_without_mission_scope(self) -> None:
        self.fixture.entry("ao-next")["allowed_nested_scopes"] = []
        nested = self.fixture.repo("ao-next") / "mission"
        (nested / "AGENTS.md").unlink()
        (nested / "CLAUDE.md").unlink()
        nested.rmdir()
        self.fixture.write_manifest()
        self.assertEqual(self.codes(repository="ao-next"), {"MANIFEST_AO_NEXT_SCOPE"})

    def test_rejects_ao_next_extra_scope(self) -> None:
        self.fixture.allow_nested("ao-next", "extra")
        self.assertEqual(self.codes(repository="ao-next"), {"MANIFEST_AO_NEXT_SCOPE"})

    def test_repository_selector_limits_file_validation(self) -> None:
        (self.fixture.repo("ao-arena") / "AGENTS.md").unlink()
        self.assertEqual(self.codes(repository="ao-architecture"), set())
        self.assertIn("MISSING_ROOT_AGENTS", self.codes(repository="ao-arena"))

    def test_rejects_missing_root_agents(self) -> None:
        (self.fixture.repo("ao-architecture") / "AGENTS.md").unlink()
        self.assert_code("MISSING_ROOT_AGENTS")

    def test_rejects_missing_root_claude(self) -> None:
        (self.fixture.repo("ao-architecture") / "CLAUDE.md").unlink()
        self.assert_code("MISSING_ROOT_CLAUDE")

    def test_rejects_duplicated_claude_rules(self) -> None:
        (self.fixture.repo("ao-architecture") / "CLAUDE.md").write_text(
            "# Claude rules\n\nDuplicated repository rules.\n",
            encoding="utf-8",
        )
        self.assert_code("CLAUDE_BYTES_INVALID")

    def test_rejects_wrong_claude_import_target(self) -> None:
        (self.fixture.repo("ao-architecture") / "CLAUDE.md").write_bytes(b"@README.md\n")
        self.assert_code("CLAUDE_BYTES_INVALID")

    def test_rejects_claude_import_without_final_newline(self) -> None:
        (self.fixture.repo("ao-architecture") / "CLAUDE.md").write_bytes(b"@AGENTS.md")
        self.assert_code("CLAUDE_BYTES_INVALID")

    def test_rejects_symlinked_instruction_file(self) -> None:
        path = self.fixture.repo("ao-architecture") / "CLAUDE.md"
        path.unlink()
        try:
            os.symlink("AGENTS.md", path)
        except OSError as exc:
            if os.name == "nt" and getattr(exc, "winerror", None) == 1314:
                self.skipTest("Windows symlink privilege is unavailable")
            raise
        self.assert_code("INSTRUCTION_SYMLINK")

    def test_rejects_empty_instruction_file(self) -> None:
        (self.fixture.repo("ao-architecture") / "AGENTS.md").write_bytes(b"")
        self.assert_code("EMPTY_INSTRUCTION_FILE")

    def test_rejects_nested_agents_without_claude(self) -> None:
        nested = self.fixture.allow_nested("ao2", "crates/ao2-runtime")
        (nested / "CLAUDE.md").unlink()
        self.assert_code("NESTED_PAIR_MISSING")

    def test_rejects_nested_claude_without_agents(self) -> None:
        nested = self.fixture.allow_nested("ao2", "crates/ao2-runtime")
        (nested / "AGENTS.md").unlink()
        self.assert_code("NESTED_PAIR_MISSING")

    def test_rejects_nested_file_outside_allowed_scope(self) -> None:
        nested = self.fixture.repo("ao2") / "docs"
        nested.mkdir()
        (nested / "AGENTS.md").write_text("# Unexpected\n", encoding="utf-8")
        (nested / "CLAUDE.md").write_bytes(b"@AGENTS.md\n")
        self.assert_code("UNEXPECTED_INSTRUCTION_SCOPE")

    def test_rejects_oversized_active_root(self) -> None:
        (self.fixture.repo("ao-architecture") / "AGENTS.md").write_text("x" * (12 * 1024 + 1), encoding="utf-8")
        self.assert_code("ROOT_SIZE_LIMIT")

    def test_rejects_oversized_archived_root(self) -> None:
        self.fixture.entry("ao-arena")["lifecycle"] = "archived_hosted"
        self.fixture.write_manifest()
        (self.fixture.repo("ao-arena") / "AGENTS.md").write_text("x" * (8 * 1024 + 1), encoding="utf-8")
        self.assert_code("ROOT_SIZE_LIMIT")

    def test_rejects_root_line_limit(self) -> None:
        (self.fixture.repo("ao-architecture") / "AGENTS.md").write_text("x\n" * 121, encoding="utf-8")
        self.assert_code("ROOT_SIZE_LIMIT")

    def test_rejects_oversized_nested_file(self) -> None:
        nested = self.fixture.allow_nested("ao2", "crates/ao2-runtime")
        (nested / "AGENTS.md").write_text("x" * (8 * 1024 + 1), encoding="utf-8")
        self.assert_code("NESTED_SIZE_LIMIT")

    def test_rejects_nested_line_limit(self) -> None:
        nested = self.fixture.allow_nested("ao2", "crates/ao2-runtime")
        (nested / "AGENTS.md").write_text("x\n" * 81, encoding="utf-8")
        self.assert_code("NESTED_SIZE_LIMIT")

    def test_rejects_oversized_combined_chain(self) -> None:
        first = self.fixture.allow_nested("ao2", "crates")
        second = self.fixture.allow_nested("ao2", "crates/ao2-runtime")
        (self.fixture.repo("ao2") / "AGENTS.md").write_text("r" * 11_000, encoding="utf-8")
        (first / "AGENTS.md").write_text("n" * 7_000, encoding="utf-8")
        (second / "AGENTS.md").write_text("d" * 7_000, encoding="utf-8")
        self.assert_code("CHAIN_SIZE_LIMIT")

    def test_rejects_user_specific_absolute_path(self) -> None:
        (self.fixture.repo("ao-architecture") / "AGENTS.md").write_text(
            "# Instructions\n\nRead /Users/example/private/config.json.\n",
            encoding="utf-8",
        )
        self.assert_code("USER_ABSOLUTE_PATH")

    def test_rejects_obvious_secret_material(self) -> None:
        (self.fixture.repo("ao-architecture") / "AGENTS.md").write_text(
            "# Instructions\n\nAuthorization: Bearer abcdefghijklmnopqrstuvwxyz123456\n",
            encoding="utf-8",
        )
        self.assert_code("SECRET_MATERIAL")

    def test_rejects_github_token_without_embedding_public_scan_literal(self) -> None:
        token = "gh" + "p_" + "a" * 24
        (self.fixture.repo("ao-architecture") / "AGENTS.md").write_text(
            f"# Instructions\n\nLeaked token: {token}\n",
            encoding="utf-8",
        )
        self.assert_code("SECRET_MATERIAL")

    def test_validator_source_avoids_public_scan_token_literals(self) -> None:
        source = (Path(__file__).parent / "verify_agent_instruction_layout.py").read_bytes()
        self.assertNotIn(b"gh" + b"p_", source)
        self.assertNotIn(b"github_" + b"pat_", source)

    def test_rejects_missing_claude_local_ignore(self) -> None:
        (self.fixture.repo("ao-architecture") / ".gitignore").write_text(
            ".claude/settings.local.json\n",
            encoding="utf-8",
        )
        self.assert_code("MISSING_LOCAL_IGNORE")

    def test_rejects_missing_settings_local_ignore(self) -> None:
        (self.fixture.repo("ao-architecture") / ".gitignore").write_text(
            "CLAUDE.local.md\n",
            encoding="utf-8",
        )
        self.assert_code("MISSING_LOCAL_IGNORE")

    def test_rejects_unknown_lifecycle(self) -> None:
        self.fixture.entry("ao-architecture")["lifecycle"] = "maintained"
        self.fixture.write_manifest()
        self.assert_code("MANIFEST_UNKNOWN_LIFECYCLE")

    def test_rejects_legacy_hosted_repository_classified_as_archived(self) -> None:
        entry = self.fixture.entry("ao-operator")
        entry["lifecycle"] = "archived_hosted"
        entry["required_root_files"] = ["AGENTS.md", "CLAUDE.md"]
        entry.pop("exclusion_reason")
        entry.pop("expected_head")
        self.fixture.write_manifest()
        self.assert_code("MANIFEST_LIFECYCLE_CLASSIFICATION")

    def test_rejects_active_repository_classified_as_legacy_hosted(self) -> None:
        entry = self.fixture.entry("ao-arena")
        entry["lifecycle"] = "excluded_legacy_hosted"
        entry["required_root_files"] = []
        entry["exclusion_reason"] = "Incorrect fixture classification."
        entry["expected_head"] = "0" * 40
        self.fixture.write_manifest()
        self.assert_code("MANIFEST_LIFECYCLE_CLASSIFICATION")

    def test_rejects_unknown_manifest_field(self) -> None:
        self.fixture.entry("ao-architecture")["owner"] = "nobody"
        self.fixture.write_manifest()
        self.assert_code("MANIFEST_UNKNOWN_FIELD")

    def test_rejects_duplicate_manifest_key(self) -> None:
        raw = self.fixture.manifest_path.read_text(encoding="utf-8")
        raw = raw.replace('"schema_version": "1.0.0"', '"schema_version": "1.0.0", "schema_version": "1.0.0"', 1)
        self.fixture.manifest_path.write_text(raw, encoding="utf-8")
        with self.assertRaises(ManifestError) as raised:
            load_manifest(self.fixture.manifest_path)
        self.assertEqual(raised.exception.code, "MANIFEST_DUPLICATE_KEY")

    def test_rejects_duplicate_repository(self) -> None:
        self.fixture.manifest["repositories"].append(copy.deepcopy(self.fixture.entry("ao-architecture")))
        self.fixture.write_manifest()
        self.assert_code("MANIFEST_DUPLICATE_REPOSITORY")

    def test_rejects_missing_repository(self) -> None:
        self.fixture.manifest["repositories"] = [
            item for item in self.fixture.manifest["repositories"] if item["name"] != "ao-architecture"
        ]
        self.fixture.write_manifest()
        self.assert_code("MANIFEST_MISSING_REPOSITORY")

    def test_rejects_unexpected_repository(self) -> None:
        self.fixture.manifest["repositories"].append({
            "name": "ao-surprise",
            "lifecycle": "active_hosted",
            "remote": "hosted",
            "required_root_files": ["AGENTS.md", "CLAUDE.md"],
            "allowed_nested_scopes": [],
        })
        self.fixture.write_manifest()
        self.assert_code("MANIFEST_UNEXPECTED_REPOSITORY")

    def test_rejects_malformed_manifest(self) -> None:
        self.fixture.manifest_path.write_text('{"schema_version":', encoding="utf-8")
        with self.assertRaises(ManifestError) as raised:
            load_manifest(self.fixture.manifest_path)
        self.assertEqual(raised.exception.code, "MANIFEST_MALFORMED")

    def test_rejects_trailing_manifest_content(self) -> None:
        self.fixture.manifest_path.write_text(
            json.dumps(self.fixture.manifest) + "\nfalse\n",
            encoding="utf-8",
        )
        with self.assertRaises(ManifestError) as raised:
            load_manifest(self.fixture.manifest_path)
        self.assertEqual(raised.exception.code, "MANIFEST_MALFORMED")

    def test_rejects_manifest_path_traversal(self) -> None:
        self.fixture.entry("ao2")["allowed_nested_scopes"] = ["../outside"]
        self.fixture.write_manifest()
        self.assert_code("MANIFEST_UNSAFE_PATH")

    def test_rejects_absolute_manifest_path(self) -> None:
        self.fixture.entry("ao2")["allowed_nested_scopes"] = ["/tmp/outside"]
        self.fixture.write_manifest()
        self.assert_code("MANIFEST_ABSOLUTE_PATH")

    def test_rejects_modified_excluded_repository(self) -> None:
        (self.fixture.repo("ao-covenant-stub-20260617") / "README.md").write_text(
            "Modified historical fixture.\n",
            encoding="utf-8",
        )
        self.assert_code("EXCLUDED_REPOSITORY_MODIFIED")

    def test_rejects_modified_excluded_legacy_hosted_repository(self) -> None:
        (self.fixture.repo("ao-runtime") / "README.md").write_text(
            "Modified pre-AO-Stack legacy fixture.\n",
            encoding="utf-8",
        )
        self.assert_code("EXCLUDED_REPOSITORY_MODIFIED")

    def test_rejects_excluded_legacy_hosted_head_change(self) -> None:
        repo = self.fixture.repo("ao-runtime")
        (repo / "LATER.md").write_text("Later legacy commit.\n", encoding="utf-8")
        subprocess.run(["git", "add", "LATER.md"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "later"], cwd=repo, check=True)
        self.assert_code("EXCLUDED_REPOSITORY_HEAD_CHANGED")

    def test_rejects_missing_excluded_legacy_hosted_head(self) -> None:
        del self.fixture.entry("ao-runtime")["expected_head"]
        self.fixture.write_manifest()
        self.assert_code("MANIFEST_EXCLUDED_HEAD")

    def test_discovery_ignores_dependencies_caches_generated_and_evidence(self) -> None:
        repo = self.fixture.repo("ao-architecture")
        for scope in (
            ".git/objects",
            "node_modules/package",
            "target/debug",
            ".venv/lib",
            "__pycache__",
            ".pytest_cache",
            "docs/evidence/historical",
            "generated/output",
        ):
            nested = repo / scope
            nested.mkdir(parents=True, exist_ok=True)
            (nested / "AGENTS.md").write_text("# Ignored\n", encoding="utf-8")
        self.assertEqual(self.codes(repository="ao-architecture"), set())

    def test_manifest_loader_returns_valid_document(self) -> None:
        self.assertEqual(load_manifest(self.fixture.manifest_path), self.fixture.manifest)


if __name__ == "__main__":
    unittest.main()
