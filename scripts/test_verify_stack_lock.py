import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from verify_stack_lock import validate_lock


class VerifyStackLockTest(unittest.TestCase):
    def test_rejects_duplicate_commits(self):
        lock = {
            "schema": "ao.architecture.stack-lock.v0.1",
            "status": "current",
            "repository_count": 2,
            "repositories": [
                {"repository": "one", "commit": "a" * 40, "detected_version": "unversioned", "proposed_boundary": "ao2", "primary_authority": "one", "branch": "main"},
                {"repository": "two", "commit": "a" * 40, "detected_version": "unversioned", "proposed_boundary": "ao2", "primary_authority": "two", "branch": "main"},
            ],
            "safety": {"promotion_granted": False, "rsi_remains_denied": True, "migration_started": False},
        }
        errors = validate_lock(lock, expected_repositories={"one", "two"})
        self.assertIn("commit aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa is duplicated", errors)

    def test_accepts_current_repository_lockfile(self):
        lock = __import__("json").loads(Path("stack/ao-stack.lock.json").read_text())
        self.assertEqual(validate_lock(lock), [])


if __name__ == "__main__":
    unittest.main()
