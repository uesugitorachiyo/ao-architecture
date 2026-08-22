#!/usr/bin/env python3
"""Offline tests for safe AO development-baseline materialization."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "bootstrap_development_baseline.py"
SPEC = importlib.util.spec_from_file_location("bootstrap_development_baseline", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load bootstrap_development_baseline")
bootstrap = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bootstrap)


class JSONInputTests(unittest.TestCase):
    def test_loads_bounded_duplicate_safe_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            path.write_text('{"schema":"example.v1"}', encoding="utf-8")
            self.assertEqual(
                bootstrap.load_json_file(path, 1024),
                {"schema": "example.v1"},
            )

    def test_rejects_duplicate_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            path.write_text('{"schema":"one","schema":"two"}', encoding="utf-8")
            with self.assertRaisesRegex(bootstrap.BootstrapError, "duplicate key: schema"):
                bootstrap.load_json_file(path, 1024)

    def test_rejects_non_utf8_and_oversized_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            invalid = root / "invalid.json"
            invalid.write_bytes(b'{"value":"\xff"}')
            with self.assertRaisesRegex(bootstrap.BootstrapError, "input is not UTF-8"):
                bootstrap.load_json_file(invalid, 1024)
            oversized = root / "oversized.json"
            oversized.write_bytes(b" " * 17)
            with self.assertRaisesRegex(bootstrap.BootstrapError, "input exceeds 16 bytes"):
                bootstrap.load_json_file(oversized, 16)

    def test_rejects_symlink_input_when_supported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.json"
            target.write_text("{}", encoding="utf-8")
            link = root / "link.json"
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation is unavailable")
            with self.assertRaisesRegex(bootstrap.BootstrapError, "regular non-link file"):
                bootstrap.load_json_file(link, 1024)


class RootSafetyTests(unittest.TestCase):
    def test_materialize_accepts_absent_or_empty_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            absent = parent / "AO Baseline With Spaces"
            self.assertEqual(
                bootstrap.validate_materialization_root(absent, "materialize"),
                absent.resolve(strict=False),
            )
            empty = parent / "empty"
            empty.mkdir()
            self.assertEqual(
                bootstrap.validate_materialization_root(empty, "materialize"),
                empty.resolve(strict=True),
            )

    def test_materialize_rejects_nonempty_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "root"
            root.mkdir()
            (root / "existing.txt").write_text("do not overwrite", encoding="utf-8")
            with self.assertRaisesRegex(bootstrap.BootstrapError, "materialize root must be empty"):
                bootstrap.validate_materialization_root(root, "materialize")

    def test_verify_existing_requires_regular_existing_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            missing = parent / "missing"
            with self.assertRaisesRegex(bootstrap.BootstrapError, "verify-existing root must exist"):
                bootstrap.validate_materialization_root(missing, "verify-existing")
            root = parent / "root"
            root.mkdir()
            self.assertEqual(
                bootstrap.validate_materialization_root(root, "verify-existing"),
                root.resolve(strict=True),
            )

    def test_rejects_unknown_mode(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(bootstrap.BootstrapError, "mode must be materialize or verify-existing"):
                bootstrap.validate_materialization_root(Path(directory), "repair")

    def test_rejects_symlink_root_and_ancestor_when_supported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            real = parent / "real"
            real.mkdir()
            link = parent / "link"
            try:
                link.symlink_to(real, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation is unavailable")
            with self.assertRaisesRegex(bootstrap.BootstrapError, "link or reparse"):
                bootstrap.validate_materialization_root(link, "verify-existing")
            with self.assertRaisesRegex(bootstrap.BootstrapError, "link or reparse"):
                bootstrap.validate_materialization_root(link / "child", "materialize")

    def test_contained_child_accepts_safe_name_and_rejects_unsafe_names(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.assertEqual(
                bootstrap.contained_child(root, "ao-mission"),
                root / "ao-mission",
            )
            for name in ("", ".", "..", "../escape", "nested/repo", "nested\\repo", "/absolute", "C:\\absolute"):
                with self.subTest(name=name):
                    with self.assertRaises(bootstrap.BootstrapError):
                        bootstrap.contained_child(root, name)

    def test_detects_casefold_collisions(self) -> None:
        with self.assertRaisesRegex(bootstrap.BootstrapError, "case-fold collision"):
            bootstrap.require_unique_casefold(["ao-mission", "AO-MISSION"])

    def test_regular_path_is_not_link_or_reparse(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "regular"
            path.write_text("regular", encoding="utf-8")
            self.assertFalse(bootstrap.is_link_or_reparse(path))


class RepositoryMaterializationTests(unittest.TestCase):
    def make_upstream(self, parent: Path, name: str = "ao-fixture"):
        work = parent / f"{name}-source"
        bare = parent / f"{name}-upstream.git"
        work.mkdir()
        self.git("init", "--initial-branch=main", cwd=work)
        self.git("config", "user.name", "AO Fixture", cwd=work)
        self.git("config", "user.email", "fixture@example.invalid", cwd=work)
        (work / "README.md").write_text("fixture\n", encoding="utf-8", newline="\n")
        self.git("add", "README.md", cwd=work)
        env = os.environ.copy()
        env.update(
            GIT_AUTHOR_DATE="2026-08-22T00:00:00Z",
            GIT_COMMITTER_DATE="2026-08-22T00:00:00Z",
        )
        self.git("commit", "-m", "fixture", cwd=work, env=env)
        commit = self.git("rev-parse", "HEAD", cwd=work).stdout.strip()
        self.git("clone", "--bare", str(work), str(bare), cwd=parent)
        return bootstrap.RepositorySpec(
            name=name,
            path=name,
            upstream_url=str(bare.resolve()),
            commit=commit,
        )

    def git(self, *args: str, cwd: Path, env=None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )

    def materialize_one(self, parent: Path):
        spec = self.make_upstream(parent)
        root = parent / "AO Baseline With Spaces"
        runner = bootstrap.CommandRunner()
        records = bootstrap.materialize_repositories(root, [spec], runner)
        (root / ".ao-baseline").mkdir()
        return spec, root, runner, records

    def test_materializes_and_verifies_exact_detached_clean_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            spec, root, runner, records = self.materialize_one(parent)
            checkout = root / spec.path
            self.assertEqual(self.git("rev-parse", "HEAD", cwd=checkout).stdout.strip(), spec.commit)
            attached = subprocess.run(
                ["git", "symbolic-ref", "-q", "HEAD"], cwd=checkout, capture_output=True
            )
            self.assertNotEqual(attached.returncode, 0)
            self.assertEqual(records[0]["repository"], spec.name)
            verified = bootstrap.verify_repositories(root, [spec], runner)
            self.assertTrue(verified[0]["detached"])
            self.assertTrue(verified[0]["clean"])
            self.assertTrue(any(record.environment["GIT_TERMINAL_PROMPT"] == "0" for record in runner.records))
            self.assertTrue(any(record.environment["GCM_INTERACTIVE"] == "Never" for record in runner.records))

    def test_verify_existing_rejects_dirty_attached_and_upstream_drift(self) -> None:
        cases = {
            "dirty": lambda root, spec: (root / spec.path / "untracked.txt").write_text("dirty", encoding="utf-8"),
            "attached": lambda root, spec: self.git("switch", "-c", "local", cwd=root / spec.path),
            "upstream": lambda root, spec: self.git("remote", "set-url", "origin", str(root), cwd=root / spec.path),
        }
        expected = {
            "dirty": "repository is dirty",
            "attached": "repository is not detached",
            "upstream": "origin mismatch",
        }
        for name, mutate in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                spec, root, runner, _ = self.materialize_one(Path(directory))
                mutate(root, spec)
                with self.assertRaisesRegex(bootstrap.BootstrapError, expected[name]):
                    bootstrap.verify_repositories(root, [spec], runner)

    def test_verify_existing_rejects_missing_and_extra_siblings(self) -> None:
        for name in ("missing", "extra"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                spec, root, runner, _ = self.materialize_one(Path(directory))
                if name == "missing":
                    os.rename(root / spec.path, root / "moved")
                    expected = "workspace sibling set mismatch"
                else:
                    (root / "unexpected").mkdir()
                    expected = "workspace sibling set mismatch"
                with self.assertRaisesRegex(bootstrap.BootstrapError, expected):
                    bootstrap.verify_repositories(root, [spec], runner)

    def test_verify_existing_changes_no_tracked_or_untracked_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            spec, root, runner, _ = self.materialize_one(Path(directory))
            before = self.snapshot(root)
            bootstrap.verify_repositories(root, [spec], runner)
            self.assertEqual(self.snapshot(root), before)

    def snapshot(self, root: Path) -> dict[str, bytes]:
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in root.rglob("*")
            if path.is_file()
        }

    def test_rejects_unsafe_submodule_status(self) -> None:
        for prefix in ("-", "+", "U"):
            with self.subTest(prefix=prefix):
                with self.assertRaisesRegex(bootstrap.BootstrapError, "unsafe submodule status"):
                    bootstrap.validate_submodule_status([prefix + "0" * 40 + " dependency"])
        bootstrap.validate_submodule_status([" " + "0" * 40 + " dependency"])


if __name__ == "__main__":
    unittest.main()
