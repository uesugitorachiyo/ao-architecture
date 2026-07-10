import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from verify_readiness_wording import validate_readiness_text


class VerifyReadinessWordingTest(unittest.TestCase):
    def test_accepts_documentation_scoped_checklist(self):
        text = """# Documentation Production Readiness

This checklist describes documentation quality. It does not certify runtime or product readiness.

## Documentation Checks
"""
        self.assertEqual(validate_readiness_text(text), [])

    def test_rejects_unqualified_product_readiness_claim(self):
        text = """# Production Readiness

The AO stack is production-ready.
"""
        errors = validate_readiness_text(text)
        self.assertIn("document must use a documentation-readiness title", errors)
        self.assertIn("document must explicitly deny runtime or product readiness certification", errors)
        self.assertIn("document contains an unqualified product-readiness claim", errors)


if __name__ == "__main__":
    unittest.main()
