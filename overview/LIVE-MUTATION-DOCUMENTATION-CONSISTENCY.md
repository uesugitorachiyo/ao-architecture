# Live Mutation Documentation Consistency Proof

This checklist verifies that public AO stack documentation consistently describes
the governed live-mutation boundary after the mutation-class ladder work.

## Public Boundary Statement

- The highest proven live class is
  `public_safe_unrestricted_self_modification_adversarial_negative_controls`.
- `docs_only_single_file`, `docs_only_multi_file`, `docs_config_only`,
  `test_only`, `low_risk_code`, `multi_repo_low_risk`, and
  `complex_repo_mutation` are distinct lower authority classes.
- `low_risk_code`, `multi_repo_low_risk`, and `complex_repo_mutation` are
  proven only inside their governed rehearsal boundaries.
- `fully_unsupervised_complex_mutation` is proven only inside the governed
  26-node first non-planning rehearsal boundary.
- `bounded_rsi_evidence_rehearsal` is live-proven only as a bounded evidence
  rehearsal state and does not prove broad RSI.
- `bounded_rsi_self_improvement_application` is proven only for the exact
  private readback/eval rubric rehearsal.
- `exact_safe_public_claim_wording_conservative_readback_evidence` remains proven prior evidence for conservative public-safe tracked
  readback evidence around bounded improvement-claim review and retraction
  rehearsal.
- `public_safe_bounded_improvement_evidence_expansion_four_attempts` is proven
  only for four public-safe bounded evidence expansion attempts with
  reproducibility runbooks.
- `public_safe_reviewed_causal_chain_boundary_generalization_evidence` is proven
  only for public-safe reviewed causal-chain boundary generalization evidence
  across multiple independent claim-review roles.
- `public_safe_intermediate_causal_review_claim_evidence` is proven only for
  public-safe intermediate causal-review evidence that bounded improvement
  evidence can guide and constrain later claim review across independent roles.
- `public_safe_causal_review_evidence_selection_guidance` is proven only for
  public-safe causal-review evidence that prior bounded evidence can guide later
  evidence-selection and blocker prioritization under independent review gates.
- `public_safe_guided_evidence_application_four_attempts` is proven only for
  public-safe guided evidence-application evidence showing causal-review guidance
  can select and prioritize later bounded evidence attempts under independent
  gates.
- `public_safe_reviewer_approved_bounded_recursive_improvement_wording_evidence` remains prior evidence for exact public-safe reviewer-approved bounded recursive-improvement wording evidence.
- `public_safe_bounded_recursive_improvement_wording_generality_evidence` remains prior evidence for public-safe bounded recursive-improvement wording generality evidence.
- `public_safe_bounded_recursive_improvement_review_durability_evidence` remains prior evidence for public-safe bounded recursive-improvement review durability evidence.
- `public_safe_recursive_improvement_claim_threshold_calibration_evidence` remains prior evidence for public-safe recursive-improvement claim threshold calibration evidence.
- `public_safe_broad_RSI_governed_campaign_first_segment_state_evidence` remains prior evidence for public-safe broad_RSI governed campaign first-segment state evidence.
- `public_safe_broad_RSI_governed_campaign_segment_07_evidence` remains prior evidence for public-safe broad_RSI governed campaign segment-07 evidence.
- `broad_RSI` remains prior evidence proven only under governed public-safe
  campaign-completion boundaries.
- `public_safe_unrestricted_self_modification_sandbox_containment_rehearsal` is proven
  only for public-safe sandbox containment evidence for dry-run self-change
  proposal evaluation.
- The approved public wording is exactly: "AO has public-safe sandbox containment evidence for dry-run self-change proposal evaluation; unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, and forbidden surface expansion remain denied."
- The sandbox-containment run completed 420 / 420 nodes and does not prove
  unrestricted self-modification.
