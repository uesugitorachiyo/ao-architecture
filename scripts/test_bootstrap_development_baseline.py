#!/usr/bin/env python3
"""Offline tests for safe AO development-baseline materialization."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
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


if __name__ == "__main__":
    unittest.main()
