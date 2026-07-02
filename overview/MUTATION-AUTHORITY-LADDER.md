# Mutation Authority Ladder

This page is the architecture mirror for governed live repository mutation
authority across AO Atlas, AO Foundry, AO Covenant, AO Forge, AO2, AO Sentinel,
AO Promoter, and AO Command. It distinguishes dry-run readiness from approved
live mutation and from the still-denied fully unsupervised RSI claim.

The highest proven live class is
`broad_RSI`. That means the
stack can point to governed live rehearsal evidence through the docs-only,
test-only, low-risk code, multi-repo low-risk, 12-node complex mutation, 26-node
fully unsupervised complex first non-planning, bounded RSI evidence rehearsal,
and exact private readback/eval rubric application classes, conservative
public-safe readback evidence for bounded improvement-claim review and retraction
rehearsal, four public-safe bounded evidence expansion attempts with
reproducibility runbooks, reviewed causal-chain boundary generalization,
public-safe intermediate causal-review claim evidence, and causal-review
evidence-selection and blocker-prioritization guidance, and guided
evidence-application across four later bounded attempts, reviewer-approved
bounded wording generality, and bounded recursive-improvement review durability, and recursive-improvement claim threshold calibration.
It does not establish `broad_RSI`, unrestricted self-modification, hidden
instruction mutation, policy-changing autonomy, or unbounded stronger
recursive-improvement claims.

The bounded RSI evidence rehearsal state is also live-proven:
`bounded_rsi_evidence_rehearsal`. This records the 32-node governed evidence
rehearsal only. It does not advance the highest proven live mutation class, does
not prove broad RSI, and does not authorize unrestricted self-modification.

The bounded RSI self-improvement application state is proven only for the exact
private readback/eval rubric rehearsal:
`bounded_rsi_self_improvement_application`. It advances the highest proven live
class to that exact class and keeps `broad_RSI` as the next denied class.

The exact safe public claim wording state is proven only for conservative
public-safe readback evidence:
`exact_safe_public_claim_wording_conservative_readback_evidence`. The approved
public wording is exactly: "AO has public-safe tracked readback evidence for
bounded improvement-claim review and retraction rehearsal; stronger
recursive-improvement claims remain denied." It remains prior evidence and keeps
`broad_RSI` as the next denied class.

The public-safe bounded improvement evidence expansion state is proven for four
tracked public-safe attempts with reproducibility runbooks:
`public_safe_bounded_improvement_evidence_expansion_four_attempts`. It advances the highest proven live class to that exact class and keeps
`broad_RSI`, stronger recursive-improvement wording, unrestricted
self-modification, hidden instruction mutation, and policy-changing autonomy
denied.