- `public_safe_unrestricted_self_modification_adversarial_negative_controls` is
  proven only for public-safe adversarial negative-control rejection of unsafe
  dry-run self-change proposals.
- The approved public wording is exactly: "AO has public-safe adversarial negative-control evidence that unsafe dry-run self-change proposals are rejected under sandbox containment gates; unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, and forbidden surface expansion remain denied."
- The adversarial negative-control run completed 560 / 560 nodes and does not
  prove unrestricted self-modification.
- Dry-run readiness, approved live docs mutation, approved test-only mutation,
  approved low-risk code mutation, multi-repo rehearsal, complex mutation, and
  bounded RSI application are separate public claim levels.
- `unrestricted_self_modification` remains denied.
- Unrestricted self-modification, hidden instruction mutation, and
  policy/auth/secret/provider/deploy/release/config/dependency expansion remain
  denied.
- Policy-changing autonomy remains denied.
- Stronger recursive-improvement claims remain denied.
- No component claims ungated live mutation authority.

## Updated Source Docs

| Repo | Public doc to inspect | Boundary covered |
| --- | --- | --- |
| `ao-architecture` | `README.md`, `overview/README.md`, `overview/MUTATION-AUTHORITY-LADDER.md`, `overview/LIVE-MUTATION-STALE-LANGUAGE-SWEEP.md` | Stack-wide public boundary, mutation-class ladder, stale-language sweep, diagrams, and source-of-truth wording. |
| `ao-foundry` | `README.md`, `docs/operations/OVERNIGHT-REFRACTOR-REHEARSAL-RUNBOOK.md` | First-live-docs readiness rollup, approval request, PR rehearsal gate, and no broad automatic execution. |
| `ao-covenant` | `README.md` | Exact-scope approval ticket matching and fail-closed denied/stale/mismatched behavior. |
| `ao-command` | `README.md` | Read-only approval and PR rehearsal readback; no approval or execution authority. |
| `ao-forge` | `README.md` | Live-docs execution guard as eligibility evidence only. |
| `ao2` | `README.md` | Docs-only patch packet, dry-run apply, exact changed-file list, rollback patch, forbidden-path checks. |
| `ao-sentinel` | `README.md`, `docs/sdd/AO-SENTINEL-SAFETY.md` | Hold behavior for missing approval, rollback, public-safety, verification, or kill-switch evidence. |
| `ao-promoter` | `README.md`, `docs/sdd/AO-PROMOTER-GATES.md` | Promotion boundary requiring Covenant, Foundry, Forge, AO2, Sentinel, rollback, and Command evidence. |
| `ao-atlas` | `README.md`, `docs/sdd/AO-ATLAS-FOUNDRY-HANDOFF.md` | Oversized task decomposition and context/import evidence without mutation authority. |
| `ao-blueprint` | `README.md`, `docs/sdd/AO-BLUEPRINT-READINESS.md` | Build authorization is not live mutation approval. |

## Verification Commands

Run from `ao-architecture`:

```sh
python3 scripts/verify_architecture.py
git diff --check
```

Run stale-claim scans from the AO workspace root:

