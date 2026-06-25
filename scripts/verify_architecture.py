#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

ACTIVE_REPOS = [
    "ao-foundry",
    "ao-forge",
    "ao-covenant",
    "ao2",
    "ao2-control-plane",
    "ao-command",
    "ao-arena",
    "ao-crucible",
    "ao-sentinel",
    "ao-promoter",
]

NEW_REPOS = ["ao-arena", "ao-crucible", "ao-sentinel", "ao-promoter"]

REQUIRED_IMAGES = [
    "images/ao-stack-overview.svg",
    "images/authority-boundaries.svg",
    "images/evidence-flow.svg",
    "images/ao-arena-scoreboard.svg",
    "images/ao-crucible-hardening.svg",
    "images/ao-sentinel-regression-monitor.svg",
    "images/ao-promoter-gated-promotion.svg",
]

REQUIRED_RSI_MAP_FILES = [
    "overview/RSI-CLAIM-EVIDENCE-MAP.md",
    "overview/rsi-claim-evidence-manifest.json",
]

REQUIRED_RSI_CLAIMS = [
    "bounded, governed RSI evidence chain",
    "not a claim of full autonomous self-mutating RSI",
    "AO Foundry RSI improvement gate",
    "AO Foundry RSI candidate evidence",
    "AO Foundry RSI next improvement task evidence",
    "Foundry pulse -> Forge retention -> Command health",
    "scripts/rsi-evidence-chain-smoke.sh",
    "Covenant RSI claim boundary",
    "examples/full-rsi-claim-boundary/",
    "evidence-approved.contract.json",
    "AO Covenant PR #55",
    "mutation authority and live self-change are not proven",
    "`claim.publish` side effect",
    "`full-autonomous-self-mutating-rsi` resource",
    "rollback evidence",
    "live self-change evidence",
    "RSI Claim Evidence Map",
    "rsi-claim-evidence-manifest.json",
    "claim_level=bounded_governed_rsi",
    "claim_level=full_autonomous_self_mutating_rsi",
]

REQUIRED_RSI_MAP_TERMS = [
    "claim_level=bounded_governed_rsi",
    "claim_level=full_autonomous_self_mutating_rsi",
    "AO Foundry PR #65",
    "AO Forge PR #142",
    "AO Command PR #28",
    "AO Covenant PR #55",
    "AO Covenant PR #56",
    "mutation authority",
    "rollback evidence",
    "live self-change evidence",
    "not active RSI evidence",
]

REQUIRED_RSI_MANIFEST_TERMS = [
    '"schema_version": "ao.architecture.rsi-claim-evidence-manifest.v0.1"',
    '"claim_level": "bounded_governed_rsi"',
    '"claim_level": "full_autonomous_self_mutating_rsi"',
    '"decision": "allowed"',
    '"decision": "denied"',
    '"ao-foundry"',
    '"ao-forge"',
    '"ao-command"',
    '"ao-covenant"',
    '"number": 28',
    '"number": 56',
    '"Add RSI manifest command"',
    '"Define RSI claim level vocabulary"',
    '"ao2"',
    '"ao2-control-plane"',
    '"ao-operator"',
    '"ao-runtime"',
    '"ao-control-plane"',
]

REQUIRED_COVENANT_CLAIM_BOUNDARY = [
    "RSI Claim Publication Gate",
    "`claim.publish` side effect",
    "`full-autonomous-self-mutating-rsi` resource",
    "examples/full-rsi-claim-boundary/",
    "evidence-approved.contract.json",
    "AO Covenant PR #55",
    "mutation authority, rollback evidence, and live self-change evidence",
]

SAFETY_PATTERNS = [
    r"/Users/",
    r"/home/",
    r"C:\\",
    r"(?<![A-Za-z0-9_.-])/tmp/[A-Za-z0-9_.-]",
    r"/var/folders/",
    r"Authorization: Bearer",
    r"OPENAI_API_KEY",
    r"ANTHROPIC_API_KEY",
    r"GITHUB_TOKEN",
    r"BEGIN PRIVATE KEY",
    r"password=",
    r"token=",
    r"cookie=",
    r"AKIA[0-9A-Z]{16}",
]