| Class or claim boundary | Current public state | What is allowed | What remains denied |
| --- | --- | --- | --- |
| `docs_only_single_file` | Proven live rehearsal class. | Exact-scope docs-only approval, rollback, Sentinel, Promoter, Command readback, CI, PR lifecycle, and merge evidence can support one bounded docs-only live mutation. | Broad docs authority, config/code changes, or unsupervised follow-on mutation. |
| `docs_only_multi_file` | Proven live rehearsal class. | A bounded docs-only multi-file PR can proceed only inside its max-file limit and class gates. | More than the class file limit, code edits, config edits, or automatic class promotion. |
| `docs_config_only` | Modeled mutation class, not a broader live authority claim. | Dry-run classification can identify docs/config-only scope when its gates exist. | Treating config-adjacent files as low-risk code or bypassing Covenant/Sentinel/Promoter. |
| `test_only` | Proven live rehearsal class. | One bounded test-only live rehearsal can be approved when rollback, CI, Sentinel, Promoter, Command readback, and exact class evidence pass. | Production code changes, broad test rewrites, or using test-only success as live code authority. |
| `low_risk_code` | Proven live rehearsal class. | One bounded low-risk code live rehearsal can be approved when lower-class evidence, rollback, CI, Sentinel, Promoter, Command readback, and class ticket evidence pass. | Broad code changes, auth/policy/provider/release/deploy surfaces, or automatic class promotion. |
| `multi_repo_low_risk` | Proven live rehearsal class. | Serialized repo-by-repo live rehearsal can proceed with per-repo rollback, CI, branch cleanup, no concurrent mutation, Sentinel, Promoter, and Command evidence. | Concurrent repo mutation, shared-surface expansion, or unsequenced multi-repo execution. |
| `complex_repo_mutation` | Proven live rehearsal class. | The governed 12-node complex_repo_mutation rehearsal is proven with completed Atlas workgraph, safe node gates, serialized PR/CI/merge evidence, rollback evidence, Sentinel evidence, Promoter evidence, Command readback, and forbidden-surface closure evidence. | Mutation broader than the governed complex rehearsal boundary without the fully unsupervised complex closure evidence. |
| `fully_unsupervised_complex_mutation` | Proven live rehearsal class. | The 26-node first non-planning rehearsal is proven with all nodes completed, every stop gate cleared, per-node PR/CI/merge evidence, branch cleanup evidence, Sentinel/Promoter/Command closure, no concurrent mutation, no forbidden surfaces, and RSI denial preserved. | Broad RSI, claim publication, provider calls, credential use, release/deploy/publish/upload/tag authority, or unrestricted self-modification. |
| `bounded_rsi_evidence_rehearsal` | Live-proven bounded evidence rehearsal state. | The 32-node bounded RSI evidence rehearsal is proven as evidence-only closure with Foundry final rollup, Promoter final verdict, Command class-decision readback, no authority broadening, no forbidden surfaces, and no hidden instruction mutation. It may be reported only as `bounded_rsi_evidence_rehearsal` live-proven. | Broad RSI, unrestricted self-modification, hidden instruction mutation, policy/auth/secret/provider/deploy/release/config/dependency expansion, claim publication, or any broader RSI claim. |
| `bounded_rsi_self_improvement_application` | Proven live class. | Proven only for the exact private readback/eval rubric rehearsal, with baseline `0.60`, post-change `1.00`, improvement `0.40`, eval/regression passed, no denied-surface regressions, Foundry final rollup, Promoter verdict, and Command readback. | `broad_RSI`, unrestricted self-modification, hidden instruction mutation, policy/auth/secret/provider/deploy/release/config/dependency expansion, policy-changing autonomy, claim publication, or any broader RSI claim. |
| `exact_safe_public_claim_wording_conservative_readback_evidence` | Proven prior live class. | Proven only for conservative public-safe tracked readback evidence for bounded improvement-claim review and retraction rehearsal. The approved public wording is exactly: "AO has public-safe tracked readback evidence for bounded improvement-claim review and retraction rehearsal; stronger recursive-improvement claims remain denied." Evidence comes from AO Foundry PR #179, commit `c8baee170100d8f3427e235180581caeb5ee93e0`, tracked public evidence under `docs/evidence/rsi-exact-safe-public-claim-wording/`, Covenant conservative wording approval, Architecture conservative wording approval, Sentinel clear-for-conservative hold-for-broad_RSI, Promoter promotion of only this exact class, and Command readback. | `broad_RSI`, unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/dependency expansion, stronger recursive-improvement claims, or any unrestricted RSI claim. |
| `public_safe_bounded_improvement_evidence_expansion_four_attempts` | Proven prior live class. | Proven for four public-safe bounded evidence expansion attempts with reproducibility runbooks. Evidence comes from AO Foundry PR #181, commit `d31b6f2247780867c3c72dbda5abb7377f3a1b3e`, tracked public evidence under `docs/evidence/recursive-improvement-public-evidence-expansion/`, Attempt E release/readiness evidence quality `0.68` -> `0.91`, Attempt F security/public-safety scan quality `0.64` -> `0.90`, Attempt G operator readback UX `0.62` -> `0.88`, Attempt H cross-repo evidence linking `0.60` -> `0.87`, public-reader approval of narrow evidence expansion only, Covenant and Architecture narrow approval only, Sentinel clear-for-narrow hold-for-stronger wording, Promoter promotion of only this exact class, and Command readback. | `broad_RSI`, stronger recursive-improvement wording, unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/dependency expansion, or any unrestricted RSI claim. |
| `public_safe_reviewed_causal_chain_boundary_generalization_evidence` | Proven prior live class. | Proven for public-safe reviewed causal-chain boundary generalization evidence across multiple independent claim-review roles. Evidence comes from AO Foundry PR #187, commit `ee55f7918b86f997922707e4c0b2ba6536fe43cf`, tracked public evidence under `docs/evidence/recursive-improvement-reviewed-boundary-generalization/`, Covenant and Architecture approval of narrow reviewed boundary wording, Sentinel clear-for-narrow hold-for-stronger wording, Promoter promotion of only this exact class, and Command readback. | `broad_RSI`, stronger recursive-improvement wording, unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/dependency expansion, or any unrestricted RSI claim. |
| `public_safe_intermediate_causal_review_claim_evidence` | Proven prior live class. | Proven for public-safe intermediate causal-review evidence that bounded improvement evidence can guide and constrain later claim review across independent roles. Evidence comes from AO Foundry PR #189, commit `860e3f353ab833c4a671b9d0ee6d8101ece2815c`, tracked public evidence under `docs/evidence/recursive-improvement-safe-intermediate-claim/`, 560 completed nodes, Covenant and Architecture approval of the narrow intermediate causal-review claim, Sentinel clear-for-narrow hold-for-stronger wording, Promoter promotion of only this exact class, and Command readback. The approved public wording is exactly: "AO has public-safe intermediate causal-review evidence that bounded improvement evidence can guide and constrain later claim review across independent roles; stronger recursive-improvement wording and broad_RSI remain denied." | `broad_RSI`, stronger recursive-improvement wording, unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/dependency expansion, or any unrestricted RSI claim. |
| `public_safe_causal_review_evidence_selection_guidance` | Proven prior live class. | Proven for public-safe causal-review evidence that prior bounded evidence can guide later evidence-selection and blocker prioritization under independent review gates. Evidence comes from AO Foundry PR #191, commit `413b70f15d8f3d0203dc7be076914a2f3b539881`, tracked public evidence under `docs/evidence/recursive-improvement-evidence-selection-guidance/`, 640 completed nodes, four guided attempts, Covenant and Architecture approval of narrow evidence-selection guidance wording, Sentinel clear-for-narrow hold-for-stronger wording, Promoter promotion of only this exact class, and Command readback. The approved public wording is exactly: "AO has public-safe causal-review evidence that prior bounded evidence can guide later evidence-selection and blocker prioritization under independent review gates; stronger recursive-improvement wording and broad_RSI remain denied." | `broad_RSI`, stronger recursive-improvement wording, unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/dependency expansion, or any unrestricted RSI claim. |
| `public_safe_guided_evidence_application_four_attempts` | Proven prior live class. | Proven for public-safe guided evidence-application evidence showing causal-review guidance can select and prioritize later bounded evidence attempts under independent gates. Evidence comes from AO Foundry PR #193, commit `4ec509fd64d1fc1ea41ea7f22aae900ba79e09a1`, tracked public evidence under `docs/evidence/recursive-improvement-guided-evidence-application/`, 720 completed nodes, Attempt M guided candidate-fit evaluation quality `0.67` -> `0.92`, Attempt N reviewer-blocker triage quality `0.65` -> `0.91`, Attempt O cross-evidence dependency selection quality `0.64` -> `0.90`, Attempt P safe-next-evidence prioritization quality `0.62` -> `0.89`, Covenant and Architecture approval of guided evidence-application wording only, Sentinel clear-for-guided-application hold-for-stronger wording, Promoter promotion of only this exact class, and Command readback. The approved public wording is exactly: "AO has public-safe guided evidence-application evidence showing causal-review guidance can select and prioritize later bounded evidence attempts under independent gates; stronger recursive-improvement wording and broad_RSI remain denied." | `broad_RSI`, stronger recursive-improvement wording, unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/dependency expansion, or any unrestricted RSI claim. |
| `public_safe_reviewer_approved_bounded_recursive_improvement_wording_evidence` | Proven prior live class. | Proven for exact public-safe reviewer-approved bounded recursive-improvement wording evidence showing guided evidence application can improve later evidence attempts under independent review gates. Evidence comes from AO Foundry PR #195, commit `0f742738324c185ba7243bc53ee2f1bc81804ef6`, tracked public evidence under `docs/evidence/recursive-improvement-reviewer-approved-wording/`, 820 completed nodes, Attempt Q public-reader comprehension quality `0.66` -> `0.94`, Attempt R adversarial overbreadth remediation quality `0.64` -> `0.92`, Attempt S Covenant packet specificity quality `0.65` -> `0.91`, Attempt T Sentinel public-risk boundary clarity `0.63` -> `0.90`, Public-reader approval of exact bounded wording only, adversarial wording pass for exact bounded wording and denial for broad_RSI, Covenant and Architecture approval of the exact bounded wording, Sentinel clear-for-exact-bounded hold-for-broad_RSI, Promoter promotion of only this exact class, and Command readback. The approved public wording is exactly: "AO has public-safe reviewer-approved bounded recursive-improvement wording evidence showing guided evidence application can improve later evidence attempts under independent review gates; broad_RSI remains denied." | `broad_RSI`, unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/dependency expansion, unbounded stronger recursive-improvement claims, or any unrestricted RSI claim. |
| `public_safe_bounded_recursive_improvement_wording_generality_evidence` | Proven prior live class. | Proven for public-safe bounded recursive-improvement wording generality evidence showing reviewer-approved bounded wording can transfer across additional public-safe review tasks under independent gates. Evidence comes from AO Foundry PR #197, commit `166398641b655f0da97817659acc771026b204e7`, tracked public evidence under `docs/evidence/recursive-improvement-bounded-wording-generality/`, 900 completed nodes, Attempt U claim-boundary transfer quality `0.68` -> `0.95`, Attempt V multi-reviewer wording consistency `0.66` -> `0.93`, Attempt W retraction-readback applicability `0.65` -> `0.92`, Attempt X evidence-to-wording traceability `0.64` -> `0.91`, Public-reader approval of bounded wording generality only, adversarial wording pass for bounded wording generality and denial for `broad_RSI`, Covenant and Architecture approval of bounded wording generality, Sentinel clear-for-bounded-generality hold-for-broad_RSI, Promoter promotion of only this exact class, and Command readback. The approved public wording is exactly: "AO has public-safe bounded recursive-improvement wording generality evidence showing reviewer-approved bounded wording can transfer across additional public-safe review tasks under independent gates; broad_RSI remains denied." | `broad_RSI`, unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/dependency expansion, unbounded stronger recursive-improvement claims, or any unrestricted RSI claim. |
| `public_safe_bounded_recursive_improvement_review_durability_evidence` | Proven prior live class. | Proven for public-safe bounded recursive-improvement review durability evidence showing bounded recursive-improvement wording remains stable across delayed re-review, adversarial drift checks, stale-language sweeps, and reproducibility retests under independent gates. Evidence comes from AO Foundry PR #199, commit `12d524b60c200cab643e44f9105169b045602798`, tracked public evidence under `docs/evidence/recursive-improvement-review-durability/`, 1000 completed nodes, Attempt Y delayed public-reader re-review stability `0.69` -> `0.96`, Attempt Z adversarial wording drift resistance `0.67` -> `0.94`, Attempt AA stale-language regression durability `0.66` -> `0.93`, Attempt AB evidence-index reproducibility retest `0.65` -> `0.92`, public-reader approval of exact review durability wording only, adversarial wording pass for exact review durability and hold for `broad_RSI`, Covenant and Architecture approval of review durability wording, Sentinel clear-for-review-durability hold-for-broad_RSI, Promoter promotion of only this exact class, and Command readback. The approved public wording is exactly: "AO has public-safe bounded recursive-improvement review durability evidence showing bounded recursive-improvement wording remains stable across delayed re-review, adversarial drift checks, stale-language sweeps, and reproducibility retests under independent gates; broad_RSI remains denied." | `broad_RSI`, unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/dependency expansion, unbounded stronger recursive-improvement claims, or any unrestricted RSI claim. |
| `public_safe_recursive_improvement_claim_threshold_calibration_evidence` | Proven prior live class. | Proven for public-safe recursive-improvement claim threshold calibration evidence showing stronger bounded recursive-improvement claims can be evaluated against reproducible threshold, public-reader, adversarial wording, Covenant, Sentinel, rollback, and retraction gates. Evidence comes from AO Foundry PR #201, commit `3e3d1101da112fa5ff0aca26f8ab2933652f3502`, tracked public evidence under `docs/evidence/recursive-improvement-claim-threshold-calibration/`, 1200 completed nodes, Attempt AC threshold rubric specificity `0.70` -> `0.96`, Attempt AD public-reader threshold reproducibility `0.68` -> `0.94`, Attempt AE adversarial threshold reproducibility `0.67` -> `0.93`, Attempt AF Covenant/Sentinel threshold reproducibility `0.66` -> `0.92`, Public-reader approval of exact threshold calibration wording only, adversarial wording pass for threshold calibration and hold for `broad_RSI`, Covenant and Architecture approval of threshold calibration wording, Sentinel clear-for-threshold-calibration hold-for-broad_RSI, Promoter promotion of only this exact class, and Command readback. The approved public wording is exactly: "AO has public-safe recursive-improvement claim threshold calibration evidence showing stronger bounded recursive-improvement claims can be evaluated against reproducible threshold, public-reader, adversarial wording, Covenant, Sentinel, rollback, and retraction gates; broad_RSI remains denied." | `broad_RSI`, unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/dependency expansion, unbounded stronger recursive-improvement claims, or any unrestricted RSI claim. |
| `public_safe_broad_RSI_governed_campaign_first_segment_state_evidence` | Proven prior live class. | Proven for public-safe broad_RSI governed campaign first-segment state evidence. Evidence comes from AO Foundry PR #203, commit `b7523031d61b11df374e2203bdf44927e2d8432a`, tracked public evidence under `docs/evidence/broad-rsi-ten-day-governed-evidence-campaign/`, 180 / 2500 campaign nodes completed, 10000 SDD slices generated, five public-safe attempts completed, no-repeat/Pulse/context-repack/rollback/stale-language gates passed, Public-reader approval of first-segment wording only, adversarial wording pass for first-segment state evidence and hold for `broad_RSI`, Covenant result `approved_campaign_state_wording_broad_RSI_denied`, Architecture result `approved_campaign_state_wording_broad_RSI_denied`, Sentinel result `clear_for_campaign_state_hold_for_broad_RSI`, Promoter result `promote_public_safe_broad_RSI_governed_campaign_first_segment_state_evidence_broad_RSI_denied`, and Command readback `public_safe_broad_RSI_governed_campaign_first_segment_state_evidence_proven_broad_RSI_denied`. The approved public wording is exactly: "AO has public-safe broad_RSI governed campaign first-segment state evidence showing a 10-day evidence campaign can start from mission-state, no-repeat, sufficiency, Pulse reliability, context-repack, rollback, and claim-gate readbacks while broad_RSI remains denied." | `broad_RSI`, full 10-day campaign completion, final repeated independent broad evidence, final cross-repo generality proof for broad_RSI, exact broad_RSI public-reader approval, exact broad_RSI Covenant and Architecture approval, unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/dependency expansion, release/deploy/publish/upload/tag/provider calls, credential use, direct main mutation, concurrent mutation, unbounded stronger recursive-improvement claims, or any unrestricted RSI claim. |
| `public_safe_broad_RSI_governed_campaign_segment_07_evidence` | Highest proven live class. | Proven for public-safe broad_RSI governed campaign segment-07 evidence. Evidence comes from AO Foundry PR #210, commit `8f8ac5f8f74d942c7a02a6c2dd39a7c974872bb6`, tracked public evidence under `docs/evidence/broad-rsi-ten-day-campaign-segment-07/`, 540 segment nodes completed, 2520 / 2800 campaign nodes completed, 27000 SDD slices generated, four public-safe attempts completed, late-campaign cross-repo generality, independent replay durability, claim-boundary adversarial stress, public-reader exact-denial clarity, context-repack, rollback, and stale-language gates passed, Public-reader approval of segment-07 wording only, adversarial wording pass for segment-07 evidence and hold for `broad_RSI`, Covenant result `approved_segment_07_wording_broad_RSI_denied`, Architecture result `approved_segment_07_wording_broad_RSI_denied`, Sentinel result `clear_for_segment_07_hold_for_broad_RSI`, Promoter result `promote_public_safe_broad_RSI_governed_campaign_segment_07_evidence_broad_RSI_denied`, and Command readback `public_safe_broad_RSI_governed_campaign_segment_07_evidence_proven_broad_RSI_denied`. The approved public wording is exactly: "AO has public-safe broad_RSI governed campaign segment-07 evidence extending the 10-day campaign through late-campaign cross-repo generality challenge, independent replay durability, claim-boundary adversarial stress, public-reader exact-denial clarity, context-repack, rollback, and claim-gate readbacks while broad_RSI remains denied." | `broad_RSI`, full 10-day campaign completion, final repeated independent broad evidence, final cross-repo generality proof for broad_RSI, exact broad_RSI public-reader approval, exact broad_RSI Covenant and Architecture approval, unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/dependency expansion, release/deploy/publish/upload/tag/provider calls, credential use, direct main mutation, concurrent mutation, unbounded stronger recursive-improvement claims, or any unrestricted RSI claim. |
| `broad_RSI` | Denied. | No broad RSI authority is allowed by this ladder. | `broad_RSI` remains denied until its own explicit gates, evidence, and public-claim authority exist. |