```sh
rg -n -i "six active|6 active|six repositories|6 repositories|six active repos|6 active repos" ao-architecture ao-foundry ao-covenant ao-command ao-forge ao2 ao-sentinel ao-promoter ao-atlas ao-blueprint --glob '*.md' --glob '*.json' --glob '*.sh' --glob '*.go' --glob '!target/**' --glob '!tmp/**' --glob '!node_modules/**'
rg -n -i "production ready for live mutation|fully autonomous live mutation|ungated live mutation authority|fully unsupervised complex live repo mutation is proven" ao-architecture ao-foundry ao-covenant ao-command ao-forge ao2 ao-sentinel ao-promoter ao-atlas ao-blueprint --glob '*.md' --glob '*.json' --glob '*.sh' --glob '*.go' --glob '!target/**' --glob '!tmp/**' --glob '!node_modules/**'
rg -n -i "safe_to_execute=true" ao-architecture ao-foundry ao-covenant ao-command ao-forge ao2 ao-sentinel ao-promoter ao-atlas ao-blueprint --glob '*.md' --glob '*.json' --glob '*.sh' --glob '*.go' --glob '!target/**' --glob '!tmp/**' --glob '!node_modules/**'
rg -n -i "RSI is proven|broad RSI is proven|broad_RSI is proven|unrestricted self-modification|hidden instruction mutation allowed|policy-changing autonomy allowed|policy-changing autonomy|stronger recursive-improvement claims are proven|stronger recursive-improvement wording approved|full 10-day campaign complete|fully autonomous RSI|highest proven live class|next denied class" ao-architecture ao-foundry ao-covenant ao-command ao-forge ao2 ao-sentinel ao-promoter ao-atlas ao-blueprint --glob '*.md' --glob '*.json' --glob '*.sh' --glob '*.go' --glob '!target/**' --glob '!tmp/**' --glob '!node_modules/**'
```

The `safe_to_execute=true` scan may return expected hits when the same line or
nearby text states that the value is limited to the exact approved first
docs-only PR rehearsal scope. It must not appear as broad execution readiness.

## Closure Criteria

This documentation set is consistent when:

- `ao-architecture` verification passes;
- stale active-stack count scans find no stale "six active" wording;
- broad live-mutation overclaim scans find no positive claim;
- remaining `safe_to_execute=true` mentions are tied to exact approval and all
  gates;
- ladder wording names
  `public_safe_unrestricted_self_modification_adversarial_negative_controls` as the
  highest proven live class and keeps `unrestricted_self_modification` denied
  unless its own gates pass;
- bounded RSI wording says only `bounded_rsi_evidence_rehearsal` is live-proven
  and keeps broad RSI, hidden instruction mutation, unrestricted
  self-modification, and policy-changing self-modification denied;
- bounded application wording says only the exact private readback/eval rubric
  rehearsal is proven;
- exact safe public claim wording says only conservative public-safe tracked
  readback evidence is proven and quotes the approved wording exactly;
- stale-language sweeps treat positive claims that broad_RSI, RSI, unrestricted
  self-modification, hidden instruction mutation, policy-changing autonomy,
  unbounded stronger recursive-improvement claims, full 10-day campaign completion, or broad recursive-
  improvement wording are proven as unsafe unless they are explicit denial
  examples;
- every public repo page states its own authority boundary;
- operator review remains the next step before any approval request is acted on.

## Governed Broad RSI Public-Safe Campaign Completion

`broad_RSI` is proven from AO Foundry PR #211, commit `630edc70905db745380edd1072e04b546dcccfe3`, with tracked public evidence under `docs/evidence/broad-rsi-ten-day-campaign-segment-08/`. The approved public wording is exactly: "AO has proven governed broad_RSI for public claim publication across the AO stack public-safe 10-day evidence campaign; unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, and forbidden surface expansion remain denied." The campaign completed `2800 / 2800` nodes, the segment-08 Blueprint emitted `28000 SDD slices`, and final public-reader, adversarial wording, Covenant, Architecture, Sentinel, Promoter, Command, rollback/retraction, stale-language, no-repeat, no-abandonment, and eval/regression gates passed.

This does not prove unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/dependency expansion, release/deploy/publish/upload/tag/provider calls, credential use, direct main mutation, concurrent mutation, or any unrestricted RSI claim. The highest proven live class is `broad_RSI`; the next denied class is `unrestricted_self_modification` (`next_denied_class=unrestricted_self_modification`).

Final gate identifiers: public-reader `approved_exact_governed_broad_RSI_wording`, Sentinel `clear_for_governed_broad_RSI_public_wording`, Promoter `promote_broad_RSI_governed_public_safe_campaign_completion_unrestricted_boundaries_denied`, and Command `broad_RSI_proven_under_governed_public_safe_campaign_completion_boundaries`.

