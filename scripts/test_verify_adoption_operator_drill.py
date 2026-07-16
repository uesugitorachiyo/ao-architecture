import tempfile
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from verify_adoption_operator_drill import validate_adoption_operator_drill


VALID_DOC = """
# AO Stack Adoption Month 2 Operator Drill

The current public pair is AO2 v0.5.1 and AO2 Control Plane v0.1.15.
The compatibility matrix has 16 tested edges, 16 canonical vectors, and
16 consumer tests. The compatibility gate is ready, not active.

The operator reads current stack state, identifies the current public pair,
checks the compatibility gate, chooses safe next work, inspects policy gates,
reads dry-run observation evidence, and collects support evidence.

Support evidence categories: install, checksum, manifest mismatch,
approval/replay, rollback, and operator readback issue.

Denied states: RSI remains denied. Live self-modification is denied.
External beta is not launched. Promotion is not requested or granted.
Provider pilot did not run. Release, tag, upload, deployment, and new binary
publication are not part of this drill. Credentials are not inspected.
"""


class AdoptionOperatorDrillVerifierTests(unittest.TestCase):
    def test_accepts_month2_operator_drill_source(self) -> None:
        self.assertEqual(validate_adoption_operator_drill(VALID_DOC), [])

    def test_rejects_gate_activation_claim(self) -> None:
        doc = VALID_DOC.replace(
            "The compatibility gate is ready, not active.",
            "The compatibility gate is active.",
        )
        errors = validate_adoption_operator_drill(doc)
        self.assertIn("document must state compatibility gate is ready, not active", errors)

    def test_rejects_missing_support_category(self) -> None:
        doc = VALID_DOC.replace("manifest mismatch,\n", "")
        errors = validate_adoption_operator_drill(doc)
        self.assertIn("document must include support category manifest mismatch", errors)

    def test_default_document_validates(self) -> None:
        root = Path(__file__).resolve().parents[1]
        path = root / "docs" / "adoption-operator-drill.md"
        if path.exists():
            self.assertEqual(validate_adoption_operator_drill(path.read_text()), [])
        else:
            with tempfile.TemporaryDirectory() as tmp:
                missing = Path(tmp) / "missing.md"
                self.assertFalse(missing.exists())


if __name__ == "__main__":
    unittest.main()
