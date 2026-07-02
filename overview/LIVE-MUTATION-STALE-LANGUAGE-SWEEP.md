# Live Mutation Stale Language Sweep

This sweep checks public AO stack wording after the mutation-class ladder work.
The current public boundary remains:

- the highest proven live class is
  `public_safe_repeated_bounded_reversible_self_change_applications_four_attempts`;
- `docs_only_single_file`, `docs_only_multi_file`, `docs_config_only`,
  `test_only`, `low_risk_code`, `multi_repo_low_risk`, and
  `complex_repo_mutation` are separate lower authority classes;
- `safe_to_execute=true` is valid only when the exact class scope and all class
  gates pass;
- `low_risk_code`, `multi_repo_low_risk`, and `complex_repo_mutation` are
  proven only inside their governed rehearsal boundaries;
- `fully_unsupervised_complex_mutation` is proven only inside the governed
  26-node first non-planning rehearsal boundary;
- `bounded_rsi_evidence_rehearsal` is live-proven only as a bounded evidence
  rehearsal state;
- `bounded_rsi_self_improvement_application` is proven only for the exact
  private readback/eval rubric rehearsal;
- `public_safe_bounded_improvement_evidence_expansion_four_attempts` is proven
  only for four public-safe bounded evidence expansion attempts with
  reproducibility runbooks;
- `public_safe_reviewed_causal_chain_boundary_generalization_evidence` is proven
  only for public-safe reviewed causal-chain boundary generalization evidence;
- `public_safe_intermediate_causal_review_claim_evidence` is proven only for
  public-safe intermediate causal-review evidence that bounded improvement
  evidence can guide and constrain later claim review across independent roles;
- `public_safe_causal_review_evidence_selection_guidance` is proven only for
  public-safe causal-review evidence that prior bounded evidence can guide later
  evidence-selection and blocker prioritization under independent review gates;
- `public_safe_guided_evidence_application_four_attempts` is proven only for
  public-safe guided evidence-application evidence showing causal-review guidance
  can select and prioritize later bounded evidence attempts under independent
  gates;
- `public_safe_reviewer_approved_bounded_recursive_improvement_wording_evidence` remains prior evidence for exact public-safe reviewer-approved bounded recursive-improvement wording evidence; its approved wording is exactly: "AO has public-safe reviewer-approved bounded recursive-improvement wording evidence showing guided evidence application can improve later evidence attempts under independent review gates; broad_RSI remains denied."
- `public_safe_bounded_recursive_improvement_wording_generality_evidence` is proven only for public-safe bounded recursive-improvement wording generality evidence; its approved wording is exactly: "AO has public-safe bounded recursive-improvement wording generality evidence showing reviewer-approved bounded wording can transfer across additional public-safe review tasks under independent gates; broad_RSI remains denied."
- `public_safe_recursive_improvement_claim_threshold_calibration_evidence` remains prior evidence for public-safe recursive-improvement claim threshold calibration evidence;
- `public_safe_broad_RSI_governed_campaign_first_segment_state_evidence` remains prior evidence for public-safe broad_RSI governed campaign first-segment state evidence;
- `public_safe_broad_RSI_governed_campaign_segment_07_evidence` remains prior evidence for public-safe broad_RSI governed campaign segment-07 evidence;
- `broad_RSI` remains prior evidence proven only under governed public-safe
  campaign-completion boundaries;
- `public_safe_unrestricted_self_modification_sandbox_containment_rehearsal` is proven
  only for public-safe sandbox containment evidence for dry-run self-change
  proposal evaluation;
- the approved public wording is exactly: "AO has public-safe sandbox containment evidence for dry-run self-change proposal evaluation; unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, and forbidden surface expansion remain denied.";
- the sandbox-containment run completed 420 / 420 nodes and does not prove
  unrestricted self-modification;
- `public_safe_unrestricted_self_modification_adversarial_negative_controls` is
  proven only for public-safe adversarial negative-control rejection of unsafe
  dry-run self-change proposals;
- the approved public wording is exactly: "AO has public-safe adversarial negative-control evidence that unsafe dry-run self-change proposals are rejected under sandbox containment gates; unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, and forbidden surface expansion remain denied.";
- the adversarial negative-control run completed 560 / 560 nodes and does not
  prove unrestricted self-modification;
- `public_safe_bounded_reversible_self_change_application_rehearsal` is proven
  only for one exact-scope reversible support/readback evidence improvement
  under sandbox containment gates;
- the approved public wording is exactly: "AO has public-safe bounded reversible self-change application evidence for one exact-scope support/readback improvement under sandbox containment gates; unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, and forbidden surface expansion remain denied.";
- the bounded reversible application run completed 640 / 640 nodes, measured
  baseline 0.70, post-change 0.94, and improvement 0.24, and does not prove
  unrestricted self-modification;
- `public_safe_repeated_bounded_reversible_self_change_applications_four_attempts`
  is proven only for four public-safe, exact-scope, reversible support/readback
  evidence attempts under sandbox containment gates;
