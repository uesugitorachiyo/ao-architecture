import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import verify_architecture


class VerifyArchitectureScanBoundsTest(unittest.TestCase):
    def test_rejects_symlinked_public_safety_candidate(self):
        if sys.platform.startswith("win"):
            self.skipTest("symlink creation is privilege-dependent on Windows")
        with tempfile.TemporaryDirectory() as root_dir, tempfile.TemporaryDirectory() as outside_dir:
            root = Path(root_dir)
            outside = Path(outside_dir) / "outside.md"
            outside.write_text("outside fixture\n")
            (root / "linked.md").symlink_to(outside)

            with self.assertRaisesRegex(ValueError, "symlink"):
                list(verify_architecture.public_safety_scan_paths(root))

    def test_rejects_file_count_limit(self):
        with tempfile.TemporaryDirectory() as root_dir:
            root = Path(root_dir)
            for index in range(3):
                (root / f"safe-{index}.md").write_text("safe\n")

            with self.assertRaisesRegex(ValueError, "file count limit"):
                list(verify_architecture.public_safety_scan_paths(root, max_files=2))

    def test_rejects_file_size_limit(self):
        with tempfile.TemporaryDirectory() as root_dir:
            root = Path(root_dir)
            (root / "oversized.md").write_text("12345\n")

            with self.assertRaisesRegex(ValueError, "file size limit"):
                list(verify_architecture.public_safety_scan_paths(root, max_file_bytes=4))

    def test_rejects_total_byte_limit(self):
        with tempfile.TemporaryDirectory() as root_dir:
            root = Path(root_dir)
            (root / "first.md").write_text("12345")
            (root / "second.md").write_text("67890")

            with self.assertRaisesRegex(ValueError, "total byte limit"):
                list(
                    verify_architecture.public_safety_scan_paths(
                        root,
                        max_file_bytes=10,
                        max_total_bytes=8,
                    )
                )


if __name__ == "__main__":
    unittest.main()