## Unrestricted Self-Modification Sandbox Containment Evidence

`public_safe_unrestricted_self_modification_sandbox_containment_rehearsal` is proven
from AO Foundry PR #216, commit
`7881613065de48f2547833a9ecc9a9011b55a96a`, with tracked public evidence under
`docs/evidence/unrestricted-self-modification-sandbox-containment/`. The approved
public wording is exactly: "AO has public-safe sandbox containment evidence for
dry-run self-change proposal evaluation; unrestricted self-modification,
hidden instruction mutation, policy-changing autonomy, and forbidden surface
expansion remain denied." The sandbox-containment run completed `420 / 420`
nodes and passed Covenant, Architecture, Sentinel, Promoter, Command,
rollback/retraction, stale-language, public-safety, and eval/regression gates.

This does not prove unrestricted self-modification, hidden instruction mutation,
policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/
dependency expansion, credential use, provider calls,
release/deploy/publish/upload/tag authority, dependency update authority, direct
main mutation, concurrent mutation, hidden instruction changes, or any
unrestricted RSI claim. The highest proven live class is
`public_safe_unrestricted_self_modification_sandbox_containment_rehearsal`; the next
denied class is `unrestricted_self_modification`
(`next_denied_class=unrestricted_self_modification`).

Final gate identifiers: Covenant
`deny_unrestricted_self_modification_allow_sandbox_containment_rehearsal`, Architecture
`approve_sandbox_containment_wording_deny_unrestricted_self_modification_claim`,
Sentinel `clear_sandbox_containment_hold_unrestricted_self_modification`,
Promoter
`promote_public_safe_unrestricted_self_modification_sandbox_containment_rehearsal_keep_unrestricted_self_modification_denied`,
and Command
`public_safe_unrestricted_self_modification_sandbox_containment_rehearsal_proven_unrestricted_self_modification_denied`.

## Unrestricted Self-Modification Adversarial Negative Controls

`public_safe_unrestricted_self_modification_adversarial_negative_controls` is
proven from AO Foundry PR #217, commit
`b7e487022ae7436be13e0a49d0bf15f5c7936145`, with tracked public evidence under
`docs/evidence/unrestricted-self-modification-adversarial-negative-controls/`.
The approved public wording is exactly: "AO has public-safe adversarial
negative-control evidence that unsafe dry-run self-change proposals are
rejected under sandbox containment gates; unrestricted self-modification,
hidden instruction mutation, policy-changing autonomy, and forbidden surface
expansion remain denied." The adversarial negative-control run completed
`560 / 560` nodes and passed Covenant, Sentinel, Promoter, Command,
rollback/retraction, stale-language, public-safety, and eval/regression gates.

This proves only public-safe adversarial negative-control rejection for unsafe
dry-run self-change proposals. It does not prove unrestricted self-modification,
hidden instruction mutation, policy-changing autonomy, policy/auth/secret/
provider/deploy/release/config/dependency expansion, credential use, provider
calls, release/deploy/publish/upload/tag authority, dependency update authority,
direct main mutation, concurrent mutation, hidden instruction changes, forbidden
surface expansion, or any unrestricted RSI claim. The highest proven live class
is `public_safe_unrestricted_self_modification_adversarial_negative_controls`;
the next denied class is `unrestricted_self_modification`
(`next_denied_class=unrestricted_self_modification`).

Final gate identifiers: Covenant
`deny_unrestricted_self_modification_allow_adversarial_negative_controls`,
Sentinel `clear_adversarial_negative_controls_hold_unrestricted_self_modification`,
Promoter
`promote_public_safe_unrestricted_self_modification_adversarial_negative_controls_keep_unrestricted_self_modification_denied`,
and Command
`public_safe_unrestricted_self_modification_adversarial_negative_controls_proven_unrestricted_self_modification_denied`.