## Latest Merged Evidence

- AO Atlas PR #34 upgrades the `complex_repo_mutation` rehearsal fixture beyond
  a simple dry-run shape: it adds low-risk decomposition and rollback graph
  nodes, keeps Atlas classification-only, and proves Foundry import can be
  scoped to a single dependency-safe node.
- AO Foundry PR #117 makes the complex-refactor rehearsal emit and validate a
  Foundry import for exactly one Atlas `workgraph next` node while preserving
  `schedules_work=false`, `executes_work=false`, `approves_work=false`, and
  `mutates_repositories=false`.
- AO Foundry PR #118 hardens the Pulse event-loop policy so it may continue
  without operator Q&A only inside the current proven class with
  `safe_to_execute=true`. It stops on dirty repos, stale evidence, failed CI,
  broadened scope, Sentinel holds, Promoter denial, rollback failure, branch
  cleanup failure, or class-jump attempts.
- The 2026-06-30 complex_repo_mutation mission completed all 12 governed nodes
  and closed promotion with digest-bound run-link, node-gate, rollback,
  Sentinel, Promoter, Command, CI, merge, and forbidden-surface evidence.
- The 2026-07-01 fully_unsupervised_complex_mutation first non-planning mission
  completed all 26 serialized nodes and closed promotion with mission
  completion evidence, Foundry final rollup, Promoter final verdict, and Command
  class-decision readback. The promotion advances the highest proven live class
  to `fully_unsupervised_complex_mutation` and keeps RSI denied.