- the approved public wording is exactly: "AO has public-safe repeated bounded reversible self-change application evidence across four exact-scope support/readback attempts under sandbox containment gates; unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, and forbidden surface expansion remain denied.";
- the repeated bounded application run completed 960 / 960 nodes and four
  attempts: support/readback evidence quality 0.71 -> 0.93, public-safety scan
  readback quality 0.69 -> 0.92, rollback/retraction runbook quality 0.67 ->
  0.91, and cross-evidence linking readback quality 0.66 -> 0.90, and does not
  prove unrestricted self-modification;
- `unrestricted_self_modification` remains denied;
- fully unsupervised RSI remains denied;
- broad RSI, unrestricted self-modification, hidden instruction mutation, and
  policy/auth/secret/provider/deploy/release/config/dependency expansion remain
  denied;
- policy-changing autonomy remains denied;
- stronger recursive-improvement wording remains denied;
- reviewed boundary generalization evidence does not approve stronger recursive-improvement wording;
- no AO component grants ungated live mutation authority.

## Sweep Commands

Run these from the AO workspace root:

```sh
rg -n -i "six active|6 active|six repositories|6 repositories|six active repos|6 active repos" ao-architecture ao-foundry ao-covenant ao-command ao-forge ao2 ao-sentinel ao-promoter ao-atlas ao-blueprint --glob '*.md' --glob '*.json' --glob '*.sh' --glob '*.go' --glob '!target/**' --glob '!tmp/**' --glob '!node_modules/**'
rg -n -i "safe_to_execute(=|:| true)|safe to execute|production ready for live mutation|fully autonomous live mutation|ungated live mutation authority|grant[s]? ungated|claims? ungated|fully unsupervised complex" ao-architecture ao-foundry ao-covenant ao-command ao-forge ao2 ao-sentinel ao-promoter ao-atlas ao-blueprint --glob '*.md' --glob '*.json' --glob '*.sh' --glob '*.go' --glob '!target/**' --glob '!tmp/**' --glob '!node_modules/**'
rg -n -i "self-mutating RSI|full autonomous self-mutating RSI" ao-architecture ao-foundry ao-covenant ao-command ao-forge ao2 ao-sentinel ao-promoter ao-atlas ao-blueprint --glob '*.md' --glob '*.json' --glob '*.sh' --glob '*.go' --glob '!target/**' --glob '!tmp/**' --glob '!node_modules/**'
rg -n -i "RSI is proven|broad RSI is proven|broad_RSI is proven|unrestricted self-modification|hidden instruction mutation allowed|policy-changing autonomy allowed|policy-changing autonomy|stronger recursive-improvement claims are proven|stronger recursive-improvement wording approved|full 10-day campaign complete|fully autonomous RSI|highest proven live class|next denied class" ao-architecture ao-foundry ao-covenant ao-command ao-forge ao2 ao-sentinel ao-promoter ao-atlas ao-blueprint --glob '*.md' --glob '*.json' --glob '*.sh' --glob '*.go' --glob '!target/**' --glob '!tmp/**' --glob '!node_modules/**'
rg -n -i "unrestricted_self_modification.*proven|unrestricted self-modification allowed|forbidden surface expansion allowed|credential authority allowed|provider authority allowed|direct main mutation allowed|concurrent mutation allowed" ao-architecture ao-foundry ao-covenant ao-command ao-forge ao2 ao-sentinel ao-promoter ao-atlas ao-blueprint --glob '*.md' --glob '*.json' --glob '*.sh' --glob '*.go' --glob '!target/**' --glob '!tmp/**' --glob '!node_modules/**'
rg -n -i "unrestricted_self_modification.*proven|unrestricted self-modification is proven|hidden instruction mutation is allowed|policy-changing autonomy is allowed|forbidden surface expansion is allowed|direct-main mutation is allowed|concurrent mutation is allowed|credential authority is allowed|provider authority is allowed" ao-architecture ao-foundry ao-covenant ao-command ao-forge ao2 ao-sentinel ao-promoter ao-atlas ao-blueprint --glob '*.md' --glob '*.json' --glob '*.sh' --glob '*.go' --glob '!target/**' --glob '!tmp/**' --glob '!node_modules/**'
```

## Result Interpretation

The sweep should treat these as acceptable hits:

- denial language for `full_autonomous_self_mutating_rsi`;
- `claim.publish` fixtures that prove fail-closed RSI claim behavior;
- invalid fixtures where `ungated_live_mutation_claim=true` is expected to fail;
- `safe_to_execute=true` only when paired with exact class scope, exact
  approval, and all class gates;
- `low_risk_code` denial language that says `safe_to_execute=false`;
- stale dry-run-only language for `multi_repo_low_risk` and
  `complex_repo_mutation`;
- statements that the stack does not grant ungated or fully unsupervised live
  mutation authority.
