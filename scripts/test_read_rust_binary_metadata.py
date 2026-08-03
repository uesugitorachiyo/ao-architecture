from __future__ import annotations

import json
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.rust_binary_provenance import PREFIX, RustProvenanceError, read_rust_binary_metadata


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "read_rust_binary_metadata.py"


def marker(**overrides: object) -> bytes:
    value: dict[str, object] = {
        "build_profile": "release",
        "cargo_lock_sha256": hashlib.sha256(b"lock").hexdigest(),
        "repository": "ao2",
        "source_sha": "a" * 40,
        "source_modified": False,
        "target": "linux-x86_64",
        "version": "0.5.6",
    }
    value.update(overrides)
    return PREFIX + json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii") + b"\x00"


class RustBinaryMetadataTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.binary = Path(self.temp.name) / "ao2"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write(self, value: bytes) -> None:
        self.binary.write_bytes(b"header\x00" + value + b"\x00trailer")

    def test_reads_one_canonical_embedded_marker(self) -> None:
        self.write(marker())
        metadata = read_rust_binary_metadata(self.binary)
        self.assertEqual(metadata["repository"], "ao2")
        self.assertEqual(metadata["source_sha"], "a" * 40)
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(self.binary)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), metadata)

    def test_rejects_missing_duplicate_and_malformed_markers(self) -> None:
        for value, message in (
            (b"ordinary binary", "exactly one"),
            (marker() + marker(), "exactly one"),
            (PREFIX + b"{bad}\x00", "malformed"),
        ):
            with self.subTest(message=message):
                self.write(value)
                with self.assertRaisesRegex(RustProvenanceError, message):
                    read_rust_binary_metadata(self.binary)

    def test_rejects_wrong_fields_profile_sha_and_non_ascii(self) -> None:
        cases = [
            (marker(extra="unsafe"), "fields"),
            (marker(build_profile="debug"), "profile"),
            (marker(source_sha="not-a-sha"), "source SHA"),
            (marker(cargo_lock_sha256="not-a-digest"), "Cargo.lock SHA-256"),
            (marker(source_modified=True), "clean source"),
            (marker(version="\u2603"), "bounded ASCII"),
        ]
        for value, message in cases:
            with self.subTest(message=message):
                self.write(value)
                with self.assertRaisesRegex(RustProvenanceError, message):
                    read_rust_binary_metadata(self.binary)

    def test_rejects_duplicate_json_keys(self) -> None:
        value = (
            PREFIX
            + b'{"build_profile":"release","repository":"ao2","repository":"other",'
            + b'"cargo_lock_sha256":"'
            + b"b" * 64
            + b'","source_modified":false,'
            + b'"source_sha":"'
            + b"a" * 40
            + b'","target":"linux-x86_64","version":"0.5.6"}\x00'
        )
        self.write(value)
        with self.assertRaisesRegex(RustProvenanceError, "duplicate JSON key"):
            read_rust_binary_metadata(self.binary)


if __name__ == "__main__":
    unittest.main()