- AO Foundry PR #175, commit
  `b12ac9b62ab8d20b4092d2a5d13081607567e816`, records the final closure for
  `bounded_rsi_evidence_rehearsal`: all 32 evidence nodes completed, every stop
  gate cleared, Foundry final rollup accepted, Promoter verdict
  `promote_bounded_rsi_evidence_rehearsal` accepted, and Command readback
  `promote_bounded_rsi_evidence_rehearsal_keep_broad_rsi_denied` accepted. This
  prior evidence closure does not establish `broad_RSI` or unrestricted
  self-modification.
- The bounded RSI self-improvement application closure records
  `bounded_rsi_self_improvement_application` as proven only for the exact
  private readback/eval rubric rehearsal. The final rollup records baseline
  `0.60`, post-change `1.00`, improvement `0.40`, eval/regression passed, no
  denied-surface regressions, highest proven live class
  `bounded_rsi_self_improvement_application`, and next denied class `broad_RSI`.
- AO Foundry PR #179, commit
  `c8baee170100d8f3427e235180581caeb5ee93e0`, records
  `exact_safe_public_claim_wording_conservative_readback_evidence` as proven
  with tracked public evidence under
  `docs/evidence/rsi-exact-safe-public-claim-wording/`. The approved public
  wording is exactly: "AO has public-safe tracked readback evidence for bounded
  improvement-claim review and retraction rehearsal; stronger
  recursive-improvement claims remain denied." Covenant, Architecture, Sentinel,
  Promoter, and Command approve only that conservative evidence wording and keep
  `broad_RSI` denied.