def fail(message: str) -> None:
    print(f"verify_architecture.py: {message}", file=sys.stderr)
    sys.exit(1)


def read_text(path: Path) -> str:
    try:
        return path.read_text()
    except FileNotFoundError:
        fail(f"missing required file: {path.relative_to(ROOT)}")


def markdown_image_targets(text: str) -> list[str]:
    return re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)


def assert_contains(path: Path, needle: str) -> None:
    text = read_text(path)
    if needle not in text:
        fail(f"{path.relative_to(ROOT)} missing {needle}")


def main() -> int:
    readme = ROOT / "README.md"
    overview = ROOT / "overview" / "README.md"
    readiness = ROOT / "overview" / "PRODUCTION-READINESS.md"

    for repo in ACTIVE_REPOS:
        assert_contains(readme, f"`{repo}`")
        guide = ROOT / repo / "README.md"
        text = read_text(guide)
        for heading in [
            "## Search-Friendly Summary",
            "## Component At A Glance",
            "## Role In The AO Orchestration Framework",
            "## Architecture",
            "## Workflows",
            "## Contracts And Evidence",
            "## Interactions With Other Repositories",
            "## Production-Readiness Notes",
            "## Quick Verification",
        ]:
            if heading not in text:
                fail(f"{guide.relative_to(ROOT)} missing section {heading}")
        if not markdown_image_targets(text):
            fail(f"{guide.relative_to(ROOT)} has no markdown image")

    overview_text = read_text(overview)
    readiness_text = read_text(readiness)
    root_text = read_text(readme)
    command_text = read_text(ROOT / "ao-command" / "README.md")
    rsi_claim_text = "\n".join([root_text, overview_text, command_text])
    for required_file in REQUIRED_RSI_MAP_FILES:
        if not (ROOT / required_file).exists():
            fail(f"missing required RSI map file: {required_file}")

    for claim in REQUIRED_RSI_CLAIMS:
        if claim not in rsi_claim_text:
            fail(f"architecture docs missing RSI claim guard: {claim}")

    rsi_map_text = read_text(ROOT / "overview" / "RSI-CLAIM-EVIDENCE-MAP.md")
    for term in REQUIRED_RSI_MAP_TERMS:
        if term not in rsi_map_text:
            fail(f"RSI claim evidence map missing required term: {term}")

    rsi_manifest_text = read_text(ROOT / "overview" / "rsi-claim-evidence-manifest.json")
    for term in REQUIRED_RSI_MANIFEST_TERMS:
        if term not in rsi_manifest_text:
            fail(f"RSI claim evidence manifest missing required term: {term}")

    covenant_text = read_text(ROOT / "ao-covenant" / "README.md")
    for claim in REQUIRED_COVENANT_CLAIM_BOUNDARY:
        if claim not in covenant_text:
            fail(f"ao-covenant/README.md missing RSI claim boundary: {claim}")

    for repo in NEW_REPOS:
        if repo not in overview_text:
            fail(f"overview/README.md missing {repo}")
        if repo not in readiness_text:
            fail(f"overview/PRODUCTION-READINESS.md missing {repo}")

    for image in REQUIRED_IMAGES:
        path = ROOT / image
        if not path.exists():
            fail(f"missing required image: {image}")
        try:
            ET.parse(path)
        except ET.ParseError as exc:
            fail(f"invalid SVG XML in {image}: {exc}")

    for md in ROOT.rglob("*.md"):
        text = read_text(md)
        for target in markdown_image_targets(text):
            if target.startswith("http://") or target.startswith("https://"):
                continue
            image_path = (md.parent / target).resolve()
            if not image_path.exists():
                fail(f"{md.relative_to(ROOT)} references missing image {target}")

    scan_suffixes = {".md", ".svg", ".json", ".txt"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix not in scan_suffixes:
            continue
        text = path.read_text(errors="ignore")
        for pattern in SAFETY_PATTERNS:
            if re.search(pattern, text):
                fail(f"public-safety pattern {pattern!r} found in {path.relative_to(ROOT)}")

    print("verify_architecture.py: all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
