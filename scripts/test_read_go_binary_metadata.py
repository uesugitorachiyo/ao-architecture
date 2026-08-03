import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
READER = ROOT / "scripts" / "read_go_binary_metadata.go"


class ReadGoBinaryMetadataTests(unittest.TestCase):
    def build_fixture(self, root: Path) -> Path:
        (root / "go.mod").write_text(
            "module example.com/ao-buildinfo-fixture\n\ngo 1.24\n",
            encoding="utf-8",
        )
        (root / "main.go").write_text(
            'package main\n\nimport "fmt"\n\nfunc main() { fmt.Println("fixture") }\n',
            encoding="utf-8",
        )
        binary = root / "fixture"
        result = subprocess.run(
            ["go", "build", "-trimpath", "-o", str(binary), "."],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return binary

    def run_reader(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["go", "run", str(READER), *arguments],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_reads_exact_binary_metadata_deterministically(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            binary = self.build_fixture(Path(temporary))
            first = self.run_reader(str(binary))
            second = self.run_reader(str(binary))

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(first.stdout, second.stdout)
        metadata = json.loads(first.stdout)
        self.assertEqual(metadata["Path"], "example.com/ao-buildinfo-fixture")
        self.assertEqual(metadata["Main"]["Path"], "example.com/ao-buildinfo-fixture")
        self.assertIn("Deps", metadata)
        self.assertEqual(metadata["Deps"], [])
        self.assertEqual(
            set(metadata["Main"]), {"Path", "Version", "Sum"}
        )

    def test_rejects_missing_binary_argument(self) -> None:
        result = self.run_reader()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("usage: read_go_binary_metadata", result.stderr)

    def test_rejects_non_go_binary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            plain = Path(temporary) / "plain"
            plain.write_text("not a Go binary\n", encoding="utf-8")
            result = self.run_reader(str(plain))

        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("read Go build metadata", result.stderr)


if __name__ == "__main__":
    unittest.main()