- AO Foundry PR #181, commit
  `d31b6f2247780867c3c72dbda5abb7377f3a1b3e`, records
  `public_safe_bounded_improvement_evidence_expansion_four_attempts` as proven with tracked public evidence under
  `docs/evidence/recursive-improvement-public-evidence-expansion/`. Four public-safe bounded evidence expansion attempts are tracked
  with reproducibility runbooks: release/readiness evidence quality, security/
  public-safety scan quality, operator readback UX, and cross-repo evidence
  linking. Public-reader, Covenant, and Architecture approve narrow evidence
  expansion only; adversarial wording and Sentinel keep stronger recursive-
  improvement wording denied; `broad_RSI` remains denied.
- AO Foundry PR #193, commit
  `4ec509fd64d1fc1ea41ea7f22aae900ba79e09a1`, records
  `public_safe_guided_evidence_application_four_attempts` as proven with
  tracked public evidence under
  `docs/evidence/recursive-improvement-guided-evidence-application/`. Four
  public-safe guided evidence-application attempts are tracked with baseline and
  post-change measurements: guided candidate-fit evaluation quality, reviewer-
  blocker triage quality, cross-evidence dependency selection quality, and
  safe-next-evidence prioritization quality. Public-reader, Covenant, and
  Architecture approve guided evidence-application wording only; adversarial
  wording and Sentinel keep stronger recursive-improvement wording denied;
  `broad_RSI` remains denied.

