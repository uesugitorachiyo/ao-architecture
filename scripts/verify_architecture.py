#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from verify_copied_schema_classification import validate_document as validate_copied_schema_classification
from verify_component_release_classification import validate_manifest as validate_component_release_classification
from verify_external_beta_preflight import CAPABILITY_LABELS, EXPECTED_REPOSITORIES, validate_manifest


ROOT = Path(__file__).resolve().parents[1]

ACTIVE_REPOS = [
    "ao-mission",
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
    "images/ao-mission-pipeline.svg",
    "images/ao-mission-gateway-authority-map.svg",
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
    "highest proven live class is\n`public_safe_unrestricted_self_modification_authority_request_dry_run_four_attempts`",
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
    "broad_RSI",
    "AO Foundry PR #211",
    "630edc70905db745380edd1072e04b546dcccfe3",
    "docs/evidence/broad-rsi-ten-day-campaign-segment-08/",
    "Governed Broad RSI Public-Safe Campaign Completion",
    "2800 / 2800",
    "28000 SDD slices",
    "approved_exact_governed_broad_RSI_wording",
    "clear_for_governed_broad_RSI_public_wording",
    "promote_broad_RSI_governed_public_safe_campaign_completion_unrestricted_boundaries_denied",
    "broad_RSI_proven_under_governed_public_safe_campaign_completion_boundaries",
    "full 10-day campaign completion",
    "next denied class is `unrestricted_self_modification`",
    "Unrestricted Self-Modification Sandbox Containment Evidence",
    "public_safe_unrestricted_self_modification_sandbox_containment_rehearsal",
    "AO Foundry PR #216",
    "7881613065de48f2547833a9ecc9a9011b55a96a",
    "docs/evidence/unrestricted-self-modification-sandbox-containment/",
    "420 / 420",
    "deny_unrestricted_self_modification_allow_sandbox_containment_rehearsal",
    "approve_sandbox_containment_wording_deny_unrestricted_self_modification_claim",
    "clear_sandbox_containment_hold_unrestricted_self_modification",
    "promote_public_safe_unrestricted_self_modification_sandbox_containment_rehearsal_keep_unrestricted_self_modification_denied",
    "public_safe_unrestricted_self_modification_sandbox_containment_rehearsal_proven_unrestricted_self_modification_denied",
    "Unrestricted Self-Modification Adversarial Negative Controls",
    "public_safe_unrestricted_self_modification_adversarial_negative_controls",
    "AO Foundry PR #217",
    "b7e487022ae7436be13e0a49d0bf15f5c7936145",
    "docs/evidence/unrestricted-self-modification-adversarial-negative-controls/",
    "560 / 560",
    "deny_unrestricted_self_modification_allow_adversarial_negative_controls",
    "clear_adversarial_negative_controls_hold_unrestricted_self_modification",
    "promote_public_safe_unrestricted_self_modification_adversarial_negative_controls_keep_unrestricted_self_modification_denied",
    "public_safe_unrestricted_self_modification_adversarial_negative_controls_proven_unrestricted_self_modification_denied",
    "Unrestricted Self-Modification Bounded Reversible Application",
    "public_safe_bounded_reversible_self_change_application_rehearsal",
    "AO Foundry PR #218",
    "3b2feaced4207c97f98cef44f3b3276c59a7873b",
    "docs/evidence/unrestricted-self-modification-bounded-reversible-application/",
    "640 / 640",
    "baseline `0.70`",
    "post-change `0.94`",
    "improvement `0.24`",
    "deny_unrestricted_self_modification_allow_bounded_reversible_application",
    "clear_bounded_reversible_application_hold_unrestricted_self_modification",
    "promote_public_safe_bounded_reversible_self_change_application_rehearsal_keep_unrestricted_self_modification_denied",
    "public_safe_bounded_reversible_self_change_application_rehearsal_proven_unrestricted_self_modification_denied",
    "Repeated Bounded Reversible Self-Change Applications",
    "public_safe_repeated_bounded_reversible_self_change_applications_four_attempts",
    "AO Foundry PR #219",
    "88b52ce1ca9e8679cccdc64fe21c2b63340076b5",
    "docs/evidence/unrestricted-self-modification-repeated-bounded-applications/",
    "960 / 960",
    "support/readback evidence quality `0.71`",
    "public-safety scan readback quality `0.69`",
    "rollback/retraction runbook quality `0.67`",
    "cross-evidence linking readback quality `0.66`",
    "deny_unrestricted_self_modification_allow_repeated_bounded_applications",
    "clear_repeated_bounded_applications_hold_unrestricted_self_modification",
    "promote_public_safe_repeated_bounded_reversible_self_change_applications_four_attempts_keep_unrestricted_self_modification_denied",
    "public_safe_repeated_bounded_reversible_self_change_applications_four_attempts_proven_unrestricted_self_modification_denied",
    "Bounded Sandboxed Self-Change Applications",
    "public_safe_bounded_sandboxed_self_change_applications_non_readback_four_attempts",
    "AO Foundry PR #220",
    "eff03edd62ba32af57defc71a7f3b800f320b8d3",
    "docs/evidence/unrestricted-self-modification-bounded-sandbox-applications/",
    "140 / 140",
    "fixture/schema evidence quality `0.68`",
    "CI/readiness diagnostics evidence quality `0.66`",
    "public-safety rule calibration evidence quality `0.65`",
    "rollback/evidence-link integrity quality `0.64`",
    "deny_unrestricted_self_modification_allow_bounded_sandbox_non_readback_applications",
    "approve_bounded_sandbox_non_readback_wording_deny_unrestricted_self_modification_claim",
    "clear_bounded_sandbox_non_readback_applications_hold_unrestricted_self_modification",
    "promote_public_safe_bounded_sandboxed_self_change_applications_non_readback_four_attempts_keep_unrestricted_self_modification_denied",
    "public_safe_bounded_sandboxed_self_change_applications_non_readback_four_attempts_proven_unrestricted_self_modification_denied",
    "Support-Code/Eval Sandboxed Self-Change",
    "public_safe_bounded_sandboxed_self_change_support_code_eval_four_attempts",
    "AO Foundry PR #222",
    "9938df55959ac904295fd4d0dc0eddc52626c972",
    "docs/evidence/unrestricted-self-modification-support-code-eval/",
    "240 / 240",
    "support-code fixture validation quality `0.72`",
    "eval harness diagnostics quality `0.70`",
    "rollback automation evidence quality `0.69`",
    "sandbox containment trace quality `0.68`",
    "deny_unrestricted_self_modification_allow_support_code_eval",
    "approve_support_code_eval_wording_deny_unrestricted_self_modification_claim",
    "clear_support_code_eval_hold_unrestricted_self_modification",
    "promote_public_safe_bounded_sandboxed_self_change_support_code_eval_four_attempts_keep_unrestricted_self_modification_denied",
    "public_safe_bounded_sandboxed_self_change_support_code_eval_four_attempts_proven_unrestricted_self_modification_denied",
    "sandbox containment bypass",
    "bounded sandboxed self-change multi-surface support/eval negative-control evidence",
    "docs/evidence/unrestricted-self-modification-multi-surface-support-eval/final-rollup.json",
    "public_safe_bounded_sandboxed_self_change_multi_surface_support_eval_negative_controls_four_attempts=proven",

    "Multi-Surface Support/Eval Negative-Control Sandboxed Self-Change",
    "public_safe_bounded_sandboxed_self_change_multi_surface_support_eval_negative_controls_four_attempts",
    "AO Foundry PR #223",
    "3cd8c470538d626bebfc63262979f364ea53b081",
    "docs/evidence/unrestricted-self-modification-multi-surface-support-eval/",
    "300 / 300",
    "cross-repo support fixture consistency `0.74`",
    "evaluation harness negative-control coverage `0.71`",
    "sandbox containment bypass rejection evidence `0.70`",
    "cross-surface rollback/readiness traceability `0.69`",
    "deny_unrestricted_self_modification_allow_multi_surface_support_eval_negative_controls",
    "approve_multi_surface_support_eval_wording_deny_unrestricted_self_modification_claim",
    "clear_multi_surface_support_eval_hold_unrestricted_self_modification",
    "promote_public_safe_bounded_sandboxed_self_change_multi_surface_support_eval_negative_controls_four_attempts_keep_unrestricted_self_modification_denied",
    "public_safe_bounded_sandboxed_self_change_multi_surface_support_eval_negative_controls_four_attempts_proven_unrestricted_self_modification_denied",
    "Delegated Dry-Run Authority-Gap Sandboxed Self-Change",
    "public_safe_bounded_sandboxed_self_change_delegated_dry_run_authority_gap_four_attempts",
    "AO Foundry PR #224",
    "afdd6562dfe83cec2eaa5d4172e23f9cec26c14e",
    "docs/evidence/unrestricted-self-modification-delegated-dry-run-authority-gap/",
    "docs/evidence/unrestricted-self-modification-delegated-dry-run-authority-gap/final-rollup.json",
    "360 / 360",
    "delegated dry-run ticket/readback consistency `0.73`",
    "Forge/AO2 bounded packet containment evidence `0.71`",
    "Foundry-to-Atlas handoff no-authority-broadening evidence `0.70`",
    "rollback/retraction/kill-switch traceability across delegated dry-run surfaces `0.69`",
    "deny_unrestricted_self_modification_allow_delegated_dry_run_authority_gap",
    "approve_delegated_dry_run_authority_gap_wording_deny_unrestricted_self_modification_claim",
    "clear_delegated_dry_run_authority_gap_hold_unrestricted_self_modification",
    "promote_public_safe_bounded_sandboxed_self_change_delegated_dry_run_authority_gap_four_attempts_keep_unrestricted_self_modification_denied",
    "public_safe_bounded_sandboxed_self_change_delegated_dry_run_authority_gap_four_attempts_proven_unrestricted_self_modification_denied",
    "Sandbox-Boundary Stress Sandboxed Self-Change",
    "public_safe_bounded_sandboxed_self_change_sandbox_boundary_stress_four_attempts",
    "AO Foundry PR #225",
    "8297e87cb32b8889a205ac6d38736e32004ba824",
    "docs/evidence/unrestricted-self-modification-sandbox-boundary-stress/",
    "docs/evidence/unrestricted-self-modification-sandbox-boundary-stress/final-rollup.json",
    "420 / 420",
    "sandbox boundary fixture denial consistency `0.74`",
    "containment escape negative-control coverage `0.72`",
    "delegated packet boundary drift detection `0.71`",
    "rollback/kill-switch traceability under sandbox-boundary stress `0.70`",
    "external execution authority",
    "deny_unrestricted_self_modification_allow_sandbox_boundary_stress",
    "approve_sandbox_boundary_stress_wording_deny_unrestricted_self_modification_claim",
    "clear_sandbox_boundary_stress_hold_unrestricted_self_modification",
    "promote_public_safe_bounded_sandboxed_self_change_sandbox_boundary_stress_four_attempts_keep_unrestricted_self_modification_denied",
    "public_safe_bounded_sandboxed_self_change_sandbox_boundary_stress_four_attempts_proven_unrestricted_self_modification_denied",
    "public_safe_bounded_sandboxed_self_change_sandbox_boundary_generality_four_attempts",
    "AO Foundry PR #227",
    "d5a03bded8157df53b4fedc0736e953f29854501",
    "docs/evidence/unrestricted-self-modification-sandbox-boundary-generality/",
    "docs/evidence/unrestricted-self-modification-sandbox-boundary-generality/final-rollup.json",
    "500 / 500",
    "sandboxed evidence-link permission boundary `0.75`",
    "sandboxed negative-control fixture portability `0.73`",
    "sandboxed rollback replay boundary `0.72`",
    "sandboxed cross-surface claim-minimization boundary `0.71`",
    "deny_unrestricted_self_modification_allow_sandbox_boundary_generality",
    "approve_sandbox_boundary_generality_wording_deny_unrestricted_self_modification_claim",
    "clear_sandbox_boundary_generality_hold_unrestricted_self_modification",
    "promote_public_safe_bounded_sandboxed_self_change_sandbox_boundary_generality_four_attempts_keep_unrestricted_self_modification_denied",
    "public_safe_bounded_sandboxed_self_change_sandbox_boundary_generality_four_attempts_proven_unrestricted_self_modification_denied",
    "public_safe_external_execution_authority_boundary_fixture_evidence_four_attempts",
    "AO Foundry PR #229",
    "fcd734c1907c3649166334a5b15c42d0e2e990de",
    "docs/evidence/external-execution-authority-boundary/",
    "docs/evidence/external-execution-authority-boundary/final-rollup.json",
    "260 / 260",
    "provider-call denial fixture quality `0.76`",
    "credential-use denial fixture quality `0.74`",
    "external-command allowlist readback quality `0.73`",
    "rollback/retraction evidence quality `0.72`",
    "actual external execution authority",
    "provider calls",
    "credential use",
    "deny_actual_external_execution_authority_allow_fixture_boundary_evidence",
    "approve_external_execution_boundary_fixture_wording_deny_actual_external_execution_authority",
    "clear_external_execution_boundary_fixture_evidence_hold_actual_external_execution_authority",
    "promote_public_safe_external_execution_authority_boundary_fixture_evidence_four_attempts_keep_unrestricted_self_modification_denied",
    "public_safe_external_execution_authority_boundary_fixture_evidence_four_attempts_proven_external_execution_authority_denied",
    "public_safe_sandboxed_external_execution_dry_run_packet_evidence_four_attempts",
    "AO Foundry PR #231",
    "18a609f430a9a7e91fc0e62aea4b5789144c9fec",
    "docs/evidence/sandboxed-external-execution-dry-run-packet/",
    "docs/evidence/sandboxed-external-execution-dry-run-packet/final-rollup.json",
    "520 / 520",
    "provider-call dry-run ticket fixture quality `0.77`",
    "credential-use denial packet quality `0.75`",
    "external-command dry-run allowlist packet quality `0.74`",
    "sandbox containment bypass negative-control packet quality `0.73`",
    "deny_actual_external_execution_authority_allow_dry_run_packet_evidence",
    "approve_sandboxed_external_execution_dry_run_packet_wording_deny_actual_external_execution_authority",
    "clear_sandboxed_external_execution_dry_run_packet_hold_actual_external_execution_authority",
    "promote_public_safe_sandboxed_external_execution_dry_run_packet_evidence_four_attempts_keep_unrestricted_self_modification_denied",
    "public_safe_sandboxed_external_execution_dry_run_packet_evidence_four_attempts_proven_external_execution_authority_denied",
    "bounded_packet_enforced_for_dry_run_authority_evidence_only",
    "public_safe_external_execution_authority_readiness_boundary_map",
    "AO Foundry PR #232",
    "b6f409946775bc19a04f5ca25a9aea91b9631707",
    "docs/evidence/external-execution-authority-readiness-boundary/",
    "docs/evidence/external-execution-authority-readiness-boundary/final-rollup.json",
    "640 / 640",
    "execution-authority denial readiness-map quality `0.78`",
    "provider-call quarantine readiness quality `0.76`",
    "credential non-use readiness quality `0.75`",
    "sandbox bypass stop-readiness quality `0.74`",
    "approved_public_safe_external_execution_readiness_boundary_only_actual_external_execution_denied",
    "narrow_readiness_boundary_wording_supported_actual_external_execution_wording_denied",
    "clear_for_readiness_boundary_map_hold_for_actual_external_execution_and_unrestricted_self_modification",
    "promote_public_safe_external_execution_authority_readiness_boundary_map_actual_external_execution_denied_unrestricted_self_modification_denied",
    "public_safe_external_execution_authority_readiness_boundary_map_proven_actual_external_execution_denied_unrestricted_self_modification_denied",
    "all_packets_exact_scope_reversible_dry_run_only",
    "public_safe_bounded_sandboxed_external_execution_authority_rehearsal_four_attempts",
    "AO Foundry PR #233",
    "ee11d0e8093d357d803e6a5df8c36e5badf46dc6",
    "docs/evidence/bounded-sandboxed-external-execution-authority-rehearsal/",
    "docs/evidence/bounded-sandboxed-external-execution-authority-rehearsal/final-rollup.json",
    "720 / 720",
    "allowlisted local command sandbox rehearsal quality",
    "sandbox environment isolation evidence quality",
    "provider and credential quarantine during sandboxed execution quality",
    "kill-switch rollback and retraction evidence quality",
    "approve_bounded_sandboxed_external_execution_authority_rehearsal_actual_external_execution_broad_authority_denied",
    "approve_bounded_sandboxed_external_execution_authority_rehearsal_wording_deny_unrestricted_self_modification",
    "clear_bounded_sandboxed_external_execution_authority_rehearsal_hold_unrestricted_self_modification_and_sandbox_bypass",
    "promote_public_safe_bounded_sandboxed_external_execution_authority_rehearsal_four_attempts_keep_unrestricted_self_modification_denied",
    "public_safe_bounded_sandboxed_external_execution_authority_rehearsal_four_attempts_proven_unrestricted_self_modification_denied",
    "bounded_packet_enforced_for_allowlisted_local_command_sandbox_rehearsal_only",
    "public_safe_contained_external_command_self_change_application_four_attempts",
    "AO Foundry PR #234",
    "a9ea020f4b19a43c22dcde7194409989862ae951",
    "docs/evidence/unrestricted-self-modification-contained-external-command-self-change/",
    "docs/evidence/unrestricted-self-modification-contained-external-command-self-change/final-rollup.json",
    "contained local-command readback fixture improvement",
    "contained local-command eval fixture improvement",
    "contained local-command rollback fixture improvement",
    "contained local-command stale-language fixture improvement",
    "deny_unrestricted_self_modification_allow_contained_external_command_self_change_application",
    "approve_contained_external_command_self_change_wording_deny_unrestricted_self_modification_claim",
    "clear_contained_external_command_self_change_hold_unrestricted_self_modification_and_sandbox_bypass",
    "promote_public_safe_contained_external_command_self_change_application_four_attempts_keep_unrestricted_self_modification_denied",
    "public_safe_contained_external_command_self_change_application_four_attempts_proven_unrestricted_self_modification_denied",
    "bounded_packet_enforced_for_contained_external_command_self_change_application",
    "public_safe_sandbox_bypass_resistance_evidence_four_attempts",
    "AO Foundry PR #235",
    "322bd8b2ce3b6f8134196d33b0f605e0fe68f938",
    "docs/evidence/unrestricted-self-modification-sandbox-bypass-resistance/",
    "docs/evidence/unrestricted-self-modification-sandbox-bypass-resistance/final-rollup.json",
    "9000 / 9000",
    "sandbox bypass negative-control readback quality",
    "allowlist-denial fixture quality",
    "containment-boundary rollback trace quality",
    "stale-language and public-claim bypass denial quality",
    "deny_unrestricted_self_modification_allow_sandbox_bypass_resistance_evidence",
    "approve_sandbox_bypass_resistance_wording_deny_unrestricted_self_modification_claim",
    "clear_sandbox_bypass_resistance_hold_unrestricted_self_modification_and_bypass_authority",
    "promote_public_safe_sandbox_bypass_resistance_evidence_four_attempts_keep_unrestricted_self_modification_denied",
    "public_safe_sandbox_bypass_resistance_evidence_four_attempts_proven_unrestricted_self_modification_denied",
    "bounded_packet_enforced_for_sandbox_bypass_resistance_evidence_only",
    "public_safe_unrestricted_self_modification_authority_escalation_criteria_four_attempts",
    "AO Foundry PR #236",
    "b5f3b9a4f3164635a0dff078675a15a03f7c2fb6",
    "docs/evidence/unrestricted-self-modification-authority-escalation-criteria/",
    "docs/evidence/unrestricted-self-modification-authority-escalation-criteria/final-rollup.json",
    "10000 / 10000",
    "authority threshold rubric completeness",
    "denied-surface escalation mapping quality",
    "operator and Covenant escalation readback quality",
    "rollback and kill-switch escalation proof quality",
    "deny_unrestricted_self_modification_allow_authority_escalation_criteria_evidence",
    "approve_authority_escalation_criteria_wording_deny_unrestricted_self_modification_claim",
    "clear_authority_escalation_criteria_hold_unrestricted_self_modification_and_bypass_authority",
    "promote_public_safe_unrestricted_self_modification_authority_escalation_criteria_four_attempts_keep_unrestricted_self_modification_denied",
    "public_safe_unrestricted_self_modification_authority_escalation_criteria_four_attempts_proven_unrestricted_self_modification_denied",
    "bounded_packet_enforced_for_authority_escalation_criteria_evidence_only",
    "public_safe_unrestricted_self_modification_authority_request_dry_run_four_attempts",
    "AO Foundry PR #237",
    "1eda6a0c0fc6a97580e7ef52a94cfae85f41d5f2",
    "docs/evidence/unrestricted-self-modification-authority-request-dry-run/",
    "docs/evidence/unrestricted-self-modification-authority-request-dry-run/final-rollup.json",
    "12000 / 12000",
    "authority-request packet completeness",
    "Covenant denial ticket readback quality",
    "Sentinel hold and kill-switch request trace quality",
    "Command and Promoter no-execution decision quality",
    "deny_unrestricted_self_modification_allow_authority_request_dry_run_evidence",
    "approve_authority_request_dry_run_wording_deny_unrestricted_self_modification_claim",
    "clear_authority_request_dry_run_hold_unrestricted_self_modification_and_bypass_authority",
    "promote_public_safe_unrestricted_self_modification_authority_request_dry_run_four_attempts_keep_unrestricted_self_modification_denied",
    "public_safe_unrestricted_self_modification_authority_request_dry_run_four_attempts_proven_unrestricted_self_modification_denied",
    "bounded_packet_enforced_for_authority_request_dry_run_evidence_only",
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

REQUIRED_AO_MISSION_CONTRACT_MAP_TERMS = [
    "AO Mission contract map",
    "AO Mission Gateway Authority Map",
    "| Contract | Producer | Consumer | Authority boundary |",
    "ao.mission.record.v0.1",
    "ao.mission.event-loop-decision.v0.1",
    "ao.mission.scheduler-readback.v0.1",
    "ao.mission.scheduler-recovery-readback.v0.1",
    "ao.mission.ledger-compaction-readback.v0.1",
    "ao.mission.timeline-compaction-readback.v0.1",
    "ao.mission.route-decision.v0.1",
    "AO Mission route-history exports",
    "AO Mission route history",
    "ao.mission.gateway-intent-ledger.v0.1",
    "ao.command.mission-gateway.v0.1",
    "ao.command.mission-evidence.v0.1",
    "A2A fixture server readback",
    "Telegram freshness classification",
    "covenant.scheduler-recovery-authority-denial.v1",
    "gateway/recovery/compaction -> Atlas -> Foundry -> Command readback path",
    "gateway -> ledger -> Atlas provenance path",
    "Telegram, A2A, codex-cron",
    "scheduler recovery -> ledger compaction -> Atlas/Foundry provenance path",
    "ao.command.mission-status.v0.1",
    "ao.mission.artifact-manifest.v0.1",
    "ao.mission.archive.v0.1",
    "ao.mission.archive-validation.v0.1",
    "ao.atlas.ao-mission-import.v0.1",
    "ao.atlas.ao-mission-workgraph-metadata.v0.1",
    "ao.foundry.ao-mission-smoke-readback.v0.1",
    "ao.foundry.ao-mission-final-rollup-smoke.v0.1",
    "ao.foundry.ao-mission-readiness-ledger.v0.1",
    "ao.foundry.ao-mission-e2e-smoke.v0.1",
    "intent/readback only",
    "scheduler wakeup substrate only",
    "Recovery provenance only",
    "Ledger compaction provenance only",
    "Timeline compaction provenance only",
    "artifact-ref digest mismatch blocks import",
    "Mission archive validation provenance",
    "Gateway readiness rollup provenance",
    "correlation_id",
    "optional scheduler-recovery",
    "optional ledger-compaction",
    "optional timeline-compaction",
]

REQUIRED_AO_MISSION_GATEWAY_AUTHORITY_TERMS = [
    "AO Mission Gateway Authority Map",
    "Telegram gateway",
    "A2A gateway",
    "A2A fixture server readback",
    "Telegram freshness classification",
    "codex-cron adapter",
    "streaming=false",
    "push_notifications=false",
    "state_transition_history=true",
    "artifact_readbacks=true",
    "covenant.gateway-intent-authority-denial.v1",
    "covenant.telegram-intent-authority-denial.v1",
    "covenant.a2a-intent-authority-denial.v1",
    "covenant.scheduler-recovery-authority-denial.v1",
    "External agents receive no direct mutation authority",
    "Artifact refs are digest-bound readbacks",
    "Mission archive validation is provenance only",
    "Gateway readiness rollup is provenance only",
    "Replay correlation IDs connect gateway readbacks to rollups",
    "No gateway implementation should add a shortcut",
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
    "next_denied_class=unrestricted_self_modification",
    "public_safe_unrestricted_self_modification_sandbox_containment_rehearsal",
    "public_safe_unrestricted_self_modification_adversarial_negative_controls",
    "public_safe_bounded_reversible_self_change_application_rehearsal",
    "unrestricted self-modification remains denied",
    "public_safe_bounded_sandboxed_self_change_applications_non_readback_four_attempts",
    "bounded sandboxed self-change application evidence",
    "public_safe_bounded_sandboxed_self_change_support_code_eval_four_attempts",
    "bounded sandboxed self-change support-code/eval evidence",
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
    "public_safe_unrestricted_self_modification_sandbox_containment_rehearsal=proven",
    "docs/evidence/unrestricted-self-modification-sandbox-containment/final-rollup.json",
    "public_safe_unrestricted_self_modification_sandbox_containment_rehearsal_proven_unrestricted_self_modification_denied",
    "public_safe_unrestricted_self_modification_adversarial_negative_controls=proven",
    "docs/evidence/unrestricted-self-modification-adversarial-negative-controls/final-rollup.json",
    "public_safe_unrestricted_self_modification_adversarial_negative_controls_proven_unrestricted_self_modification_denied",
    "public_safe_bounded_reversible_self_change_application_rehearsal=proven",
    "docs/evidence/unrestricted-self-modification-bounded-reversible-application/final-rollup.json",
    "public_safe_bounded_reversible_self_change_application_rehearsal_proven_unrestricted_self_modification_denied",
    "public_safe_bounded_sandboxed_self_change_applications_non_readback_four_attempts=proven",
    "docs/evidence/unrestricted-self-modification-bounded-sandbox-applications/final-rollup.json",
    "public_safe_bounded_sandboxed_self_change_applications_non_readback_four_attempts_proven_unrestricted_self_modification_denied",
    "public_safe_bounded_sandboxed_self_change_support_code_eval_four_attempts=proven",
    "docs/evidence/unrestricted-self-modification-support-code-eval/final-rollup.json",
    "public_safe_bounded_sandboxed_self_change_support_code_eval_four_attempts_proven_unrestricted_self_modification_denied",
    "public_safe_bounded_sandboxed_self_change_delegated_dry_run_authority_gap_four_attempts=proven",
    "docs/evidence/unrestricted-self-modification-delegated-dry-run-authority-gap/final-rollup.json",
    "public_safe_bounded_sandboxed_self_change_delegated_dry_run_authority_gap_four_attempts_proven_unrestricted_self_modification_denied",
    "public_safe_bounded_sandboxed_self_change_sandbox_boundary_stress_four_attempts=proven",
    "docs/evidence/unrestricted-self-modification-sandbox-boundary-stress/final-rollup.json",
    "public_safe_bounded_sandboxed_self_change_sandbox_boundary_stress_four_attempts_proven_unrestricted_self_modification_denied",
    "public_safe_bounded_sandboxed_self_change_sandbox_boundary_generality_four_attempts=proven",
    "docs/evidence/unrestricted-self-modification-sandbox-boundary-generality/final-rollup.json",
    "public_safe_bounded_sandboxed_self_change_sandbox_boundary_generality_four_attempts_proven_unrestricted_self_modification_denied",
    "public_safe_external_execution_authority_boundary_fixture_evidence_four_attempts=proven",
    "docs/evidence/external-execution-authority-boundary/final-rollup.json",
    "public_safe_external_execution_authority_boundary_fixture_evidence_four_attempts_proven_external_execution_authority_denied",
    "public_safe_sandboxed_external_execution_dry_run_packet_evidence_four_attempts=proven",
    "docs/evidence/sandboxed-external-execution-dry-run-packet/final-rollup.json",
    "public_safe_sandboxed_external_execution_dry_run_packet_evidence_four_attempts_proven_external_execution_authority_denied",
    "public_safe_external_execution_authority_readiness_boundary_map=proven",
    "docs/evidence/external-execution-authority-readiness-boundary/final-rollup.json",
    "public_safe_external_execution_authority_readiness_boundary_map_proven_actual_external_execution_denied_unrestricted_self_modification_denied",
    "public_safe_contained_external_command_self_change_application_four_attempts=proven",
    "docs/evidence/unrestricted-self-modification-contained-external-command-self-change/final-rollup.json",
    "public_safe_contained_external_command_self_change_application_four_attempts_proven_unrestricted_self_modification_denied",
    "public_safe_sandbox_bypass_resistance_evidence_four_attempts",
    "public_safe_sandbox_bypass_resistance_evidence_four_attempts=proven",
    "docs/evidence/unrestricted-self-modification-sandbox-bypass-resistance/final-rollup.json",
    "public_safe_sandbox_bypass_resistance_evidence_four_attempts_proven_unrestricted_self_modification_denied",
    "public_safe_unrestricted_self_modification_authority_escalation_criteria_four_attempts=proven",
    "docs/evidence/unrestricted-self-modification-authority-escalation-criteria/final-rollup.json",
    "public_safe_unrestricted_self_modification_authority_escalation_criteria_four_attempts_proven_unrestricted_self_modification_denied",
    "public_safe_unrestricted_self_modification_authority_request_dry_run_four_attempts=proven",
    "docs/evidence/unrestricted-self-modification-authority-request-dry-run/final-rollup.json",
    "public_safe_unrestricted_self_modification_authority_request_dry_run_four_attempts_proven_unrestricted_self_modification_denied",
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

SAFETY_SCAN_SUFFIXES = {".md", ".svg", ".json", ".txt"}
MAX_PUBLIC_SAFETY_SCAN_FILES = 4096
MAX_PUBLIC_SAFETY_SCAN_FILE_BYTES = 1 * 1024 * 1024
MAX_PUBLIC_SAFETY_SCAN_TOTAL_BYTES = 16 * 1024 * 1024


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


def relative_display(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def public_safety_scan_paths(
    root: Path,
    suffixes: set[str] | None = None,
    max_files: int = MAX_PUBLIC_SAFETY_SCAN_FILES,
    max_file_bytes: int = MAX_PUBLIC_SAFETY_SCAN_FILE_BYTES,
    max_total_bytes: int = MAX_PUBLIC_SAFETY_SCAN_TOTAL_BYTES,
) -> list[Path]:
    suffixes = suffixes or SAFETY_SCAN_SUFFIXES
    root_info = root.lstat()
    if root_info.st_mode & 0o170000 == 0o120000:
        raise ValueError(f"public-safety scan symlink is not allowed: {relative_display(root, root)}")

    paths: list[Path] = []
    total_bytes = 0
    for path in sorted(root.rglob("*")):
        if ".git" in path.parts:
            continue
        info = path.lstat()
        if path.is_symlink():
            raise ValueError(f"public-safety scan symlink is not allowed: {relative_display(root, path)}")
        if not path.is_file() or path.suffix not in suffixes:
            continue
        if info.st_size > max_file_bytes:
            raise ValueError(f"public-safety scan file size limit exceeded for {relative_display(root, path)}")
        paths.append(path)
        if len(paths) > max_files:
            raise ValueError("public-safety scan file count limit exceeded")
        total_bytes += info.st_size
        if total_bytes > max_total_bytes:
            raise ValueError("public-safety scan total byte limit exceeded")
    return paths


def assert_contains(path: Path, needle: str) -> None:
    text = read_text(path)
    if needle not in text:
        fail(f"{path.relative_to(ROOT)} missing {needle}")


def main() -> int:
    readme = ROOT / "README.md"
    readiness = ROOT / "overview" / "PRODUCTION-READINESS.md"
    evidence_catalog = ROOT / "overview" / "EVIDENCE-CATALOG.md"
    manifest_path = ROOT / "stack" / "external-beta-tested-stack.json"
    component_release_classification_path = ROOT / "stack" / "component-release-classification.json"
    try:
        manifest = json.loads(manifest_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid external-beta tested-stack manifest: {exc}")
    for error in validate_manifest(manifest):
        fail(f"external-beta tested-stack manifest invalid: {error}")
    try:
        component_release_classification = json.loads(component_release_classification_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid component release classification manifest: {exc}")
    for error in validate_component_release_classification(component_release_classification):
        fail(f"component release classification invalid: {error}")

    readiness_text = read_text(readiness)
    repository_names = {entry["repository"] for entry in manifest["repositories"]}
    if repository_names != EXPECTED_REPOSITORIES:
        fail("manifest repository names do not match the active stack")
    for entry in manifest["repositories"]:
        component_page = ROOT / entry["architecture_page"]
        component_text = read_text(component_page)
        for required in ("**Role:**", "**Maturity:**", "**Boundary:**", "**Repository:**"):
            if required not in component_text:
                fail(f"{component_page.relative_to(ROOT)} missing {required}")
        if entry["role"] not in component_text:
            fail(f"{component_page.relative_to(ROOT)} role differs from manifest")
        unsupported = set(entry["capabilities"]) - CAPABILITY_LABELS
        if unsupported:
            fail(f"{entry['repository']} uses unsupported capabilities: {sorted(unsupported)}")

    catalog_text = read_text(evidence_catalog)
    readiness_rows = [line for line in readiness_text.splitlines() if line.startswith("| ")]
    if len(readiness_rows) < len(EXPECTED_REPOSITORIES) + 2:
        fail("PRODUCTION-READINESS.md must cover all fourteen repositories")
    for historical in REQUIRED_RSI_MAP_FILES + REQUIRED_LIVE_MUTATION_LADDER_FILES:
        if Path(historical).name not in catalog_text:
            fail(f"evidence catalog missing {historical}")
    if "external beta has not launched" not in catalog_text.lower() and "does not launch an external beta" not in catalog_text.lower():
        fail("evidence catalog must deny external-beta launch")

    for image in REQUIRED_IMAGES:
        path = ROOT / image
        if not path.exists():
            fail(f"missing required image: {image}")
        try:
            ET.parse(path)
        except ET.ParseError as exc:
            fail(f"invalid SVG XML in {image}: {exc}")

    external_beta_image = ROOT / "images" / "external-beta-topology.svg"
    if not external_beta_image.exists():
        fail("missing external-beta topology diagram")
    try:
        ET.parse(external_beta_image)
    except ET.ParseError as exc:
        fail(f"invalid external-beta topology SVG: {exc}")

    try:
        markdown_paths = public_safety_scan_paths(ROOT, suffixes={".md"})
        safety_paths = public_safety_scan_paths(ROOT)
    except OSError as exc:
        fail(f"public-safety scan failed to inspect path metadata: {exc}")
    except ValueError as exc:
        fail(str(exc))

    for md in markdown_paths:
        text = read_text(md)
        for target in markdown_image_targets(text):
            if target.startswith("http://") or target.startswith("https://"):
                continue
            image_path = (md.parent / target).resolve()
            if not image_path.exists():
                fail(f"{md.relative_to(ROOT)} references missing image {target}")

    for path in safety_paths:
        text = path.read_text(errors="ignore")
        for pattern in SAFETY_PATTERNS:
            if re.search(pattern, text):
                fail(f"public-safety pattern {pattern!r} found in {path.relative_to(ROOT)}")

    print("verify_architecture.py: all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
