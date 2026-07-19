#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOC = ROOT / "docs" / "release-readiness" / "month6-no-release-readiness.md"

REQUIRED_PHRASES = {
    "document must state no release is needed": "does not require a new stable release train",
    "document must mention AO2 v0.5.2": "AO2 v0.5.2",
    "document must mention Control Plane v0.1.17": "AO2 Control Plane v0.1.17",
    "document must state no AO2 release candidate": "No AO2 release candidate is selected",
    "document must state no further Control Plane release is pending": "No additional Control Plane release is pending after the v0.1.17 release",
    "document must state no additional tag release upload deployment or binary publication": "No additional tag, release, upload, deployment, or new binary publication is authorized",
    "document must classify AO2 as no runtime source change": "AO2 has no runtime source change after v0.5.2",
    "document must classify Control Plane as no runtime source change": "AO2 Control Plane has no runtime source change after v0.1.17",
    "document must mention Control Plane compiled dependency refresh": "compiled dependency refresh",
    "document must mention 16 tested compatibility edges": "16 tested edges",
    "document must state compatibility gate is ready, not active": "Compatibility gate is ready, not active",
    "document must mention Month 4 fixture-only dry-run": "fixture-only dry-run",
    "document must mention Month 5 operator workflow": "Month 5 operator workflow",
    "document must state RSI remains denied": "RSI remains denied",
    "document must state live self-modification is denied": "Live self-modification is denied",
    "document must state provider pilot did not run": "Provider pilot did not run",
    "document must state external beta is not launched": "External beta is not launched",
    "document must state promotion is not requested or granted": "Promotion is not requested or granted",
    "document must state credentials are not inspected": "Credentials are not inspected",
    "document must mention release_decision=no_release": "release_decision=no_release",
    "document must recommend next planning cycle": "next six-month-roadmap recommendation",
}

FORBIDDEN_PHRASES = [
    "release candidate selected for publication",
    "external beta is launched",
    "promotion is requested",
    "promotion is granted",
    "RSI is authorized",
    "live self-modification is authorized",
    "provider pilot ran",
]


def validate_month6_no_release_readiness(document: str) -> list[str]:
    errors: list[str] = []
    lower = " ".join(document.lower().split())
    for error, phrase in REQUIRED_PHRASES.items():
        if phrase.lower() not in lower:
            errors.append(error)
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in lower:
            errors.append(f"document must not claim {phrase}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AO Architecture Month 6 no-release readiness source of truth")
    parser.add_argument("--doc", type=Path, default=DEFAULT_DOC)
    args = parser.parse_args()
    try:
        document = args.doc.read_text()
    except OSError as exc:
        print(f"verify_month6_no_release_readiness.py: {exc}", file=sys.stderr)
        return 1
    errors = validate_month6_no_release_readiness(document)
    if errors:
        for error in errors:
            print(f"verify_month6_no_release_readiness.py: {error}", file=sys.stderr)
        return 1
    print("verify_month6_no_release_readiness.py: Month 6 no-release readiness verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