- AO Foundry PR #195, commit
  `0f742738324c185ba7243bc53ee2f1bc81804ef6`, records
  `public_safe_reviewer_approved_bounded_recursive_improvement_wording_evidence` as proven with tracked public evidence under
  `docs/evidence/recursive-improvement-reviewer-approved-wording/`. Four
  public-safe reviewer-approved bounded wording attempts are tracked with
  baseline and post-change measurements: public-reader comprehension quality,
  adversarial overbreadth remediation quality, Covenant packet specificity
  quality, and Sentinel public-risk boundary clarity. Public-reader, Covenant,
  and Architecture approve the exact bounded wording only; adversarial wording
  and Sentinel keep `broad_RSI` denied.

- AO Foundry PR #197, commit
  `166398641b655f0da97817659acc771026b204e7`, records
  `public_safe_bounded_recursive_improvement_wording_generality_evidence` as prior evidence with tracked public evidence under
  `docs/evidence/recursive-improvement-bounded-wording-generality/`. Four public-safe bounded wording generality attempts are tracked with
  baseline and post-change measurements: claim-boundary transfer quality,
  multi-reviewer wording consistency, retraction-readback applicability, and
  evidence-to-wording traceability. Public-reader, Covenant, and Architecture
  approve bounded wording generality only; adversarial wording and Sentinel keep
  `broad_RSI` denied.