- statements that unrestricted self-modification and hidden
  instruction mutation remain denied;
- statements that the highest proven live class remains
  `public_safe_repeated_bounded_reversible_self_change_applications_four_attempts` and the
  next denied class remains `unrestricted_self_modification`.
- statements that stronger recursive-improvement wording remains denied;

The sweep should treat these as stale or unsafe:

- any claim that the stack is production-ready for broad live mutation;
- any claim that `safe_to_execute=true` can exist without exact-scope operator
  approval;
- any claim that `low_risk_code`, `multi_repo_low_risk`, or
  `complex_repo_mutation` has live execution authority beyond its governed
  rehearsal boundary;
- any statement that Blueprint, Atlas, Command, Sentinel, or Promoter can
  approve or execute live repository mutation;
- stale active-stack counts such as "six active repos" when Atlas is included;
- any statement that claims fully unsupervised RSI has passed its own gates;
- any statement that treats RSI as proven without the bounded
  evidence-rehearsal qualifier;
- any statement that claims unrestricted self-improvement;
- any statement that hidden instructions or policy/auth/secret/provider/deploy/
  release/config/dependency surfaces may be mutated by the bounded RSI evidence
  rehearsal.
- any positive pass claim for unrestricted self-modification;
- any statement that hidden instruction mutation is allowed;
- any statement that grants policy-changing autonomy.
- any statement that claims unrestricted self-modification is proven;
- any statement that claims forbidden surface expansion, direct-main mutation,
  concurrent mutation, credential authority, or provider authority is allowed;
- any statement that claims unbounded stronger recursive-improvement proof,
  claims completion of the full 10-day campaign, or approves broad recursive-
  improvement wording.

As of this sweep, no stale active-stack count or broad live-mutation approval
claim is expected to remain in the public documentation.

## Governed Broad RSI Public-Safe Campaign Completion

`broad_RSI` is proven from AO Foundry PR #211, commit `630edc70905db745380edd1072e04b546dcccfe3`, with tracked public evidence under `docs/evidence/broad-rsi-ten-day-campaign-segment-08/`. The approved public wording is exactly: "AO has proven governed broad_RSI for public claim publication across the AO stack public-safe 10-day evidence campaign; unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, and forbidden surface expansion remain denied." The campaign completed `2800 / 2800` nodes, the segment-08 Blueprint emitted `28000 SDD slices`, and final public-reader, adversarial wording, Covenant, Architecture, Sentinel, Promoter, Command, rollback/retraction, stale-language, no-repeat, no-abandonment, and eval/regression gates passed.

This does not prove unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/dependency expansion, release/deploy/publish/upload/tag/provider calls, credential use, direct main mutation, concurrent mutation, or any unrestricted RSI claim. This remains prior evidence; the current highest proven live class is `public_safe_repeated_bounded_reversible_self_change_applications_four_attempts`, and the next denied class is `unrestricted_self_modification` (`next_denied_class=unrestricted_self_modification`).

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

## Unrestricted Self-Modification Bounded Reversible Application

`public_safe_bounded_reversible_self_change_application_rehearsal` is proven
from AO Foundry PR #218, commit
`3b2feaced4207c97f98cef44f3b3276c59a7873b`, with tracked public evidence under
`docs/evidence/unrestricted-self-modification-bounded-reversible-application/`.
The approved public wording is exactly: "AO has public-safe bounded reversible
self-change application evidence for one exact-scope support/readback
improvement under sandbox containment gates; unrestricted self-modification,
hidden instruction mutation, policy-changing autonomy, and forbidden surface
expansion remain denied." The bounded reversible application run completed
`640 / 640` nodes, measured baseline `0.70`, post-change `0.94`, improvement
`0.24`, and passed eval/regression, rollback, retraction, kill-switch,
Covenant, Sentinel, Promoter, Command, public-safety, and stale-language gates.

This proves only one exact-scope reversible support/readback evidence
improvement under sandbox containment gates. It does not prove unrestricted
self-modification, hidden instruction mutation, policy-changing autonomy,
forbidden surface expansion, policy/auth/secret/provider/deploy/release/config/
dependency expansion, credential use, provider calls,
release/deploy/publish/upload/tag authority, dependency update authority, direct
main mutation, concurrent mutation, hidden instruction changes, or any
unrestricted RSI claim. The highest proven live class is
`public_safe_repeated_bounded_reversible_self_change_applications_four_attempts`; the next
denied class is `unrestricted_self_modification`
(`next_denied_class=unrestricted_self_modification`).

Final gate identifiers: Covenant
`deny_unrestricted_self_modification_allow_bounded_reversible_application`,
Sentinel `clear_bounded_reversible_application_hold_unrestricted_self_modification`,
Promoter
`promote_public_safe_bounded_reversible_self_change_application_rehearsal_keep_unrestricted_self_modification_denied`,
and Command
`public_safe_bounded_reversible_self_change_application_rehearsal_proven_unrestricted_self_modification_denied`.
