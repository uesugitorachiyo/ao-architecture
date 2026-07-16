import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from verify_adoption_month6_no_release_readiness import validate_adoption_month6_no_release_readiness


VALID_DOC = """
# AO Stack Adoption Month 6 No-Release Readiness

release_decision=no_release.
AO2 v0.5.1 and AO2 Control Plane v0.1.15 remain the current public pair.
AO2 changes since v0.5.1 are docs, tests, and fixtures only.
Control Plane changes since v0.1.15 are workflows, scripts, docs, tests, and
fixtures only. No shipped binary behavior requires public artifact replacement.

The compatibility matrix remains 16 tested edges, 16 canonical vectors, and
16 consumer tests. The compatibility gate is ready, not active.

Month 4 controlled improvement remains fixture-only dry-run. Month 5 support
readiness package is current. RSI remains denied. External beta is not
launched. Promotion is not requested or granted. Provider pilot did not run.
No release, tag, upload, deployment, or new binary publication is selected.
"""


class AdoptionMonth6NoReleaseReadinessTests(unittest.TestCase):
    def test_accepts_adoption_month6_no_release_doc(self) -> None:
        self.assertEqual(validate_adoption_month6_no_release_readiness(VALID_DOC), [])

    def test_rejects_release_selection(self) -> None:
        doc = VALID_DOC.replace("release_decision=no_release", "release_decision=release")
        self.assertIn(
            "document must record release_decision=no_release",
            validate_adoption_month6_no_release_readiness(doc),
        )

    def test_rejects_missing_support_package(self) -> None:
        doc = VALID_DOC.replace("Month 5 support\nreadiness package is current.", "")
        self.assertIn(
            "document must mention Month 5 support readiness package",
            validate_adoption_month6_no_release_readiness(doc),
        )

    def test_default_document_validates(self) -> None:
        root = Path(__file__).resolve().parents[1]
        doc = root / "docs" / "release-readiness" / "adoption-month6-no-release-readiness.md"
        self.assertEqual(validate_adoption_month6_no_release_readiness(doc.read_text()), [])


if __name__ == "__main__":
    unittest.main()
