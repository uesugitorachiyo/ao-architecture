import unittest
from pathlib import Path


WORKFLOW = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "ci.yml"


class WindowsDefaultWorkflowTests(unittest.TestCase):
    def test_candidate_trigger_and_windows_job_contract(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        required = (
            "      - codex/**",
            "  windows-default-environment:",
            "    runs-on: windows-latest",
            "      PYTHONUTF8: \"0\"",
            "git config --global core.autocrlf true",
            "path: source with spaces",
            "git ls-files --eol",
            "windows_preflight.py --profile binary --json",
            "python scripts/verify_architecture.py",
            "python -m unittest scripts.test_verify_windows_default_workflow",
            "git diff --check",
        )
        for marker in required:
            self.assertIn(marker, text, marker)

    def test_windows_job_is_read_only_and_no_provider_surface(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        start = text.index("  windows-default-environment:")
        job = text[start:]
        self.assertNotIn("secrets.", job)
        self.assertNotIn("git push", job)
        self.assertNotIn("gh release", job)
        self.assertIn("contents: read", job)


if __name__ == "__main__":
    unittest.main()
