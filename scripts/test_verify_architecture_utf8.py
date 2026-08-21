import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class VerifyArchitectureUTF8Tests(unittest.TestCase):
    def test_verifier_starts_with_pythonutf8_zero(self):
        env = {**os.environ, "PYTHONUTF8": "0"}
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "verify_architecture.py")],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )
        self.assertNotIn("UnicodeDecodeError", result.stderr)
        self.assertNotIn("charmap", result.stderr)


if __name__ == "__main__":
    unittest.main()
