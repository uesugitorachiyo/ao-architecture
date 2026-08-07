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
    "governed pool lifecycle gate",
    "controlled external-beta gate",
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
        "document must mention AO2 v0.5.9": "ao2 v0.5.9",
        "document must mention AO2 Control Plane v0.1.19": "ao2 control plane v0.1.19",
        "document must mention 16 tested compatibility edges": "16 tested",
        "document must state compatibility gate is blocked, not active": "compatibility gate is blocked, not active",
        "document must state 15 compatibility edges are fresh": "fifteen edges are fresh",
        "document must state the v0.5.8 vector is stale for v0.5.9": "v0.5.8 execution-to-observation vector is stale for ao2 v0.5.9",
        "document must state RSI remains denied": "rsi remains denied",
        "document must state live self-modification is denied": "live self-modification is denied",
        "document must state provider pilot did not run": "provider pilot did not run",
        "document must deny a standing unrestricted external beta": "no standing or unrestricted external-beta program is launched",
        "document must state promotion is not requested or granted": "promotion is not requested or granted",
        "document must mention Month 4 dry-run evidence": "month 4 dry-run",
        "document must identify the canonical V3 pool root": r"%userprofile%\ai agent teams\ao2-public-instances-v3",
        "document must identify the public physical Windows worker role": "physical_windows_v3",
        "document must require all five pool instances to be free": "require all five instances to be free",
        "document must retain upstream as unchanged": "third-party upstream repository unchanged",
        "document must bind restart to Mission and correlation identities": "same mission and correlation identities",
        "document must identify the completed campaign evidence": "ao-mission-governed-pool-external-beta-20260807t011024z",
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
    parser = argparse.ArgumentParser(description="Validate the AO Architecture operator workflow source of truth")
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