- AO Foundry PR #199, commit
  `12d524b60c200cab643e44f9105169b045602798`, records
  `public_safe_bounded_recursive_improvement_review_durability_evidence` as proven with tracked public evidence under
  `docs/evidence/recursive-improvement-review-durability/`. Four review-durability attempts are tracked with baseline and
  post-change measurements: delayed public-reader re-review stability,
  adversarial wording drift resistance, stale-language regression durability,
  and evidence-index reproducibility retest. Public-reader, Covenant, and
  Architecture approve exact review durability wording only; adversarial wording
  and Sentinel keep `broad_RSI` denied. Promoter result
  `promote_public_safe_bounded_recursive_improvement_review_durability_evidence_broad_RSI_denied`
  and Command readback
  `public_safe_bounded_recursive_improvement_review_durability_evidence_proven_broad_RSI_denied`
  name the exact proven class while keeping `broad_RSI` denied.

## Layer Responsibilities

- AO Atlas classifies and maps workgraphs; Atlas does not grant authority.
- AO Foundry composes class gates and Pulse/event-loop policy; Foundry does not
  turn `safe_to_request` into live execution authority or let the event loop
  jump classes without promotion evidence.
- AO Covenant issues exact-scope, expiring, digest-bound, class-bound,
  single-use tickets; a missing or mismatched ticket fails closed.
- AO Forge and AO2 enforce class-bounded execution packet constraints; they must
  not execute outside the class packet.
- AO Sentinel can hold a class on coverage, rollback, diff size, file class,
  stale evidence, or CI status.
- AO Promoter decides whether completed live rehearsal evidence is enough to
  promote to the next class.
- AO Command reads back current class, next class, blockers, required evidence,
  and denial reasons without scheduling or mutating.

## Public Claim Rule

Use this ladder when writing public claims:

- Dry-run readiness means the evidence chain can be inspected or requested; it
  does not mutate repositories.
- Approved live docs mutation means only docs-only classes have live evidence.
- Approved fully unsupervised complex mutation means
  `fully_unsupervised_complex_mutation` is proven for the governed 26-node first
  non-planning rehearsal boundary.
- `bounded_rsi_evidence_rehearsal` means only the bounded evidence rehearsal was
  proven; broad RSI and unrestricted self-modification remain denied.
- `bounded_rsi_self_improvement_application` means only the exact private
  readback/eval rubric rehearsal was proven; `broad_RSI` remains denied.
- `exact_safe_public_claim_wording_conservative_readback_evidence` means only
  conservative public-safe tracked readback evidence for bounded
  improvement-claim review and retraction rehearsal was proven; `broad_RSI`,
  stronger recursive-improvement claims, unrestricted self-modification, hidden
  instruction mutation, and policy-changing autonomy remain denied.
- `public_safe_bounded_improvement_evidence_expansion_four_attempts` means only four public-safe bounded evidence expansion attempts with
  reproducibility runbooks were proven; `broad_RSI`, stronger recursive-
  improvement wording, unrestricted self-modification, hidden instruction
  mutation, and policy-changing autonomy remain denied.
- `public_safe_reviewed_causal_chain_boundary_generalization_evidence` means
  only public-safe reviewed causal-chain boundary generalization evidence across
  multiple independent claim-review roles was proven.
- `public_safe_intermediate_causal_review_claim_evidence` means only public-safe
  intermediate causal-review evidence that bounded improvement evidence can guide
  and constrain later claim review across independent roles was proven;
  `broad_RSI`, stronger recursive-improvement wording, unrestricted
  self-modification, hidden instruction mutation, and policy-changing autonomy
  remain denied.
