import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from verify_month6_no_release_readiness import validate_month6_no_release_readiness


class VerifyMonth6NoReleaseReadinessTest(unittest.TestCase):
    def test_accepts_recorded_month6_readiness_doc(self):
        doc = (
            Path(__file__).resolve().parents[1]
            / "docs"
            / "release-readiness"
            / "month6-no-release-readiness.md"
        ).read_text()
        self.assertEqual(validate_month6_no_release_readiness(doc), [])

    def test_rejects_missing_no_release_decision_and_pair(self):
        doc = "# Month 6\n\nCompatibility evidence exists.\n"
        errors = validate_month6_no_release_readiness(doc)
        self.assertIn("document must state no release is needed", errors)
        self.assertIn("document must mention AO2 v0.5.1", errors)
        self.assertIn("document must mention Control Plane v0.1.15", errors)
        self.assertIn("document must state compatibility gate is ready, not active", errors)

    def test_rejects_overclaims(self):
        doc = "\n".join(
            [
                "Month 6 does not require a new stable release train.",
                "AO2 v0.5.1",
                "AO2 Control Plane v0.1.15",
                "No AO2 release candidate is selected.",
                "No AO2 Control Plane release candidate is selected.",
                "No tag, release, upload, deployment, or new binary publication is authorized.",
                "AO2 has no runtime source change after v0.5.1.",
                "AO2 Control Plane has no runtime source change after v0.1.15.",
                "lockfile hygiene",
                "16 tested edges",
                "Compatibility gate is ready, not active",
                "fixture-only dry-run",
                "Month 5 operator workflow",
                "RSI remains denied",
                "Live self-modification is denied",
                "Provider pilot did not run",
                "External beta is not launched",
                "Promotion is not requested or granted",
                "Credentials are not inspected",
                "release_decision=no_release",
                "next six-month-roadmap recommendation",
                "RSI is authorized",
            ]
        )
        errors = validate_month6_no_release_readiness(doc)
        self.assertIn("document must not claim RSI is authorized", errors)

    def test_rejects_stale_false_gate_language(self):
        doc = "\n".join(
            [
                "Month 6 does not require a new stable release train.",
                "AO2 v0.5.1",
                "AO2 Control Plane v0.1.15",
                "No AO2 release candidate is selected.",
                "No AO2 Control Plane release candidate is selected.",
                "No tag, release, upload, deployment, or new binary publication is authorized.",
                "AO2 has no runtime source change after v0.5.1.",
                "AO2 Control Plane has no runtime source change after v0.1.15.",
                "lockfile hygiene",
                "16 tested edges",
                "Compatibility gate remains false",
                "fixture-only dry-run",
                "Month 5 operator workflow",
                "RSI remains denied",
                "Live self-modification is denied",
                "Provider pilot did not run",
                "External beta is not launched",
                "Promotion is not requested or granted",
                "Credentials are not inspected",
                "release_decision=no_release",
                "next six-month-roadmap recommendation",
            ]
        )
        errors = validate_month6_no_release_readiness(doc)
        self.assertIn("document must state compatibility gate is ready, not active", errors)


if __name__ == "__main__":
    unittest.main()
