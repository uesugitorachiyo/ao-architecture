#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOC = ROOT / "docs" / "operator-workflow.md"

REQUIRED_GATES = [
    "release gate",
    "compatibility evidence gate",
    "policy approval gate",
    "dry-run/self-improvement gate",
    "observation/readback gate",
    "promotion/no-RSI gate",
]

REQUIRED_STEPS = [
    "read current state",
    "choose safe next work",
    "inspect policy gates",
    "run or read dry-run evidence",
    "inspect rollback and observation",
    "review Sentinel and Promoter boundaries",
    "collect support evidence",
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


def validate_operator_workflow(document: str) -> list[str]:
    errors: list[str] = []
    normalized = " ".join(document.split())
    lower = normalized.lower()

    required_phrases = {
        "document must mention AO2 v0.5.2": "ao2 v0.5.2",
        "document must mention AO2 Control Plane v0.1.17": "ao2 control plane v0.1.17",
        "document must mention 16 tested compatibility edges": "16 tested",
        "document must state compatibility gate is ready, not active": "compatibility gate is ready, not active",
        "document must state RSI remains denied": "rsi remains denied",
        "document must state live self-modification is denied": "live self-modification is denied",
        "document must state provider pilot did not run": "provider pilot did not run",
        "document must state external beta is not launched": "external beta is not launched",
        "document must state promotion is not requested or granted": "promotion is not requested or granted",
        "document must mention Month 4 dry-run evidence": "month 4 dry-run",
    }
    for error, phrase in required_phrases.items():
        if phrase.lower() not in lower:
            errors.append(error)

    for gate in REQUIRED_GATES:
        if gate.lower() not in lower:
            errors.append(f"document must include gate {gate}")

    for step in REQUIRED_STEPS:
        if step.lower() not in lower:
            errors.append(f"document must include operator step {step}")

    for field in SUPPORT_FIELDS:
        if field.lower() not in lower:
            errors.append(f"document must include support evidence field {field}")

    if "do not paste credentials" not in lower:
        errors.append("document must warn operators not to paste credentials")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AO Architecture Month 5 operator workflow source of truth")
    parser.add_argument("--doc", type=Path, default=DEFAULT_DOC)
    args = parser.parse_args()
    try:
        document = args.doc.read_text()
    except OSError as exc:
        print(f"verify_operator_workflow.py: {exc}", file=sys.stderr)
        return 1
    errors = validate_operator_workflow(document)
    if errors:
        for error in errors:
            print(f"verify_operator_workflow.py: {error}", file=sys.stderr)
        return 1
    print("verify_operator_workflow.py: operator workflow source of truth verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
