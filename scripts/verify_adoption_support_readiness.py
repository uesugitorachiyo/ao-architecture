#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOC = ROOT / "docs" / "adoption-support-readiness.md"

SUPPORT_STATES = ["fresh", "stale", "blocked", "denied", "unsupported"]

SUPPORT_CATEGORIES = [
    "install",
    "checksum",
    "manifest mismatch",
    "approval/replay",
    "rollback",
    "Windows-safe rollback",
    "operator readback issue",
    "issue-report fields",
]

SUPPORT_FIELDS = [
    "AO2 version",
    "platform",
    "exact command",
    "expected result",
    "actual result",
    "evidence path",
    "approval status",
    "manifest or checksum state",
    "rollback status",
    "observation status",
    "sanitized logs",
]


def validate_adoption_support_readiness(document: str) -> list[str]:
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
        "document must state no release is selected": "release, tag, upload, deployment",
        "document must state credentials are not inspected": "credentials are not inspected",
        "document must warn against credential pasting": "must not paste credentials",
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

    for state in SUPPORT_STATES:
        if state.lower() not in lower:
            errors.append(f"document must include support state {state}")

    for category in SUPPORT_CATEGORIES:
        if category.lower() not in lower:
            errors.append(f"document must include support category {category}")

    for field in SUPPORT_FIELDS:
        if field.lower() not in lower:
            errors.append(f"document must include support field {field}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AO Stack Adoption Month 5 support readiness source of truth")
    parser.add_argument("--doc", type=Path, default=DEFAULT_DOC)
    args = parser.parse_args()
    try:
        document = args.doc.read_text()
    except OSError as exc:
        print(f"verify_adoption_support_readiness.py: {exc}", file=sys.stderr)
        return 1
    errors = validate_adoption_support_readiness(document)
    if errors:
        for error in errors:
            print(f"verify_adoption_support_readiness.py: {error}", file=sys.stderr)
        return 1
    print("verify_adoption_support_readiness.py: adoption support readiness source verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
