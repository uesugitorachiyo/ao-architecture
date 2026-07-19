#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOC = ROOT / "docs" / "adoption-operator-drill.md"

SUPPORT_CATEGORIES = [
    "install",
    "checksum",
    "manifest mismatch",
    "approval/replay",
    "rollback",
    "operator readback issue",
]

OPERATOR_STEPS = [
    "reads current stack state",
    "identifies the current public pair",
    "checks the compatibility gate",
    "chooses safe next work",
    "inspects policy gates",
    "reads dry-run observation evidence",
    "collects support evidence",
]


def validate_adoption_operator_drill(document: str) -> list[str]:
    errors: list[str] = []
    normalized = " ".join(document.split())
    lower = normalized.lower()

    required_phrases = {
        "document must mention AO2 v0.5.2": "ao2 v0.5.2",
        "document must mention AO2 Control Plane v0.1.17": "ao2 control plane v0.1.17",
        "document must mention 16 tested edges": "16 tested",
        "document must mention 16 canonical vectors": "16 canonical vectors",
        "document must mention 16 consumer tests": "16 consumer tests",
        "document must state compatibility gate is ready, not active": "compatibility gate is ready, not active",
        "document must state RSI remains denied": "rsi remains denied",
        "document must state live self-modification is denied": "live self-modification is denied",
        "document must state external beta is not launched": "external beta is not launched",
        "document must state promotion is not requested or granted": "promotion is not requested or granted",
        "document must state provider pilot did not run": "provider pilot did not run",
        "document must state release is not part of this drill": "release, tag, upload, deployment",
        "document must state credentials are not inspected": "credentials are not inspected",
    }
    for error, phrase in required_phrases.items():
        if phrase.lower() not in lower:
            errors.append(error)

    forbidden_phrases = {
        "document must not claim compatibility gate active": "compatibility gate is active",
        "document must not claim external beta launched": "external beta launched",
        "document must not claim promotion granted": "promotion granted",
        "document must not claim RSI authorized": "rsi authorized",
    }
    for error, phrase in forbidden_phrases.items():
        if phrase.lower() in lower:
            errors.append(error)

    for step in OPERATOR_STEPS:
        if step not in lower:
            errors.append(f"document must include operator step {step}")

    for category in SUPPORT_CATEGORIES:
        if category not in lower:
            errors.append(f"document must include support category {category}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AO Stack Adoption Month 2 operator drill source-of-truth")
    parser.add_argument("--doc", type=Path, default=DEFAULT_DOC)
    args = parser.parse_args()
    try:
        document = args.doc.read_text()
    except OSError as exc:
        print(f"verify_adoption_operator_drill.py: {exc}", file=sys.stderr)
        return 1
    errors = validate_adoption_operator_drill(document)
    if errors:
        for error in errors:
            print(f"verify_adoption_operator_drill.py: {error}", file=sys.stderr)
        return 1
    print("verify_adoption_operator_drill.py: adoption operator drill source verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
