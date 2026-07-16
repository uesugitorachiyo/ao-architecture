import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from verify_adoption_support_readiness import validate_adoption_support_readiness


VALID_DOC = """
# AO Stack Adoption Month 5 Support Readiness

Current public pair: AO2 v0.5.1 and AO2 Control Plane v0.1.16.
The compatibility matrix remains 16 tested edges, 16 canonical vectors, and
16 consumer tests. The compatibility gate is ready, not active.

Support readiness states: fresh, stale, blocked, denied, unsupported.

Support package categories: install, checksum, manifest mismatch,
approval/replay, rollback, Windows-safe rollback, operator readback issue,
and issue-report fields.

The operator collects AO2 version, platform, exact command, expected result,
actual result, evidence path, approval status, manifest or checksum state,
rollback status, observation status, and sanitized logs. Operators must not
paste credentials, tokens, provider secrets, private repository contents, or
raw private logs.

RSI remains denied. Live self-modification is denied. External beta is not
launched. Promotion is not requested or granted. Provider pilot did not run.
Release, tag, upload, deployment, and new binary publication are not part of
this support readiness drill. Credentials are not inspected.
"""


class AdoptionSupportReadinessVerifierTests(unittest.TestCase):
    def test_accepts_month5_support_readiness_source(self) -> None:
        self.assertEqual(validate_adoption_support_readiness(VALID_DOC), [])

    def test_rejects_missing_windows_safe_rollback(self) -> None:
        errors = validate_adoption_support_readiness(VALID_DOC.replace("Windows-safe rollback, ", ""))
        self.assertIn("document must include support category Windows-safe rollback", errors)

    def test_rejects_missing_support_state(self) -> None:
        errors = validate_adoption_support_readiness(VALID_DOC.replace("unsupported", ""))
        self.assertIn("document must include support state unsupported", errors)

    def test_default_document_validates(self) -> None:
        root = Path(__file__).resolve().parents[1]
        doc = root / "docs" / "adoption-support-readiness.md"
        self.assertEqual(validate_adoption_support_readiness(doc.read_text()), [])


if __name__ == "__main__":
    unittest.main()
