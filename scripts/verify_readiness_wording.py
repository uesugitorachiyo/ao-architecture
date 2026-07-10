from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOCUMENT = ROOT / "overview" / "PRODUCTION-READINESS.md"
UNQUALIFIED_PRODUCT_CLAIM = re.compile(
    r"\b(?:AO(?:\s+stack|\s+system|\s+platform)?|the\s+system)\s+is\s+production-ready\b|"
    r"\bproduction-ready\s+system\b",
    re.IGNORECASE,
)


def validate_readiness_text(text: str) -> list[str]:
    errors: list[str] = []
    if not text.startswith("# Documentation Production Readiness"):
        errors.append("document must use a documentation-readiness title")
    if not re.search(
        r"does not certify (?:runtime or product|product or runtime) readiness",
        text,
        re.IGNORECASE,
    ):
        errors.append("document must explicitly deny runtime or product readiness certification")
    if UNQUALIFIED_PRODUCT_CLAIM.search(text):
        errors.append("document contains an unqualified product-readiness claim")
    if "## Documentation Checks" not in text:
        errors.append("document must retain a Documentation Checks section")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate that the readiness checklist stays documentation-scoped")
    parser.add_argument("--document", type=Path, default=DEFAULT_DOCUMENT)
    args = parser.parse_args()
    try:
        text = args.document.read_text()
    except OSError as exc:
        print(f"verify_readiness_wording.py: {exc}", file=sys.stderr)
        return 1
    errors = validate_readiness_text(text)
    if errors:
        for error in errors:
            print(f"verify_readiness_wording.py: {error}", file=sys.stderr)
        return 1
    print(f"verify_readiness_wording.py: validated documentation-scoped readiness wording in {args.document}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
