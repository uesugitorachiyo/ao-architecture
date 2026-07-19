#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOC = ROOT / "docs" / "release-readiness" / "adoption-month6-no-release-readiness.md"


def validate_adoption_month6_no_release_readiness(document: str) -> list[str]:
    errors: list[str] = []
    normalized = " ".join(document.split())
    lower = normalized.lower()

    required = {
        "document must record release_decision=no_release": "release_decision=no_release",
        "document must mention AO2 v0.5.2": "ao2 v0.5.2",
        "document must mention AO2 Control Plane v0.1.17": "ao2 control plane v0.1.17",
        "document must classify AO2 changes as docs/tests/fixtures": "ao2 changes since v0.5.2 are docs, tests, and fixtures only",
        "document must classify Control Plane changes as non-binary support work": "control plane changes since v0.1.17 are workflows, scripts, docs, tests, and fixtures only",
        "document must state no AO2 public artifact replacement is required": "no ao2 shipped binary behavior requires public artifact replacement",
        "document must mention 16 tested edges": "16 tested edges",
        "document must mention 16 canonical vectors": "16 canonical vectors",
        "document must mention 16 consumer tests": "16 consumer tests",
        "document must state compatibility gate is ready, not active": "compatibility gate is ready, not active",
        "document must mention Month 4 fixture-only dry-run": "month 4 controlled improvement remains fixture-only dry-run",
        "document must mention Month 5 support readiness package": "month 5 support readiness package is current",
        "document must state RSI remains denied": "rsi remains denied",
        "document must state external beta is not launched": "external beta is not launched",
        "document must state promotion is not requested or granted": "promotion is not requested or granted",
        "document must state provider pilot did not run": "provider pilot did not run",
        "document must state no additional release/tag/upload/deployment is selected": "no additional release, tag, upload",
    }
    for error, phrase in required.items():
        if phrase not in lower:
            errors.append(error)

    forbidden = {
        "document must not select a release": "release_decision=release",
        "document must not claim gate active": "compatibility gate is active",
        "document must not claim external beta launched": "external beta launched",
        "document must not claim promotion granted": "promotion granted",
        "document must not claim RSI authorized": "rsi authorized",
    }
    for error, phrase in forbidden.items():
        if phrase in lower:
            errors.append(error)

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AO Stack Adoption Month 6 no-release readiness")
    parser.add_argument("--doc", type=Path, default=DEFAULT_DOC)
    args = parser.parse_args()
    try:
        document = args.doc.read_text()
    except OSError as exc:
        print(f"verify_adoption_month6_no_release_readiness.py: {exc}", file=sys.stderr)
        return 1
    errors = validate_adoption_month6_no_release_readiness(document)
    if errors:
        for error in errors:
            print(f"verify_adoption_month6_no_release_readiness.py: {error}", file=sys.stderr)
        return 1
    print("verify_adoption_month6_no_release_readiness.py: adoption Month 6 no-release readiness verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
