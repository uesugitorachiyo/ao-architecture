#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

ACTIVE_REPOS = [
    "ao-blueprint",
    "ao-atlas",
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

REQUIRED_LIVE_MUTATION_LADDER_FILES = [
    "overview/MUTATION-AUTHORITY-LADDER.md",
]

REQUIRED_LIVE_MUTATION_LADDER_TERMS = [
    "Mutation Authority Ladder",
    "docs_only_single_file",
    "docs_only_multi_file",
    "docs_config_only",
    "test_only",
    "low_risk_code",
    "multi_repo_low_risk",
    "complex_repo_mutation",
    "fully_unsupervised_complex_mutation",
    "highest proven live class is\n`public_safe_broad_RSI_governed_campaign_segment_07_evidence`",
    "governed 12-node complex",
    "26-node fully unsupervised complex",
    "bounded_rsi_evidence_rehearsal",
    "live-proven as a bounded evidence rehearsal",
    "bounded_rsi_self_improvement_application",
    "proven only for the exact",
    "private readback/eval rubric rehearsal",
    "exact_safe_public_claim_wording_conservative_readback_evidence",
    "public_safe_bounded_improvement_evidence_expansion_four_attempts",
    "four public-safe bounded evidence expansion attempts",
    "public_safe_reviewed_causal_chain_boundary_generalization_evidence",
    "reviewed causal-chain boundary generalization evidence",
    "public_safe_intermediate_causal_review_claim_evidence",
    "intermediate causal-review evidence",
    "public_safe_causal_review_evidence_selection_guidance",
    "evidence-selection and blocker-prioritization guidance",
    "public_safe_guided_evidence_application_four_attempts",
    "public_safe_reviewer_approved_bounded_recursive_improvement_wording_evidence",
    "docs/evidence/recursive-improvement-bounded-wording-generality/",
    "166398641b655f0da97817659acc771026b204e7",
    "AO Foundry PR #197",
    "bounded recursive-improvement wording generality evidence",
    "public_safe_bounded_recursive_improvement_wording_generality_evidence",
    "public_safe_bounded_recursive_improvement_review_durability_evidence",
    "recursive-improvement review durability evidence",
    "docs/evidence/recursive-improvement-review-durability/",
    "12d524b60c200cab643e44f9105169b045602798",
    "AO Foundry PR #199",
    "bounded recursive-improvement review durability evidence",
    "delayed re-review, adversarial drift checks, stale-language sweeps, and reproducibility retests",
    "promote_public_safe_bounded_recursive_improvement_review_durability_evidence_broad_RSI_denied",
    "public_safe_bounded_recursive_improvement_review_durability_evidence_proven_broad_RSI_denied",
    "reviewer-approved bounded recursive-improvement wording evidence",
    "guided evidence-application evidence",
    "reproducibility runbooks",
    "conservative public-safe tracked readback evidence",
    "public-safe tracked readback evidence",
    "stronger recursive-improvement claims remain denied",
    "stronger recursive-improvement wording remains denied",
    "broad_RSI` remains denied",
    "unrestricted self-modification remains denied",
    "broad_RSI",
    "hidden instruction mutation",
    "policy/auth/secret/provider/deploy/release/config/dependency expansion",
    "policy-changing autonomy",
    "public_safe_broad_RSI_governed_campaign_first_segment_state_evidence",
    "AO Foundry PR #203",
    "b7523031d61b11df374e2203bdf44927e2d8432a",
    "docs/evidence/broad-rsi-ten-day-governed-evidence-campaign/",
    "public-safe broad_RSI governed campaign first-segment state evidence",
    "180 / 2500 campaign nodes",
    "10000 SDD slices",
    "approved_campaign_state_wording_broad_RSI_denied",
    "clear_for_campaign_state_hold_for_broad_RSI",
    "promote_public_safe_broad_RSI_governed_campaign_first_segment_state_evidence_broad_RSI_denied",
    "public_safe_broad_RSI_governed_campaign_first_segment_state_evidence_proven_broad_RSI_denied",
    "public_safe_broad_RSI_governed_campaign_segment_07_evidence",
    "AO Foundry PR #210",
    "8f8ac5f8f74d942c7a02a6c2dd39a7c974872bb6",
    "docs/evidence/broad-rsi-ten-day-campaign-segment-07/",
    "public-safe broad_RSI governed campaign segment-07 evidence",
    "2520 / 2800 campaign nodes",
    "27000 SDD slices",
    "approved_segment_07_wording_broad_RSI_denied",
    "clear_for_segment_07_hold_for_broad_RSI",
    "promote_public_safe_broad_RSI_governed_campaign_segment_07_evidence_broad_RSI_denied",
    "public_safe_broad_RSI_governed_campaign_segment_07_evidence_proven_broad_RSI_denied",
    "full 10-day campaign completion",
    "next denied class remains `broad_RSI`",
    "AO Foundry PR #181",
    "d31b6f2247780867c3c72dbda5abb7377f3a1b3e",
    "docs/evidence/recursive-improvement-public-evidence-expansion/",
    "AO Foundry PR #187",
    "ee55f7918b86f997922707e4c0b2ba6536fe43cf",
    "docs/evidence/recursive-improvement-reviewed-boundary-generalization/",
    "AO Foundry PR #191",
    "413b70f15d8f3d0203dc7be076914a2f3b539881",
    "docs/evidence/recursive-improvement-evidence-selection-guidance/",
    "AO Foundry PR #193",
    "4ec509fd64d1fc1ea41ea7f22aae900ba79e09a1",
    "docs/evidence/recursive-improvement-guided-evidence-application/",
    "AO Foundry PR #195",
    "0f742738324c185ba7243bc53ee2f1bc81804ef6",
    "docs/evidence/recursive-improvement-reviewer-approved-wording/",
    "AO Foundry PR #189",
    "860e3f353ab833c4a671b9d0ee6d8101ece2815c",
    "docs/evidence/recursive-improvement-safe-intermediate-claim/",
]

REQUIRED_BLUEPRINT_ATLAS_FOUNDRY_TERMS = [
    "AO Blueprint -> AO Atlas -> AO Foundry",
    "ao.atlas.blueprint-import.v0.1",
    "Atlas is the mandatory compiler between Blueprint and Foundry",
    "Foundry does not accept direct Blueprint handoff",
    "blueprint-atlas-foundry status",
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
    "bounded_rsi_evidence_rehearsal",
    "bounded_rsi_evidence_rehearsal_live_proven=true",
    "b12ac9b62ab8d20b4092d2a5d13081607567e816",
    "bounded_rsi_self_improvement_application",
    "baseline `0.60`",
    "post-change `1.00`",
    "improvement `0.40`",
    "eval/regression passed",
    "highest_proven_live_class",
    "`bounded_rsi_self_improvement_application`",
    "next_denied_class=broad_RSI",
    "broad RSI, hidden",
    "exact_safe_public_claim_wording_conservative_readback_evidence",
    "AO Foundry PR #179",
    "c8baee170100d8f3427e235180581caeb5ee93e0",
    "docs/evidence/rsi-exact-safe-public-claim-wording/",
    "public-safe tracked readback evidence",
    "stronger recursive-improvement claims remain denied",
    "stronger recursive-improvement wording remains denied",
]

REQUIRED_RSI_MAP_TERMS = [
    "claim_level=bounded_governed_rsi",
    "claim_level=full_autonomous_self_mutating_rsi",
    "AO Foundry PR #65",
    "AO Forge PR #142",
    "AO Command PR #28",
    "AO Covenant PR #55",
    "AO Covenant PR #56",
    "AO2 PR #198",
    "AO2 PR #199",
    "AO2 PR #201",
    "ao2-control-plane PR #70",
    "ao2-control-plane PR #71",
    "ao2-control-plane PR #73",
    "ao2.rsi-claim-readiness-audit.v1",
    "ao2.rsi-governed-self-change-dry-run.v1",
    "covenant.live-self-change-authority.v1",
    "live-self-change-authority.packet.json",
    "ao2.cp-ao2-rsi-claim-readiness-readback.v1",
    "ao2.cp-ao2-rsi-self-change-dry-run-readback.v1",
    "ao2.cp-ao2-rsi-authority-packet-readback.v1",
    "AO Foundry PR #175",
    "b12ac9b62ab8d20b4092d2a5d13081607567e816",
    "promote_bounded_rsi_evidence_rehearsal",
    "promote_bounded_rsi_evidence_rehearsal_keep_broad_rsi_denied",
    "AO Blueprint",
    "rsi-first-bounded-self-improvement-application-blueprint",
    "36-node workgraph",
    "ao.foundry.rsi-self-improvement-application-final-rollup.v0.1",
    "bounded_rsi_self_improvement_application=proven",
    "ao.promoter.rsi-self-improvement-application-verdict.v0.1",
    "ao.command.rsi-self-improvement-application-readback.v0.1",
    "class_decision=bounded_rsi_self_improvement_application_proven",
    "AO Foundry PR #179",
    "c8baee170100d8f3427e235180581caeb5ee93e0",
    "docs/evidence/rsi-exact-safe-public-claim-wording/final-rollup.json",
    "exact_safe_public_claim_wording_conservative_readback_evidence=proven",
    "approved_conservative_readback_evidence_only_wording_broad_RSI_denied",
    "clear_for_conservative_readback_wording_hold_for_broad_RSI",
    "promote_exact_safe_public_claim_wording_conservative_readback_evidence_broad_RSI_denied",
    "exact_safe_public_claim_wording_conservative_readback_evidence_proven_broad_RSI_denied",
    "public_safe_bounded_improvement_evidence_expansion_four_attempts=proven",
    "promote_public_safe_bounded_improvement_evidence_expansion_four_attempts_broad_RSI_denied",
    "public_safe_bounded_improvement_evidence_expansion_four_attempts proven; stronger recursive-improvement wording denied; broad_RSI denied",
    "public_safe_reviewed_causal_chain_boundary_generalization_evidence",
    "reviewed causal-chain boundary generalization",
    "public_safe_intermediate_causal_review_claim_evidence",
    "intermediate causal-review",
    "promote_public_safe_intermediate_causal_review_claim_evidence_keep_broad_RSI_denied",
    "public_safe_intermediate_causal_review_claim_evidence_proven_stronger_recursive_improvement_denied_broad_RSI_denied",
    "public_safe_causal_review_evidence_selection_guidance",
    "promote_public_safe_causal_review_evidence_selection_guidance_keep_broad_RSI_denied",
    "public_safe_causal_review_evidence_selection_guidance_proven_stronger_recursive_improvement_denied_broad_RSI_denied",
    "public_safe_guided_evidence_application_four_attempts",
    "promote_public_safe_guided_evidence_application_four_attempts_keep_broad_RSI_denied",
    "public_safe_guided_evidence_application_four_attempts_proven_stronger_recursive_improvement_denied_broad_RSI_denied",
    "public_safe_reviewer_approved_bounded_recursive_improvement_wording_evidence",
    "promote_public_safe_reviewer_approved_bounded_recursive_improvement_wording_evidence_broad_RSI_denied",
    "public_safe_reviewer_approved_bounded_recursive_improvement_wording_evidence_proven_broad_RSI_denied",
    "docs/evidence/recursive-improvement-bounded-wording-generality/final-rollup.json",
    "public_safe_bounded_recursive_improvement_wording_generality_evidence_proven_broad_RSI_denied",
    "docs/evidence/recursive-improvement-review-durability/final-rollup.json",
    "public_safe_bounded_recursive_improvement_review_durability_evidence_proven_broad_RSI_denied",
    "promote_public_safe_bounded_recursive_improvement_review_durability_evidence_broad_RSI_denied",
    "promote_public_safe_bounded_recursive_improvement_wording_generality_evidence_broad_RSI_denied",
    "docs/evidence/recursive-improvement-claim-threshold-calibration/final-rollup.json",
    "public_safe_recursive_improvement_claim_threshold_calibration_evidence_proven_broad_RSI_denied",
    "promote_public_safe_recursive_improvement_claim_threshold_calibration_evidence_broad_RSI_denied",
    "broad_RSI",
    "mutation authority",
    "rollback evidence",
    "live self-change evidence",
    "docs/evidence/broad-rsi-ten-day-governed-evidence-campaign/final-rollup.json",
    "public_safe_broad_RSI_governed_campaign_first_segment_state_evidence=proven",
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
    '"number": 195',
    '"number": 203',
    '"Add broad RSI campaign first segment evidence"',
    '"number": 197',
    '"Add reviewer-approved wording evidence"',
    '"docs/evidence/recursive-improvement-reviewer-approved-wording/final-rollup.json"',
    '"number": 56',
    '"Add RSI manifest command"',
    '"Define RSI claim level vocabulary"',
    '"number": 198',
    '"Add AO2 RSI claim readiness audit"',
    '"ao2.rsi-claim-readiness-audit.v1"',
    '"number": 199',
    '"Add AO2 RSI self-change dry-run evidence"',
    '"ao2.rsi-governed-self-change-dry-run.v1"',
    '"number": 201',
    '"Emit RSI authority packet dry-run evidence"',
    '"covenant.live-self-change-authority.v1"',
    '"live-self-change-authority.packet.json"',
    '"number": 70',
    '"Add AO2 RSI claim readiness readback"',
    '"ao2.cp-ao2-rsi-claim-readiness-readback.v1"',
    '"number": 71',
    '"Add AO2 RSI self-change dry-run readback"',
    '"ao2.cp-ao2-rsi-self-change-dry-run-readback.v1"',
    '"number": 73',
    '"Add AO2 RSI authority packet readback"',
    '"ao2.cp-ao2-rsi-authority-packet-readback.v1"',
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
    atlas_text = read_text(ROOT / "ao-atlas" / "README.md")
    blueprint_text = read_text(ROOT / "ao-blueprint" / "README.md")
    rsi_claim_text = "\n".join([root_text, overview_text, command_text])
    for required_file in REQUIRED_RSI_MAP_FILES:
        if not (ROOT / required_file).exists():
            fail(f"missing required RSI map file: {required_file}")
    for required_file in REQUIRED_LIVE_MUTATION_LADDER_FILES:
        if not (ROOT / required_file).exists():
            fail(f"missing required live mutation ladder file: {required_file}")

    for claim in REQUIRED_RSI_CLAIMS:
        if claim not in rsi_claim_text:
            fail(f"architecture docs missing RSI claim guard: {claim}")

    ladder_text = "\n".join(
        [
            root_text,
            overview_text,
            read_text(ROOT / "overview" / "LIVE-MUTATION-DOCUMENTATION-CONSISTENCY.md"),
            read_text(ROOT / "overview" / "LIVE-MUTATION-STALE-LANGUAGE-SWEEP.md"),
            read_text(ROOT / "overview" / "MUTATION-AUTHORITY-LADDER.md"),
        ]
    )
    for term in REQUIRED_LIVE_MUTATION_LADDER_TERMS:
        if term not in ladder_text:
            fail(f"architecture docs missing live mutation ladder term: {term}")

    for atlas_term in [
        "AO Atlas",
        "ao.atlas.stack-instance.v0.1",
        "ao.atlas.workgraph.v0.1",
        "ao.atlas.context-pack.v0.1",
        "ao.atlas.foundry-import.v0.1",
        "ao.foundry.atlas-readback.v0.1",
        "ao.foundry.atlas-status.v0.1",
        "does not schedule, execute, approve, publish, call providers, or mutate sibling repositories",
    ]:
        if atlas_term not in "\n".join([root_text, overview_text, atlas_text]):
            fail(f"architecture docs missing AO Atlas term: {atlas_term}")

    blueprint_atlas_foundry_text = "\n".join([root_text, overview_text, blueprint_text, atlas_text, command_text])
    for term in REQUIRED_BLUEPRINT_ATLAS_FOUNDRY_TERMS:
        if term not in blueprint_atlas_foundry_text:
            fail(f"architecture docs missing Blueprint -> Atlas -> Foundry term: {term}")

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