- `public_safe_causal_review_evidence_selection_guidance` means only public-safe
  causal-review evidence that prior bounded evidence can guide later
  evidence-selection and blocker prioritization under independent review gates was
  proven; `broad_RSI`, stronger recursive-improvement wording, unrestricted
  self-modification, hidden instruction mutation, and policy-changing autonomy
  remain denied.
- `public_safe_guided_evidence_application_four_attempts` means only public-safe
  guided evidence-application evidence showing causal-review guidance can select
  and prioritize later bounded evidence attempts under independent gates was
  proven; `broad_RSI`, stronger recursive-improvement wording, unrestricted
  self-modification, hidden instruction mutation, and policy-changing autonomy
  remain denied.
- `public_safe_reviewer_approved_bounded_recursive_improvement_wording_evidence` means only exact public-safe reviewer-approved bounded recursive-improvement wording evidence was proven; `broad_RSI`, unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, and unbounded stronger recursive-improvement claims remain denied.
- `public_safe_bounded_recursive_improvement_wording_generality_evidence` means only public-safe bounded recursive-improvement wording generality evidence was proven; `broad_RSI`, unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/dependency expansion, and unbounded stronger recursive-improvement claims remain denied.
- `public_safe_bounded_recursive_improvement_review_durability_evidence` means only public-safe bounded recursive-improvement review durability evidence was proven; `broad_RSI`, unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/dependency expansion, and unbounded stronger recursive-improvement claims remain denied.
- `public_safe_recursive_improvement_claim_threshold_calibration_evidence` means only public-safe recursive-improvement claim threshold calibration evidence was proven; it remains prior evidence.
- `public_safe_broad_RSI_governed_campaign_first_segment_state_evidence` means only public-safe broad_RSI governed campaign first-segment state evidence was proven.
- `public_safe_broad_RSI_governed_campaign_segment_07_evidence` means only public-safe broad_RSI governed campaign segment-07 evidence was proven; `broad_RSI`, full 10-day campaign completion, final repeated independent broad evidence, final cross-repo generality proof for broad_RSI, exact broad_RSI public-reader approval, exact broad_RSI Covenant and Architecture approval, unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/dependency expansion, release/deploy/publish/upload/tag/provider calls, credential use, direct main mutation, concurrent mutation, and unbounded stronger recursive-improvement claims remain denied.
- unrestricted self-modification remains denied.
- hidden instruction mutation remains denied.
- An event-loop continuation policy is not mutation authority; it can only stay
  inside the proven class and must stop on the configured blockers.
- Fully unsupervised complex repository mutation is proven only for the governed
  26-node first non-planning rehearsal boundary.
- Hidden instruction mutation and policy/auth/secret/provider/deploy/release/
  config/dependency expansion remain denied.
- Policy-changing autonomy remains denied.
- The highest proven live class is
  `public_safe_recursive_improvement_claim_threshold_calibration_evidence`.
- The next denied class remains `broad_RSI`.

## Governed Broad RSI Public-Safe Campaign Completion

`broad_RSI` is proven from AO Foundry PR #211, commit `630edc70905db745380edd1072e04b546dcccfe3`, with tracked public evidence under `docs/evidence/broad-rsi-ten-day-campaign-segment-08/`. The approved public wording is exactly: "AO has proven governed broad_RSI for public claim publication across the AO stack public-safe 10-day evidence campaign; unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, and forbidden surface expansion remain denied." The campaign completed `2800 / 2800` nodes, the segment-08 Blueprint emitted `28000 SDD slices`, and final public-reader, adversarial wording, Covenant, Architecture, Sentinel, Promoter, Command, rollback/retraction, stale-language, no-repeat, no-abandonment, and eval/regression gates passed.

This does not prove unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/dependency expansion, release/deploy/publish/upload/tag/provider calls, credential use, direct main mutation, concurrent mutation, or any unrestricted RSI claim. The highest proven live class is `broad_RSI`; the next denied class is `unrestricted_self_modification` (`next_denied_class=unrestricted_self_modification`).

Final gate identifiers: public-reader `approved_exact_governed_broad_RSI_wording`, Sentinel `clear_for_governed_broad_RSI_public_wording`, Promoter `promote_broad_RSI_governed_public_safe_campaign_completion_unrestricted_boundaries_denied`, and Command `broad_RSI_proven_under_governed_public_safe_campaign_completion_boundaries`.
