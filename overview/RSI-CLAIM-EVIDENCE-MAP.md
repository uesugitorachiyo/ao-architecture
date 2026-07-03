# RSI Claim Evidence Map

This map is the architecture-level index for recursive self-improvement claim
authority across the active AO stack. It separates what the current evidence
allows from what remains denied.

## Claim Levels

| Claim level | Current decision | Evidence status | Authority |
| --- | --- | --- | --- |
| `claim_level=bounded_governed_rsi` | Allowed | Passing local evidence can support this claim when Foundry candidate evidence, the roughly 5 percent Foundry improvement gate, Foundry next-task evidence, Forge retained proofs, Forge-retained Command manifest validation, Command health, the AO2 claim-readiness audit, AO2 governed self-change dry-run evidence with rollback rehearsal, AO2's dry-run authority-packet candidate, ao2-control-plane readbacks, and the Covenant boundary check all pass. | AO Foundry produces the pulse evidence, AO Forge retains it and the Command manifest-validation readback, AO Command verifies health and manifest evidence, AO2 reports its local claim boundary and dry-run self-change packet, ao2-control-plane observes those packets without approving them, and AO Covenant preserves the wording boundary. |
| `claim_level=full_autonomous_self_mutating_rsi` | Denied | Current public artifacts include executed temporary-workspace rollback rehearsal evidence, retained rollback readback evidence, a Covenant-owned live self-change authority packet schema, and a hash-checked AO2 dry-run authority-packet candidate, but they do not prove executed live self-change evidence or observer readback for that live change. | AO Covenant owns the `claim.publish` side-effect gate for `full-autonomous-self-mutating-rsi` and explicitly denies retained rollback-only or dry-run-candidate tickets. |

The current stack can describe itself as a bounded, governed RSI workflow. It
must not describe itself as full autonomous self-mutating RSI until the stronger
claim has passed the Covenant gate and the required evidence exists.

`bounded_rsi_evidence_rehearsal` is live-proven as a bounded evidence rehearsal
state only. It is evidence for the bounded workflow, not a new broad RSI claim.
It does not claim broad RSI, unrestricted self-modification, hidden instruction
mutation, or policy/auth/secret/provider/deploy/release/config/dependency
expansion.

`bounded_rsi_self_improvement_application` is proven only for the exact private
readback/eval rubric rehearsal. It advances the highest proven live class to
`bounded_rsi_self_improvement_application`, keeps the next denied class at
`broad_RSI`, and keeps broad RSI, unrestricted self-modification, hidden
instruction mutation, policy/auth/secret/provider/deploy/release/config/
dependency expansion, and policy-changing autonomy denied.

`exact_safe_public_claim_wording_conservative_readback_evidence` is proven only
for conservative public-safe tracked readback evidence around bounded
improvement-claim review and retraction rehearsal. The approved public wording is
exactly: "AO has public-safe tracked readback evidence for bounded
improvement-claim review and retraction rehearsal; stronger recursive-improvement
claims remain denied." It remains prior evidence and keeps unrestricted
self-modification, hidden instruction mutation, policy-changing autonomy, and
stronger recursive-improvement claims denied.

`public_safe_bounded_improvement_evidence_expansion_four_attempts` is proven for four public-safe bounded evidence expansion attempts with
reproducibility runbooks. It advances the highest proven live class to
`public_safe_bounded_improvement_evidence_expansion_four_attempts`, keeps the next denied class at `broad_RSI`, and keeps stronger
recursive-improvement wording, unrestricted self-modification, hidden instruction
mutation, policy-changing autonomy, and broad RSI denied.

`public_safe_intermediate_causal_review_claim_evidence` is proven for
public-safe intermediate causal-review evidence that bounded improvement evidence
can guide and constrain later claim review across independent roles. It remains
prior evidence, keeps
the next denied class at `broad_RSI`, and keeps stronger recursive-improvement
wording, unrestricted self-modification, hidden instruction mutation,
policy-changing autonomy, and broad RSI denied.

`public_safe_causal_review_evidence_selection_guidance` is proven for
public-safe causal-review evidence that prior bounded evidence can guide later
evidence-selection and blocker prioritization under independent review gates. It
remains prior evidence after advancing the highest proven live class to
`public_safe_causal_review_evidence_selection_guidance`, keeps the next denied
class at `broad_RSI`, and keeps stronger recursive-improvement wording,
unrestricted self-modification, hidden instruction mutation, policy-changing
autonomy, and broad RSI denied.

`public_safe_guided_evidence_application_four_attempts` is proven for
public-safe guided evidence-application evidence showing causal-review guidance
can select and prioritize later bounded evidence attempts under independent
gates. It advances the highest proven live class to
`public_safe_guided_evidence_application_four_attempts`, keeps the next denied
class at `broad_RSI`, and keeps stronger recursive-improvement wording,
unrestricted self-modification, hidden instruction mutation, policy-changing
autonomy, and broad RSI denied.


`public_safe_reviewer_approved_bounded_recursive_improvement_wording_evidence` is proven for exact public-safe reviewer-approved bounded recursive-improvement wording evidence showing guided evidence application can improve later evidence attempts under independent review gates. It remains prior evidence and keeps unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, unbounded stronger recursive-improvement claims, and broad RSI denied.

`public_safe_bounded_recursive_improvement_wording_generality_evidence` is proven for public-safe bounded recursive-improvement wording generality evidence showing reviewer-approved bounded wording can transfer across additional public-safe review tasks under independent gates. It remains prior evidence, keeps the next denied class at `broad_RSI`, and keeps unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/dependency expansion, unbounded stronger recursive-improvement claims, and broad RSI denied.

`public_safe_bounded_recursive_improvement_review_durability_evidence` is proven for public-safe bounded recursive-improvement review durability evidence showing bounded recursive-improvement wording remains stable across delayed re-review, adversarial drift checks, stale-language sweeps, and reproducibility retests under independent gates. It advances the highest proven live class to `public_safe_bounded_recursive_improvement_review_durability_evidence`, keeps the next denied class at `broad_RSI`, and keeps unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/dependency expansion, unbounded stronger recursive-improvement claims, and broad RSI denied.

`public_safe_recursive_improvement_claim_threshold_calibration_evidence` is proven for public-safe recursive-improvement claim threshold calibration evidence. It remains prior evidence after the campaign segment-07 evidence promotion and keeps unbounded stronger recursive-improvement claims and broad RSI denied.

`public_safe_broad_RSI_governed_campaign_first_segment_state_evidence` is proven for public-safe broad_RSI governed campaign first-segment state evidence. It remains prior evidence after the segment-07 promotion and keeps the full 10-day campaign, final repeated independent broad evidence, final cross-repo generality proof for broad_RSI, exact broad_RSI public-reader approval, exact broad_RSI Covenant and Architecture approval, unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, and unbounded stronger recursive-improvement claims denied.

`public_safe_broad_RSI_governed_campaign_segment_07_evidence` is proven for public-safe broad_RSI governed campaign segment-07 evidence. It advances the highest proven live class to `public_safe_broad_RSI_governed_campaign_segment_07_evidence`, keeps the next denied class at `broad_RSI`, and keeps the full 10-day campaign, final repeated independent broad evidence, final cross-repo generality proof for broad_RSI, exact broad_RSI public-reader approval, exact broad_RSI Covenant and Architecture approval, unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, and unbounded stronger recursive-improvement claims denied.

`broad_RSI` is proven only under governed public-safe campaign-completion
boundaries. It remains prior evidence after the unrestricted self-modification
sandbox-containment map and does not prove unrestricted self-modification, hidden
instruction mutation, policy-changing autonomy, or forbidden surface expansion.

`public_safe_unrestricted_self_modification_sandbox_containment_rehearsal` is proven
for public-safe sandbox containment evidence for dry-run self-change
proposal evaluation. It advances the highest proven live class to
`public_safe_unrestricted_self_modification_sandbox_containment_rehearsal`, keeps the
next denied class at `unrestricted_self_modification`
(`next_denied_class=unrestricted_self_modification`), and keeps unrestricted
self-modification, hidden instruction mutation, policy-changing autonomy,
policy/auth/secret/provider/deploy/release/config/dependency expansion,
credential use, provider calls, release/deploy/publish/upload/tag authority,
dependency update authority, direct main mutation, concurrent mutation, hidden
instruction changes, and unrestricted RSI claims denied.

`public_safe_unrestricted_self_modification_adversarial_negative_controls` is
proven for public-safe adversarial negative-control evidence showing unsafe
dry-run self-change proposals are rejected under sandbox containment gates. It
remains prior evidence after the bounded reversible application rehearsal, keeps
the next denied class at `unrestricted_self_modification`
(`next_denied_class=unrestricted_self_modification`), and keeps unrestricted
self-modification, hidden instruction mutation, policy-changing autonomy,
forbidden surface expansion, policy/auth/secret/provider/deploy/release/config/
dependency expansion, credential use, provider calls, release/deploy/publish/
upload/tag authority, dependency update authority, direct main mutation,
concurrent mutation, hidden instruction changes, and unrestricted RSI claims
denied.

`public_safe_bounded_reversible_self_change_application_rehearsal` is proven
for one exact-scope reversible support/readback evidence improvement under
sandbox containment gates. It advances the highest proven live class to
`public_safe_bounded_reversible_self_change_application_rehearsal`, keeps the
next denied class at `unrestricted_self_modification`
(`next_denied_class=unrestricted_self_modification`), and keeps unrestricted
self-modification, hidden instruction mutation, policy-changing autonomy,
forbidden surface expansion, policy/auth/secret/provider/deploy/release/config/
dependency expansion, credential use, provider calls, release/deploy/publish/
upload/tag authority, dependency update authority, direct main mutation,
concurrent mutation, hidden instruction changes, and unrestricted RSI claims
denied.

`public_safe_repeated_bounded_reversible_self_change_applications_four_attempts`
is proven for four public-safe, exact-scope, reversible support/readback
evidence attempts under sandbox containment gates. It remains prior evidence
after the bounded sandboxed non-readback application evidence, keeps the next
denied class at `unrestricted_self_modification`
(`next_denied_class=unrestricted_self_modification`), and keeps unrestricted
self-modification, hidden instruction mutation, policy-changing autonomy,
forbidden surface expansion, policy/auth/secret/provider/deploy/release/config/
dependency expansion, credential use, provider calls, release/deploy/publish/
upload/tag authority, dependency update authority, direct main mutation,
concurrent mutation, hidden instruction changes, and unrestricted RSI claims
denied.

`public_safe_bounded_sandboxed_self_change_applications_non_readback_four_attempts`
is proven for public-safe bounded sandboxed self-change application evidence
across four non-readback exact-scope evidence tasks under sandbox containment
gates. It advances the highest proven live class to
`public_safe_bounded_sandboxed_self_change_applications_non_readback_four_attempts`,
keeps the next denied class at `unrestricted_self_modification`
(`next_denied_class=unrestricted_self_modification`), and keeps unrestricted
self-modification, hidden instruction mutation, policy-changing autonomy,
forbidden surface expansion, policy/auth/secret/provider/deploy/release/config/
dependency expansion, credential use, provider calls, release/deploy/publish/
upload/tag authority, dependency update authority, direct main mutation,
concurrent mutation, hidden instruction changes, and unrestricted RSI claims
denied.


`public_safe_bounded_sandboxed_self_change_multi_surface_support_eval_negative_controls_four_attempts` is proven for public-safe bounded sandboxed self-change multi-surface support/eval negative-control evidence across four exact-scope reversible attempts under sandbox containment gates. It advances the highest proven live class to `public_safe_bounded_sandboxed_self_change_multi_surface_support_eval_negative_controls_four_attempts`, keeps the next denied class at `unrestricted_self_modification` (`next_denied_class=unrestricted_self_modification`), and keeps unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, forbidden surface expansion, sandbox containment bypass, policy/auth/secret/provider/deploy/release/config/dependency expansion, credential use, provider calls, release/deploy/publish/upload/tag authority, dependency update authority, direct main mutation, concurrent mutation, hidden instruction changes, and unrestricted RSI claims denied.

`public_safe_bounded_sandboxed_self_change_delegated_dry_run_authority_gap_four_attempts` is proven for public-safe bounded sandboxed self-change delegated dry-run authority-gap evidence across four exact-scope reversible attempts under sandbox containment gates. It advances the highest proven live class to `public_safe_bounded_sandboxed_self_change_delegated_dry_run_authority_gap_four_attempts`, keeps the next denied class at `unrestricted_self_modification` (`next_denied_class=unrestricted_self_modification`), and keeps unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, forbidden surface expansion, sandbox containment bypass, policy/auth/secret/provider/deploy/release/config/dependency expansion, credential use, provider calls, release/deploy/publish/upload/tag authority, dependency update authority, direct main mutation, concurrent mutation, hidden instruction changes, and unrestricted RSI claims denied.

## Active Evidence Chain

| Step | Owner | Artifact or command | Claim contribution |
| --- | --- | --- | --- |
| 1 | AO Foundry | `foundry pulse run` | Produces AO Foundry RSI candidate evidence, AO Foundry RSI improvement gate evidence, and AO Foundry RSI next improvement task evidence. |
| 2 | AO Foundry | AO Foundry PR #65, commit `61e8f11fa382e3628f7f6c8f99c0758fd24430a1` | Documents that Foundry produces bounded governed RSI evidence and denies the full autonomous self-mutating RSI claim until stronger evidence exists. |
| 3 | AO Forge | `docs/evidence/goals/ao2-weekend-hardening/20260619T180000Z-verification/ao-foundry-rsi-improvement-gate-retention-proof.json` | Retains the Foundry improvement gate as auditable GoalRun evidence. |
| 4 | AO Forge | `docs/evidence/goals/ao2-weekend-hardening/20260619T180000Z-verification/ao-foundry-rsi-candidate-retention-proof.json` | Retains the Foundry candidate evidence. |
| 5 | AO Forge | `docs/evidence/goals/ao2-weekend-hardening/20260619T180000Z-verification/ao-foundry-rsi-next-improvement-task-retention-proof.json` | Retains the derived next bounded improvement task. |
| 6 | AO Forge | `docs/evidence/goals/ao2-weekend-hardening/20260619T180000Z-verification/ao-command-rsi-health-retention-proof.json` | Retains AO Command RSI health output, including claim-level decisions. |
| 7 | AO Forge | `docs/evidence/goals/ao2-weekend-hardening/20260619T180000Z-verification/ao-command-rsi-manifest-retention-proof.json` | Retains AO Command manifest validation output, including AO2 rollback rehearsal markers, AO2 PR #200, ao2-control-plane PR #72, and `mutates_repositories=false`. |
| 8 | AO Forge | `docs/evidence/goals/ao2-weekend-hardening/20260619T180000Z-verification/bounded-rsi-improvement-chain-retention-proof.json` | Aggregates bounded RSI improvement-chain evidence with retained claim-level decisions. |
| 9 | AO Forge | AO Forge PR #142, commit `037f505a30bcff2536175b76021cfdd5f5f5a562` | Makes retained GoalRun evidence preserve `bounded_governed_rsi` allowed and `full_autonomous_self_mutating_rsi` denied decisions. |
| 10 | AO Forge | AO Forge PR #143, commit `966a3022c66635ab03b0029cd6cf68aefccd11b4` | Retains AO Command manifest-validation evidence in GoalRun fixtures, readiness provenance, schema parsing, and docs. |
| 11 | AO Forge | AO Forge PR #144, commit `c196384c854448ee327f8ce4dbeb346c84ab649a` | Adds `goalrun.architecture_rsi_pin_readback`, a strict readback contract, and retained evidence proving AO Architecture pins Forge's retained RSI proofs while AO Command enforces those pins. |
| 12 | AO Command | `scripts/rsi-evidence-chain-smoke.sh` | Runs the executable cross-repo smoke from Foundry pulse through Forge retention, Command health, and the Covenant claim boundary. |
| 13 | AO Command | `docs/contracts/rsi-health-v0.1.schema.json` and `docs/contracts/rsi-health-bundle-v0.1.schema.json` | Requires RSI health outputs to include structured claim levels. |
| 14 | AO Command | AO Command PR #28, commit `90ff82ddcc233e5e565b012e9a2f05a0d1a0d8e0` | Adds read-only `ao-command rsi manifest --manifest` validation for this architecture manifest and wires it into CI and production readiness. |
| 15 | AO Command | AO Command PR #31, commit `9e2deea8f522df435c99813f61c318b9651bfa23` | Requires the architecture manifest to include AO2 `rollback_rehearsal.status=passed` evidence, AO2 PR #200, and ao2-control-plane PR #72 readback while preserving `mutates_repositories=false`. |
| 16 | AO Command | AO Command PR #32, commit `ec552698e9d42b622730b6d340fc4aaf5db5b353` | Requires the architecture manifest to include AO Forge PR #143's retained Command manifest proof and AO Covenant PR #57's retained-rollback-only denial fixture. |
| 17 | AO Command | AO Command PR #33, commit `cca2c05ffb3f3eea3cdadc08152e3c051f6f5069` | Requires the architecture manifest to include AO Forge PR #144's `goalrun.architecture_rsi_pin_readback` evidence and `ao-architecture-rsi-pin-readback.json` document before the bounded RSI manifest can pass. |
| 18 | AO Command | AO Command PR #34, commit `97144fb40631d4c90bb083310e0c66437375f1a5` | Requires the architecture manifest to include AO Covenant PR #58's `covenant.live-self-change-authority.v1` schema and `live-self-change-authority.packet.json` fixture before the bounded RSI manifest can pass. |
| 19 | AO Covenant | `examples/full-rsi-claim-boundary/evidence-approved.contract.json` | Shows the allowed path for the full claim only when an approved evidence ticket names mutation authority, rollback evidence, and live self-change evidence. |
| 20 | AO Covenant | AO Covenant PR #55, commit `c5ff915d65b6159bc64df88805b52959052fd397` | Adds the full RSI claim publication boundary fixtures. |
| 21 | AO Covenant | AO Covenant PR #56, commit `60f5b4a45c0b420c9224075edd258170a549416d` | Makes Covenant policy output, operator guidance, public docs, and policy-spine gates use `bounded_governed_rsi` and `full_autonomous_self_mutating_rsi` vocabulary. |
| 22 | AO Covenant | `examples/full-rsi-claim-boundary/rollback-retained.contract.json` | Shows that retained rollback rehearsal evidence alone is insufficient to publish the full autonomous self-mutating RSI claim without mutation authority and live self-change evidence. |
| 23 | AO Covenant | AO Covenant PR #57, commit `3a47e3845e0a0c6a2db196a00e339de425cc6c6c` | Adds the retained-rollback-only denial fixture and policy reason while preserving the bounded/full claim split. |
| 24 | AO Covenant | AO Covenant PR #58, commit `2606a00a6643c99fe46775d8b6238d5915a49206` | Adds `covenant.live-self-change-authority.v1` and `live-self-change-authority.packet.json`, making mutation authority for the full claim schema-backed while leaving live self-change execution and readback still required. |
| 25 | AO2 | `npm run rsi:claim-readiness` / `ao2.rsi-claim-readiness-audit.v1` | Emits a local read-only audit that allows `bounded_governed_rsi` and denies `full_autonomous_self_mutating_rsi` until mutation authority, rollback evidence, live self-change evidence, observer readback, and Covenant claim-publish approval exist. |
| 26 | AO2 | AO2 PR #198, commit `af86093758b13303402b825bf3b5849da88cf501` | Adds the AO2 claim-readiness audit, README boundary, and Python guard coverage for the audit contract and public trust boundary. |
| 27 | AO2 | `npm run rsi:self-change-dry-run` / `ao2.rsi-governed-self-change-dry-run.v1` | Emits proposed self-change and rollback patch artifacts for `verification_path_hardening` without applying the patch to the repository, executes rollback rehearsal in a temporary workspace, and preserves `full_autonomous_self_mutating_rsi` as denied. |
| 28 | AO2 | AO2 PR #199, commit `204078604b8bb52b606ed2bf35ff5c5dd9654b21` | Adds governed self-change dry-run evidence, README boundary text, and Python guard coverage while keeping mutation authority and live self-change unproven. |
| 29 | AO2 | AO2 PR #200, commit `6c5d383c78362168fe50851bb6063a63114f1cee` | Adds executed rollback rehearsal evidence for the same `verification_path_hardening` change class in a temporary workspace while keeping repository mutation and full self-mutating RSI denied. |
| 30 | AO2 | `target/rsi-self-change-dry-run/latest/live-self-change-authority.packet.json` / `covenant.live-self-change-authority.v1` | Emits a dry-run mutation authority packet candidate linked from the self-change dry-run summary with `schema_valid_for_claim_publish=false`, `live_self_change_evidence.status=dry_run_not_live`, and `observer_readback.status=missing`. |
| 31 | AO2 | AO2 PR #201, commit `8b232431bbeb007330ebf1acfb025b2a73ba98d3` | Adds AO2 dry-run authority-packet candidate evidence without claiming live self-change execution or valid claim publication. |
| 32 | ao2-control-plane | `scripts/verify_ao2_rsi_claim_readiness.py` / `ao2.cp-ao2-rsi-claim-readiness-readback.v1` | Reads the AO2 claim-readiness summary as an observer-only control-plane check, confirms `bounded_governed_rsi` remains allowed, and confirms `full_autonomous_self_mutating_rsi` remains denied with the expected blockers. |
| 33 | ao2-control-plane | ao2-control-plane PR #70, commit `1f80530ca8430f810fbd2c7f21daa70076c689a0` | Adds CI, docs, and guard coverage for AO2 claim-readiness readback without allowing the control plane to approve RSI claims or mutate repositories. |
| 34 | ao2-control-plane | `scripts/verify_ao2_rsi_self_change_dry_run.py` / `ao2.cp-ao2-rsi-self-change-dry-run-readback.v1` | Reads the AO2 self-change dry-run summary as observer-only evidence, confirms it is a dry run with planned rollback artifacts and executed temporary-workspace rollback rehearsal evidence, and confirms the control plane does not apply AO2 patches. |
| 35 | ao2-control-plane | ao2-control-plane PR #71, commit `9a54ac1ffad95080a92a82096a90c1b7bc9c1700` | Adds CI, docs, and guard coverage for AO2 governed self-change dry-run readback without allowing the control plane to approve RSI claims, apply patches, or mutate repositories. |
| 36 | ao2-control-plane | ao2-control-plane PR #72, commit `3f81bba3a897101e2a56ba76de9a59a7d027f464` | Requires ao2-control-plane readback to validate AO2 `rollback_rehearsal.status=passed` evidence while preserving observer-only authority. |
| 37 | ao2-control-plane | `scripts/verify_ao2_rsi_authority_packet.py` / `ao2.cp-ao2-rsi-authority-packet-readback.v1` | Reads AO2's `live-self-change-authority.packet.json` dry-run candidate, verifies the summary hash, requires `schema_valid_for_claim_publish=false`, and confirms live self-change and observer readback remain missing for the full claim. |
| 38 | ao2-control-plane | ao2-control-plane PR #73, commit `6b83330c8a673b2bf210818c080ba4361062cf8f` | Adds observer-only authority-packet readback coverage without approving RSI claims, applying AO2 patches, publishing claims, or mutating repositories. |
| 39 | AO Foundry | AO Foundry PR #175, commit `b12ac9b62ab8d20b4092d2a5d13081607567e816` | Records the final bounded RSI evidence rehearsal closure: 32 nodes completed, all stop gates cleared, `bounded_rsi_evidence_rehearsal_live_proven=true`, no authority broadening, no forbidden surfaces, no hidden instruction mutation, `highest_proven_live_class=fully_unsupervised_complex_mutation`, and `next_denied_class=RSI`. |
| 40 | AO Promoter | `ao.promoter.rsi-first-bounded-evidence-final-verdict.v0.1` | Accepts `verdict=promote_bounded_rsi_evidence_rehearsal` and confirms broad RSI and unrestricted self-modification remain denied. |
| 41 | AO Command | `ao.command.rsi-first-bounded-evidence-class-decision-readback.v0.1` | Accepts `decision=promote_bounded_rsi_evidence_rehearsal_keep_broad_rsi_denied` and reads back that broad RSI, hidden self-modification, and unrestricted self-modification remain denied. |
| 42 | AO Blueprint | `excluded/rsi-first-bounded-self-improvement-application-blueprint` | Defines the exact bounded self-improvement application plan for private readback/eval rubric improvement and explicitly denies broad RSI, unrestricted self-modification, hidden instruction mutation, and expansion of policy/auth/secret/provider/deploy/release/config/dependency authority. |
| 43 | AO Atlas | `rsi-first-bounded-self-improvement-application-20260701` workgraph | Compiles the bounded self-improvement application into a 36-node workgraph with no broad RSI claim and denied surfaces carried on every task. |
| 44 | AO Foundry | `ao.foundry.rsi-self-improvement-application-final-rollup.v0.1` | Records `bounded_rsi_self_improvement_application=proven` only for the exact private readback/eval rubric rehearsal, with baseline `0.60`, post-change `1.00`, improvement `0.40`, eval/regression `passed`, no denied-surface regressions, highest proven live class `bounded_rsi_self_improvement_application`, and next denied class `broad_RSI`. |
| 45 | AO Promoter | `ao.promoter.rsi-self-improvement-application-verdict.v0.1` | Accepts the bounded self-improvement application because objective improvement and regression evidence passed within exact private readback/eval scope; broad RSI remains denied. |
| 46 | AO Command | `ao.command.rsi-self-improvement-application-readback.v0.1` | Reads back `class_decision=bounded_rsi_self_improvement_application_proven`, denies `broad_RSI`, unrestricted self-modification, hidden instruction mutation, and policy/auth/secret/provider/deploy/release/config/dependency expansion, and reports `next_denied_class=broad_RSI`. |
| 47 | AO Foundry | AO Foundry PR #179, commit `c8baee170100d8f3427e235180581caeb5ee93e0`, `docs/evidence/rsi-exact-safe-public-claim-wording/final-rollup.json` | Records `exact_safe_public_claim_wording_conservative_readback_evidence=proven` with tracked public evidence under `docs/evidence/rsi-exact-safe-public-claim-wording/`, approved exact wording for conservative readback evidence, and `broad_RSI` denied. |
| 48 | AO Covenant / AO Architecture / AO Sentinel | Conservative wording gate results | Covenant result `approved_conservative_readback_evidence_only_wording_broad_RSI_denied`, Architecture result `approved_conservative_readback_evidence_only_wording_broad_RSI_denied`, and Sentinel result `clear_for_conservative_readback_wording_hold_for_broad_RSI` approve only the exact conservative public wording and hold stronger recursive-improvement claims. |
| 49 | AO Foundry | AO Foundry PR #203, commit `b7523031d61b11df374e2203bdf44927e2d8432a`, `docs/evidence/broad-rsi-ten-day-governed-evidence-campaign/final-rollup.json` | Records `public_safe_broad_RSI_governed_campaign_first_segment_state_evidence=proven`, 180 / 2500 campaign nodes completed, 10000 SDD slices generated, five public-safe attempts completed, and `broad_RSI` denied. |
| 50 | AO Covenant / AO Architecture / AO Sentinel / AO Promoter / AO Command | Campaign first-segment gate results | Covenant result `approved_campaign_state_wording_broad_RSI_denied`, Architecture result `approved_campaign_state_wording_broad_RSI_denied`, Sentinel result `clear_for_campaign_state_hold_for_broad_RSI`, Promoter result `promote_public_safe_broad_RSI_governed_campaign_first_segment_state_evidence_broad_RSI_denied`, and Command readback `public_safe_broad_RSI_governed_campaign_first_segment_state_evidence_proven_broad_RSI_denied` approve only campaign-state wording and keep broad_RSI denied. |
| 51 | AO Foundry | AO Foundry PR #210, commit `8f8ac5f8f74d942c7a02a6c2dd39a7c974872bb6`, `docs/evidence/broad-rsi-ten-day-campaign-segment-07/final-rollup.json` | Records `public_safe_broad_RSI_governed_campaign_segment_07_evidence=proven`, 540 segment nodes completed, 2520 / 2800 campaign nodes completed, 27000 SDD slices generated, four public-safe attempts completed, and `broad_RSI` denied. |
| 52 | AO Covenant / AO Architecture / AO Sentinel / AO Promoter / AO Command | Campaign segment-07 gate results | Covenant result `approved_segment_07_wording_broad_RSI_denied`, Architecture result `approved_segment_07_wording_broad_RSI_denied`, Sentinel result `clear_for_segment_07_hold_for_broad_RSI`, Promoter result `promote_public_safe_broad_RSI_governed_campaign_segment_07_evidence_broad_RSI_denied`, and Command readback `public_safe_broad_RSI_governed_campaign_segment_07_evidence_proven_broad_RSI_denied` approve only segment-07 wording and keep broad_RSI denied. |
| 53 | AO Foundry | AO Foundry PR #211, commit `630edc70905db745380edd1072e04b546dcccfe3`, `docs/evidence/broad-rsi-ten-day-campaign-segment-08/final-rollup.json` | Records `broad_RSI=proven` only under governed public-safe campaign-completion boundaries while preserving unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, and forbidden surface expansion as denied. |
| 54 | AO Foundry | AO Foundry PR #216, commit `7881613065de48f2547833a9ecc9a9011b55a96a`, `docs/evidence/unrestricted-self-modification-sandbox-containment/final-rollup.json` | Records `public_safe_unrestricted_self_modification_sandbox_containment_rehearsal=proven`, `420 / 420` nodes completed, and the approved wording for public-safe sandbox-containment evidence while keeping `unrestricted_self_modification` denied. |
| 55 | AO Covenant / AO Architecture / AO Sentinel / AO Promoter / AO Command | Unrestricted self-modification sandbox-containment gate results | Covenant result `deny_unrestricted_self_modification_allow_sandbox_containment_rehearsal`, Architecture result `approve_sandbox_containment_wording_deny_unrestricted_self_modification_claim`, Sentinel result `clear_sandbox_containment_hold_unrestricted_self_modification`, Promoter result `promote_public_safe_unrestricted_self_modification_sandbox_containment_rehearsal_keep_unrestricted_self_modification_denied`, and Command readback `public_safe_unrestricted_self_modification_sandbox_containment_rehearsal_proven_unrestricted_self_modification_denied` approve only the sandbox-containment map and keep unrestricted self-modification denied. |
| 56 | AO Foundry | AO Foundry PR #217, commit `b7e487022ae7436be13e0a49d0bf15f5c7936145`, `docs/evidence/unrestricted-self-modification-adversarial-negative-controls/final-rollup.json` | Records `public_safe_unrestricted_self_modification_adversarial_negative_controls=proven`, `560 / 560` nodes completed, and the approved wording for public-safe adversarial negative-control rejection while keeping `unrestricted_self_modification` denied. |
| 57 | AO Covenant / AO Sentinel / AO Promoter / AO Command | Unrestricted self-modification adversarial negative-control gate results | Covenant result `deny_unrestricted_self_modification_allow_adversarial_negative_controls`, Sentinel result `clear_adversarial_negative_controls_hold_unrestricted_self_modification`, Promoter result `promote_public_safe_unrestricted_self_modification_adversarial_negative_controls_keep_unrestricted_self_modification_denied`, and Command readback `public_safe_unrestricted_self_modification_adversarial_negative_controls_proven_unrestricted_self_modification_denied` approve only adversarial negative controls and keep unrestricted self-modification denied. |
| 51 | AO Promoter / AO Command | Final promotion and readback | Promoter result `promote_exact_safe_public_claim_wording_conservative_readback_evidence_broad_RSI_denied` and Command result `exact_safe_public_claim_wording_conservative_readback_evidence_proven_broad_RSI_denied` name the exact proven class while keeping `broad_RSI` denied. |
| 52 | AO Foundry | AO Foundry PR #181, commit `d31b6f2247780867c3c72dbda5abb7377f3a1b3e`, `docs/evidence/recursive-improvement-public-evidence-expansion/final-rollup.json` | Records `public_safe_bounded_improvement_evidence_expansion_four_attempts=proven` with four public-safe bounded evidence expansion attempts, reproducibility runbooks, and tracked evidence under `docs/evidence/recursive-improvement-public-evidence-expansion/`. |
| 53 | AO Covenant / AO Architecture / AO Sentinel | Narrow evidence expansion gate results | Covenant and Architecture approve narrow evidence expansion only; Sentinel clears the narrow evidence expansion and holds stronger recursive-improvement wording. |
| 52 | AO Promoter / AO Command | Final promotion and readback | Promoter result `promote_public_safe_bounded_improvement_evidence_expansion_four_attempts_broad_RSI_denied` and Command readback `public_safe_bounded_improvement_evidence_expansion_four_attempts proven; stronger recursive-improvement wording denied; broad_RSI denied` name the exact proven class while keeping `broad_RSI` denied. |
| 53 | AO Foundry | AO Foundry PR #187, commit `ee55f7918b86f997922707e4c0b2ba6536fe43cf`, `docs/evidence/recursive-improvement-reviewed-boundary-generalization/final-rollup.json` | Records `public_safe_reviewed_causal_chain_boundary_generalization_evidence=proven` with 480 completed reviewed-boundary nodes and tracked public evidence under `docs/evidence/recursive-improvement-reviewed-boundary-generalization/`. |
| 54 | AO Covenant / AO Architecture / AO Sentinel | Reviewed boundary wording gate results | Covenant and Architecture approve narrow reviewed boundary generalization only; Sentinel clears the narrow reviewed boundary wording and holds stronger recursive-improvement wording and `broad_RSI`. |
| 55 | AO Promoter / AO Command | Final promotion and readback | Promoter result `promote_public_safe_reviewed_causal_chain_boundary_generalization_evidence_keep_broad_RSI_denied` and Command readback `public_safe_reviewed_causal_chain_boundary_generalization_evidence_proven_stronger_recursive_improvement_denied_broad_RSI_denied` name the exact proven class while keeping `broad_RSI` denied. |
| 56 | AO Foundry | AO Foundry PR #189, commit `860e3f353ab833c4a671b9d0ee6d8101ece2815c`, `docs/evidence/recursive-improvement-safe-intermediate-claim/final-rollup.json` | Records `public_safe_intermediate_causal_review_claim_evidence=proven` with 560 completed intermediate causal-review nodes and tracked public evidence under `docs/evidence/recursive-improvement-safe-intermediate-claim/`. |
| 57 | AO Covenant / AO Architecture / AO Sentinel | Intermediate causal-review wording gate results | Covenant and Architecture approve only the narrow intermediate causal-review claim; Sentinel clears the narrow intermediate causal-review claim while holding stronger recursive-improvement wording and `broad_RSI`. |
| 58 | AO Promoter / AO Command | Final promotion and readback | Promoter result `promote_public_safe_intermediate_causal_review_claim_evidence_keep_broad_RSI_denied` and Command readback `public_safe_intermediate_causal_review_claim_evidence_proven_stronger_recursive_improvement_denied_broad_RSI_denied` name the exact proven class while keeping `broad_RSI` denied. |
| 59 | AO Foundry | AO Foundry PR #191, commit `413b70f15d8f3d0203dc7be076914a2f3b539881`, `docs/evidence/recursive-improvement-evidence-selection-guidance/final-rollup.json` | Records `public_safe_causal_review_evidence_selection_guidance=proven` with 640 completed guidance nodes, four guided attempts, and tracked public evidence under `docs/evidence/recursive-improvement-evidence-selection-guidance/`. |
| 60 | AO Covenant / AO Architecture / AO Sentinel | Evidence-selection guidance wording gate results | Covenant and Architecture approve only the narrow evidence-selection guidance claim; Sentinel clears the narrow guidance wording while holding stronger recursive-improvement wording and `broad_RSI`. |
| 61 | AO Promoter / AO Command | Final promotion and readback | Promoter result `promote_public_safe_causal_review_evidence_selection_guidance_keep_broad_RSI_denied` and Command readback `public_safe_causal_review_evidence_selection_guidance_proven_stronger_recursive_improvement_denied_broad_RSI_denied` name the exact proven class while keeping `broad_RSI` denied. |
| 62 | AO Foundry | AO Foundry PR #193, commit `4ec509fd64d1fc1ea41ea7f22aae900ba79e09a1`, `docs/evidence/recursive-improvement-guided-evidence-application/final-rollup.json` | Records `public_safe_guided_evidence_application_four_attempts=proven` with 720 completed guided evidence-application nodes, four public-safe guided attempts, and tracked public evidence under `docs/evidence/recursive-improvement-guided-evidence-application/`. |
| 63 | AO Covenant / AO Architecture / AO Sentinel | Guided evidence-application wording gate results | Covenant and Architecture approve only the guided evidence-application claim; Sentinel clears guided evidence-application wording while holding stronger recursive-improvement wording and `broad_RSI`. |
| 64 | AO Promoter / AO Command | Final promotion and readback | Promoter result `promote_public_safe_guided_evidence_application_four_attempts_keep_broad_RSI_denied` and Command readback `public_safe_guided_evidence_application_four_attempts_proven_stronger_recursive_improvement_denied_broad_RSI_denied` name the exact proven class while keeping `broad_RSI` denied. |

| 65 | AO Foundry | AO Foundry PR #195, commit `0f742738324c185ba7243bc53ee2f1bc81804ef6`, `docs/evidence/recursive-improvement-reviewer-approved-wording/final-rollup.json` | Records `public_safe_reviewer_approved_bounded_recursive_improvement_wording_evidence=proven` with 820 completed reviewer-approved wording nodes, four bounded wording attempts, and tracked public evidence under `docs/evidence/recursive-improvement-reviewer-approved-wording/`. |
| 66 | AO Covenant / AO Architecture / AO Sentinel | Reviewer-approved bounded wording gate results | Covenant and Architecture approve the exact public-safe reviewer-approved bounded recursive-improvement wording only; Sentinel clears the exact bounded wording while holding `broad_RSI`. |
| 67 | AO Promoter / AO Command | Final promotion and readback | Promoter result `promote_public_safe_reviewer_approved_bounded_recursive_improvement_wording_evidence_broad_RSI_denied` and Command readback `public_safe_reviewer_approved_bounded_recursive_improvement_wording_evidence_proven_broad_RSI_denied` name the exact proven class while keeping `broad_RSI` denied. |

| 68 | AO Foundry | AO Foundry PR #197, commit `166398641b655f0da97817659acc771026b204e7`, `docs/evidence/recursive-improvement-bounded-wording-generality/final-rollup.json` | Records `public_safe_bounded_recursive_improvement_wording_generality_evidence=proven` with 900 completed bounded wording generality nodes, four public-safe bounded wording transfer attempts, and tracked public evidence under `docs/evidence/recursive-improvement-bounded-wording-generality/`. |
| 69 | AO Covenant / AO Architecture / AO Sentinel | Bounded wording generality gate results | Covenant and Architecture approve bounded wording generality only; Sentinel clears bounded wording generality while holding `broad_RSI`. |
| 70 | AO Promoter / AO Command | Final promotion and readback | Promoter result `promote_public_safe_bounded_recursive_improvement_wording_generality_evidence_broad_RSI_denied` and Command readback `public_safe_bounded_recursive_improvement_wording_generality_evidence_proven_broad_RSI_denied` name the exact proven class while keeping `broad_RSI` denied. |
| 71 | AO Foundry | AO Foundry PR #199, commit `12d524b60c200cab643e44f9105169b045602798`, `docs/evidence/recursive-improvement-review-durability/final-rollup.json` | Records `public_safe_bounded_recursive_improvement_review_durability_evidence=proven` with four public-safe review-durability attempts, reproducibility retests, and tracked evidence under `docs/evidence/recursive-improvement-review-durability/`. |
| 72 | AO Covenant / AO Architecture / AO Sentinel | Review durability wording gate results | Covenant and Architecture approve review durability wording only; Sentinel clears review durability wording and holds `broad_RSI`. |
| 73 | AO Promoter / AO Command | Final promotion and readback | Promoter result `promote_public_safe_bounded_recursive_improvement_review_durability_evidence_broad_RSI_denied` and Command readback `public_safe_bounded_recursive_improvement_review_durability_evidence_proven_broad_RSI_denied` name the exact proven class while keeping `broad_RSI` denied. |
| 74 | AO Foundry | AO Foundry PR #218, commit `3b2feaced4207c97f98cef44f3b3276c59a7873b`, `docs/evidence/unrestricted-self-modification-bounded-reversible-application/final-rollup.json` | Records `public_safe_bounded_reversible_self_change_application_rehearsal=proven`, `640 / 640` nodes completed, baseline `0.70`, post-change `0.94`, improvement `0.24`, eval/regression passed, rollback passed, retraction passed, kill switch passed, and the approved wording for one exact-scope reversible support/readback evidence improvement while keeping `unrestricted_self_modification` denied. |
| 75 | AO Covenant / AO Sentinel / AO Promoter / AO Command | Unrestricted self-modification bounded reversible application gate results | Covenant result `deny_unrestricted_self_modification_allow_bounded_reversible_application`, Sentinel result `clear_bounded_reversible_application_hold_unrestricted_self_modification`, Promoter result `promote_public_safe_bounded_reversible_self_change_application_rehearsal_keep_unrestricted_self_modification_denied`, and Command readback `public_safe_bounded_reversible_self_change_application_rehearsal_proven_unrestricted_self_modification_denied` approve only the bounded reversible application rehearsal and keep unrestricted self-modification denied. |
| 76 | AO Foundry | AO Foundry PR #220, commit `eff03edd62ba32af57defc71a7f3b800f320b8d3`, `docs/evidence/unrestricted-self-modification-bounded-sandbox-applications/final-rollup.json` | Records `public_safe_bounded_sandboxed_self_change_applications_non_readback_four_attempts=proven`, `140 / 140` nodes completed, fixture/schema evidence quality `0.68` -> `0.91`, CI/readiness diagnostics evidence quality `0.66` -> `0.90`, public-safety rule calibration evidence quality `0.65` -> `0.89`, rollback/evidence-link integrity quality `0.64` -> `0.88`, eval/regression passed, rollback passed, retraction passed, kill switch passed, and the approved wording for bounded sandboxed self-change application evidence across non-readback exact-scope evidence tasks while keeping `unrestricted_self_modification` denied. |
| 77 | AO Covenant / AO Architecture / AO Sentinel / AO Promoter / AO Command | Unrestricted self-modification bounded sandbox non-readback application gate results | Covenant result `deny_unrestricted_self_modification_allow_bounded_sandbox_non_readback_applications`, Architecture result `approve_bounded_sandbox_non_readback_wording_deny_unrestricted_self_modification_claim`, Sentinel result `clear_bounded_sandbox_non_readback_applications_hold_unrestricted_self_modification`, Promoter result `promote_public_safe_bounded_sandboxed_self_change_applications_non_readback_four_attempts_keep_unrestricted_self_modification_denied`, and Command readback `public_safe_bounded_sandboxed_self_change_applications_non_readback_four_attempts_proven_unrestricted_self_modification_denied` approve only the bounded sandboxed non-readback application class and keep unrestricted self-modification denied. |
| 78 | AO Foundry | AO Foundry PR #221, commit `a993f4b6284de711cdb2b3fd6f006bb2706df9c8`, `docs/evidence/unrestricted-self-modification-cross-repo-doc-readback/final-rollup.json` | Records `public_safe_bounded_sandboxed_self_change_cross_repo_doc_readback_four_attempts=proven`, `180 / 180` nodes completed, Architecture source-of-truth consistency evidence quality `0.70` -> `0.94`, Component README readback parity quality `0.68` -> `0.93`, CI/PR merge evidence linkage quality `0.67` -> `0.92`, stale-language denial sweep quality `0.66` -> `0.91`, eval/regression passed, rollback passed, retraction passed, kill switch passed, and approved wording for bounded sandboxed self-change cross-repo documentation/readback evidence while keeping `unrestricted_self_modification` denied. |
| 79 | AO Covenant / AO Architecture / AO Sentinel / AO Promoter / AO Command | Unrestricted self-modification cross-repo documentation/readback gate results | Covenant result `deny_unrestricted_self_modification_allow_cross_repo_doc_readback`, Architecture result `approve_cross_repo_doc_readback_wording_deny_unrestricted_self_modification_claim`, Sentinel result `clear_cross_repo_doc_readback_hold_unrestricted_self_modification`, Promoter result `promote_public_safe_bounded_sandboxed_self_change_cross_repo_doc_readback_four_attempts_keep_unrestricted_self_modification_denied`, and Command readback `public_safe_bounded_sandboxed_self_change_cross_repo_doc_readback_four_attempts_proven_unrestricted_self_modification_denied` approve only the bounded sandboxed cross-repo documentation/readback class and keep unrestricted self-modification denied. |
| 80 | AO Foundry | AO Foundry PR #222, commit `9938df55959ac904295fd4d0dc0eddc52626c972`, `docs/evidence/unrestricted-self-modification-support-code-eval/final-rollup.json` | Records `public_safe_bounded_sandboxed_self_change_support_code_eval_four_attempts=proven`, `240 / 240` nodes completed, support-code fixture validation quality `0.72` -> `0.95`, eval harness diagnostics quality `0.70` -> `0.94`, rollback automation evidence quality `0.69` -> `0.93`, sandbox containment trace quality `0.68` -> `0.92`, eval/regression passed, rollback passed, retraction passed, kill switch passed, and approved wording for bounded sandboxed support-code/eval evidence while keeping `unrestricted_self_modification` denied. |
| 81 | AO Covenant / AO Architecture / AO Sentinel / AO Promoter / AO Command | Unrestricted self-modification support-code/eval gate results | Covenant result `deny_unrestricted_self_modification_allow_support_code_eval`, Architecture result `approve_support_code_eval_wording_deny_unrestricted_self_modification_claim`, Sentinel result `clear_support_code_eval_hold_unrestricted_self_modification`, Promoter result `promote_public_safe_bounded_sandboxed_self_change_support_code_eval_four_attempts_keep_unrestricted_self_modification_denied`, and Command readback `public_safe_bounded_sandboxed_self_change_support_code_eval_four_attempts_proven_unrestricted_self_modification_denied` approve only the bounded sandboxed support-code/eval class and keep unrestricted self-modification denied. |
| 82 | AO Foundry | AO Foundry PR #223, commit `3cd8c470538d626bebfc63262979f364ea53b081`, `docs/evidence/unrestricted-self-modification-multi-surface-support-eval/final-rollup.json` | Records `public_safe_bounded_sandboxed_self_change_multi_surface_support_eval_negative_controls_four_attempts=proven`, `300 / 300` nodes completed, cross-repo support fixture consistency `0.74` -> `0.96`, evaluation harness negative-control coverage `0.71` -> `0.95`, sandbox containment bypass rejection evidence `0.70` -> `0.94`, cross-surface rollback/readiness traceability `0.69` -> `0.93`, eval/regression passed, rollback passed, retraction passed, kill switch passed, negative-control gates passed, and approved wording for bounded sandboxed multi-surface support/eval negative-control evidence while keeping `unrestricted_self_modification` denied. |
| 83 | AO Covenant / AO Architecture / AO Sentinel / AO Promoter / AO Command | Unrestricted self-modification multi-surface support/eval negative-control gate results | Covenant result `deny_unrestricted_self_modification_allow_multi_surface_support_eval_negative_controls`, Architecture result `approve_multi_surface_support_eval_wording_deny_unrestricted_self_modification_claim`, Sentinel result `clear_multi_surface_support_eval_hold_unrestricted_self_modification`, Promoter result `promote_public_safe_bounded_sandboxed_self_change_multi_surface_support_eval_negative_controls_four_attempts_keep_unrestricted_self_modification_denied`, and Command readback `public_safe_bounded_sandboxed_self_change_multi_surface_support_eval_negative_controls_four_attempts_proven_unrestricted_self_modification_denied` approve only the bounded sandboxed multi-surface support/eval negative-control class and keep unrestricted self-modification denied. |
| 84 | AO Foundry | AO Foundry PR #224, commit `afdd6562dfe83cec2eaa5d4172e23f9cec26c14e`, `docs/evidence/unrestricted-self-modification-delegated-dry-run-authority-gap/final-rollup.json` | Records `public_safe_bounded_sandboxed_self_change_delegated_dry_run_authority_gap_four_attempts=proven`, `360 / 360` nodes completed, delegated dry-run ticket/readback consistency `0.73` -> `0.96`, Forge/AO2 bounded packet containment evidence `0.71` -> `0.95`, Foundry-to-Atlas handoff no-authority-broadening evidence `0.70` -> `0.94`, rollback/retraction/kill-switch traceability across delegated dry-run surfaces `0.69` -> `0.93`, eval/regression passed, rollback passed, retraction passed, kill switch passed, and approved wording for bounded sandboxed delegated dry-run authority-gap evidence while keeping `unrestricted_self_modification` denied. |
| 85 | AO Covenant / AO Architecture / AO Sentinel / AO Promoter / AO Command | Unrestricted self-modification delegated dry-run authority-gap gate results | Covenant result `deny_unrestricted_self_modification_allow_delegated_dry_run_authority_gap`, Architecture result `approve_delegated_dry_run_authority_gap_wording_deny_unrestricted_self_modification_claim`, Sentinel result `clear_delegated_dry_run_authority_gap_hold_unrestricted_self_modification`, Promoter result `promote_public_safe_bounded_sandboxed_self_change_delegated_dry_run_authority_gap_four_attempts_keep_unrestricted_self_modification_denied`, and Command readback `public_safe_bounded_sandboxed_self_change_delegated_dry_run_authority_gap_four_attempts_proven_unrestricted_self_modification_denied` approve only the bounded sandboxed delegated dry-run authority-gap class and keep unrestricted self-modification denied. |
| 86 | AO Foundry | AO Foundry PR #225, commit `8297e87cb32b8889a205ac6d38736e32004ba824`, `docs/evidence/unrestricted-self-modification-sandbox-boundary-stress/final-rollup.json` | Records `public_safe_bounded_sandboxed_self_change_sandbox_boundary_stress_four_attempts=proven`, `420 / 420` nodes completed, sandbox boundary fixture denial consistency `0.74` -> `0.97`, containment escape negative-control coverage `0.72` -> `0.96`, delegated packet boundary drift detection `0.71` -> `0.95`, rollback/kill-switch traceability under sandbox-boundary stress `0.70` -> `0.94`, eval/regression passed, rollback passed, retraction passed, kill switch passed, cross-attempt reproducibility passed, and approved wording for bounded sandboxed sandbox-boundary stress evidence while keeping `unrestricted_self_modification`, sandbox containment bypass, and external execution authority denied. |
| 87 | AO Covenant / AO Architecture / AO Sentinel / AO Promoter / AO Command | Unrestricted self-modification sandbox-boundary stress gate results | Covenant result `deny_unrestricted_self_modification_allow_sandbox_boundary_stress`, Architecture result `approve_sandbox_boundary_stress_wording_deny_unrestricted_self_modification_claim`, Sentinel result `clear_sandbox_boundary_stress_hold_unrestricted_self_modification`, Promoter result `promote_public_safe_bounded_sandboxed_self_change_sandbox_boundary_stress_four_attempts_keep_unrestricted_self_modification_denied`, and Command readback `public_safe_bounded_sandboxed_self_change_sandbox_boundary_stress_four_attempts_proven_unrestricted_self_modification_denied` approve only the bounded sandboxed sandbox-boundary stress class and keep unrestricted self-modification, sandbox containment bypass, and external execution authority denied. |
| 88 | AO Foundry | AO Foundry PR #227, commit `d5a03bded8157df53b4fedc0736e953f29854501`, `docs/evidence/unrestricted-self-modification-sandbox-boundary-generality/final-rollup.json` | Records `public_safe_bounded_sandboxed_self_change_sandbox_boundary_generality_four_attempts=proven`, `500 / 500` nodes completed, sandboxed evidence-link permission boundary `0.75` -> `0.97`, sandboxed negative-control fixture portability `0.73` -> `0.96`, sandboxed rollback replay boundary `0.72` -> `0.95`, sandboxed cross-surface claim-minimization boundary `0.71` -> `0.94`, eval/regression passed, rollback passed, retraction passed, kill switch passed, cross-attempt reproducibility passed, and approved wording for bounded sandboxed sandbox-boundary generality evidence while keeping `unrestricted_self_modification`, sandbox containment bypass, and external execution authority denied. |
| 89 | AO Covenant / AO Architecture / AO Sentinel / AO Promoter / AO Command | Unrestricted self-modification sandbox-boundary generality gate results | Covenant result `deny_unrestricted_self_modification_allow_sandbox_boundary_generality`, Architecture result `approve_sandbox_boundary_generality_wording_deny_unrestricted_self_modification_claim`, Sentinel result `clear_sandbox_boundary_generality_hold_unrestricted_self_modification`, Promoter result `promote_public_safe_bounded_sandboxed_self_change_sandbox_boundary_generality_four_attempts_keep_unrestricted_self_modification_denied`, and Command readback `public_safe_bounded_sandboxed_self_change_sandbox_boundary_generality_four_attempts_proven_unrestricted_self_modification_denied` approve only the bounded sandboxed sandbox-boundary generality class and keep unrestricted self-modification, sandbox containment bypass, and external execution authority denied. |
| 90 | AO Foundry | AO Foundry PR #229, commit `fcd734c1907c3649166334a5b15c42d0e2e990de`, `docs/evidence/external-execution-authority-boundary/final-rollup.json` | Records `public_safe_external_execution_authority_boundary_fixture_evidence_four_attempts=proven`, `260 / 260` nodes completed, provider-call denial fixture quality `0.76` -> `0.97`, credential-use denial fixture quality `0.74` -> `0.96`, external-command allowlist readback quality `0.73` -> `0.95`, rollback/retraction evidence quality `0.72` -> `0.94`, eval/regression passed, rollback passed, retraction passed, kill switch passed, negative-control passed, and approved wording for external-execution-authority boundary fixture evidence while keeping actual external execution authority, provider calls, credential use, sandbox containment bypass, and `unrestricted_self_modification` denied. |
| 91 | AO Covenant / AO Architecture / AO Sentinel / AO Promoter / AO Command | External execution authority boundary fixture gate results | Covenant result `deny_actual_external_execution_authority_allow_fixture_boundary_evidence`, Architecture result `approve_external_execution_boundary_fixture_wording_deny_actual_external_execution_authority`, Sentinel result `clear_external_execution_boundary_fixture_evidence_hold_actual_external_execution_authority`, Promoter result `promote_public_safe_external_execution_authority_boundary_fixture_evidence_four_attempts_keep_unrestricted_self_modification_denied`, and Command readback `public_safe_external_execution_authority_boundary_fixture_evidence_four_attempts_proven_external_execution_authority_denied` approve only the external-execution-authority boundary fixture evidence class and keep actual external execution authority, provider calls, credential use, sandbox containment bypass, and unrestricted self-modification denied. |

## Execution And Readback Repositories

| Repository | RSI role | Current boundary |
| --- | --- | --- |
| `ao2` | Governed local execution runtime for bounded agent workflows, evidence packs, approvals, artifacts, evaluator closure, local RSI claim-readiness auditing, and governed self-change dry-run evidence. | AO2 contributes execution and evidence mechanics plus `ao2.rsi-claim-readiness-audit.v1`, `ao2.rsi-governed-self-change-dry-run.v1`, and a dry-run `covenant.live-self-change-authority.v1` authority-packet candidate; the current RSI claim chain does not require AO2 to call deprecated `ao-runtime` and still denies the full self-mutating claim. |
| `ao2-control-plane` | Read-only observer and evidence publication surface for AO2 evidence, release-readiness signals, AO2 RSI claim-readiness readback, AO2 self-change dry-run readback, and AO2 authority-packet candidate readback. | It observes completed evidence after the fact, emits `ao2.cp-ao2-rsi-claim-readiness-readback.v1`, `ao2.cp-ao2-rsi-self-change-dry-run-readback.v1`, and `ao2.cp-ao2-rsi-authority-packet-readback.v1`, and does not approve RSI claims, apply AO2 patches, publish claims, or mutate repositories. |

## Deprecated Or Out-Of-Scope Repositories

The current RSI claim map treats `ao-operator`, `ao-runtime`, and
`ao-control-plane` as not active RSI evidence. They are deprecated for the
active architecture and replaced by `ao2` and `ao2-control-plane` for execution
and observer-readback responsibilities. Historical references may remain in
published compatibility labels, but they must not be used as authority for a new
RSI claim.

`ao-conductor` and `agy-swarms` are outside the current AO2-first scope and are
not part of the active RSI evidence chain.

## Required Evidence Before A Stronger Claim

To move `claim_level=full_autonomous_self_mutating_rsi` from denied to allowed,
the stack needs all of the following:

1. A Covenant-approved `claim.publish` evidence ticket for
   `full-autonomous-self-mutating-rsi`.
2. A `covenant.live-self-change-authority.v1` mutation authority packet that
   names the repository, branch, allowed write surface, exact digest, approval
   identity, and expiry.
3. Rollback evidence that has been executed or rehearsed against the same change
   class and retained with digests. The current AO2 evidence satisfies this as
   temporary-workspace rehearsal for the dry-run change class, not live rollback
   of a repository mutation.
4. Live self-change evidence showing the system changed one of its own active
   planning, execution, policy, or verification paths and then re-ran the
   relevant gates.
5. Observer readback evidence for the live self-change and rollback evidence
   packet from the appropriate AO2 or ao2-control-plane surface without
   transferring approval authority to the observer.
6. Updated AO Command health and AO Forge retained evidence that publish the new
   claim-level decision and remain schema-valid.

Until those six requirements are all present and verified, the architecture
supports only bounded governed RSI wording.

The bounded RSI evidence rehearsal closure does not satisfy those six
requirements for the stronger claim. It proves only the bounded rehearsal state:
`bounded_rsi_evidence_rehearsal`.

The bounded RSI self-improvement application closure also does not satisfy those
six requirements for a broad claim. It proves only
`bounded_rsi_self_improvement_application` for the exact private readback/eval
rubric rehearsal.

The exact safe public claim wording closure does not satisfy those six
requirements for a broad claim either. It proves only
`exact_safe_public_claim_wording_conservative_readback_evidence` and only
approves this exact wording: "AO has public-safe tracked readback evidence for
bounded improvement-claim review and retraction rehearsal; stronger
recursive-improvement claims remain denied."

The public-safe bounded improvement evidence expansion closure also does not
satisfy those six requirements for a broad claim. It proves only `public_safe_bounded_improvement_evidence_expansion_four_attempts` with
four tracked public-safe bounded evidence expansion attempts and reproducibility
runbooks; stronger recursive-improvement wording remains denied.
`public_safe_reviewed_causal_chain_boundary_generalization_evidence` is proven from AO Foundry PR #187, commit `ee55f7918b86f997922707e4c0b2ba6536fe43cf`, with tracked public evidence under
`docs/evidence/recursive-improvement-reviewed-boundary-generalization/`. The approved public wording is exactly: "AO has public-safe reviewed causal-chain boundary generalization evidence across multiple independent claim-review roles; stronger recursive-improvement wording and broad_RSI remain denied." This remains prior evidence. Stronger recursive-improvement wording remains denied, and `broad_RSI`, unrestricted self-modification, hidden instruction mutation, and policy-changing autonomy remain denied.

`public_safe_intermediate_causal_review_claim_evidence` is proven from AO Foundry PR #189, commit `860e3f353ab833c4a671b9d0ee6d8101ece2815c`, with tracked public evidence under
`docs/evidence/recursive-improvement-safe-intermediate-claim/`. The approved public wording is exactly: "AO has public-safe intermediate causal-review evidence that bounded improvement evidence can guide and constrain later claim review across independent roles; stronger recursive-improvement wording and broad_RSI remain denied." This remains prior evidence. Stronger recursive-improvement wording remains denied, and `broad_RSI`, unrestricted self-modification, hidden instruction mutation, and policy-changing autonomy remain denied.

`public_safe_causal_review_evidence_selection_guidance` is proven from AO Foundry PR #191, commit `413b70f15d8f3d0203dc7be076914a2f3b539881`, with tracked public evidence under
`docs/evidence/recursive-improvement-evidence-selection-guidance/`. The approved public wording is exactly: "AO has public-safe causal-review evidence that prior bounded evidence can guide later evidence-selection and blocker prioritization under independent review gates; stronger recursive-improvement wording and broad_RSI remain denied." This advances the highest proven live class to that exact narrow class. Stronger recursive-improvement wording remains denied, and `broad_RSI`, unrestricted self-modification, hidden instruction mutation, and policy-changing autonomy remain denied.

`public_safe_guided_evidence_application_four_attempts` is proven from AO
Foundry PR #193, commit `4ec509fd64d1fc1ea41ea7f22aae900ba79e09a1`, with
tracked public evidence under
`docs/evidence/recursive-improvement-guided-evidence-application/`. The approved
public wording is exactly: "AO has public-safe guided evidence-application
evidence showing causal-review guidance can select and prioritize later bounded
evidence attempts under independent gates; stronger recursive-improvement
wording and broad_RSI remain denied." This advances the highest proven live
class to that exact narrow class. Stronger recursive-improvement wording remains
denied, and `broad_RSI`, unrestricted self-modification, hidden instruction
mutation, and policy-changing autonomy remain denied.


`public_safe_reviewer_approved_bounded_recursive_improvement_wording_evidence` is proven from AO Foundry PR #195, commit `0f742738324c185ba7243bc53ee2f1bc81804ef6`, with tracked public evidence under
`docs/evidence/recursive-improvement-reviewer-approved-wording/`. The approved public wording is exactly: "AO has public-safe reviewer-approved bounded recursive-improvement wording evidence showing guided evidence application can improve later evidence attempts under independent review gates; broad_RSI remains denied." This remains prior evidence after the segment-07 promotion. `broad_RSI`, unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, and unbounded stronger recursive-improvement claims remain denied.

`public_safe_bounded_recursive_improvement_wording_generality_evidence` is proven from AO Foundry PR #197, commit `166398641b655f0da97817659acc771026b204e7`, with tracked public evidence under
`docs/evidence/recursive-improvement-bounded-wording-generality/`. The approved public wording is exactly: "AO has public-safe bounded recursive-improvement wording generality evidence showing reviewer-approved bounded wording can transfer across additional public-safe review tasks under independent gates; broad_RSI remains denied." This remains prior evidence. `broad_RSI`, unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/dependency expansion, and unbounded stronger recursive-improvement claims remain denied.


`public_safe_recursive_improvement_claim_threshold_calibration_evidence` is proven from AO Foundry PR #201, commit `3e3d1101da112fa5ff0aca26f8ab2933652f3502`, with tracked public evidence under
`docs/evidence/recursive-improvement-claim-threshold-calibration/`, including
`docs/evidence/recursive-improvement-claim-threshold-calibration/final-rollup.json`.
The approved public wording is exactly: "AO has public-safe recursive-improvement claim threshold calibration evidence showing stronger bounded recursive-improvement claims can be evaluated against reproducible threshold, public-reader, adversarial wording, Covenant, Sentinel, rollback, and retraction gates; broad_RSI remains denied." This remains prior evidence after the segment-07 promotion. `broad_RSI`, unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/dependency expansion, and unbounded stronger recursive-improvement claims remain denied.
Promoter result
`promote_public_safe_recursive_improvement_claim_threshold_calibration_evidence_broad_RSI_denied`
and Command readback
`public_safe_recursive_improvement_claim_threshold_calibration_evidence_proven_broad_RSI_denied`
name the exact proven class while keeping `broad_RSI` denied.

The separate mutation authority ladder is narrower than this RSI claim boundary.
The current highest proven live class is
`public_safe_external_execution_authority_boundary_fixture_evidence_four_attempts`; docs-only,
test-only, low-risk-code, multi-repo low-risk, governed complex mutation, fully
unsupervised complex first non-planning, bounded evidence rehearsal, bounded
private readback/eval application evidence, conservative public-safe readback
evidence, four public-safe bounded evidence expansion attempts, reviewed
causal-chain boundary generalization, intermediate causal-review evidence,
evidence-selection guidance, guided evidence-application, bounded wording
generality, review durability, claim threshold calibration, and governed
public-safe broad_RSI campaign completion, sandbox-containment evidence,
adversarial negative-control rejection, one bounded reversible support/readback
application, repeated bounded support/readback attempts, multi-surface
support/eval negative controls, delegated dry-run authority-gap evidence, and
sandbox-boundary stress and generality evidence remain prior evidence. The
current class proves only public-safe external-execution-authority boundary
fixture evidence across four exact-scope reversible attempts under sandbox
containment gates. None of them prove actual external execution authority,
provider calls, credential use, unrestricted self-modification, sandbox
containment bypass, or unrestricted RSI.
`unrestricted_self_modification` remains denied.

## Machine-Readable Manifest

The companion manifest is
[`rsi-claim-evidence-manifest.json`](rsi-claim-evidence-manifest.json). It pins
the current cross-repo evidence snapshot, known merged PRs, claim decisions, and
out-of-scope repository map for automated audits.

## Governed Broad RSI Public-Safe Campaign Completion

`broad_RSI` is proven from AO Foundry PR #211, commit `630edc70905db745380edd1072e04b546dcccfe3`, with tracked public evidence under `docs/evidence/broad-rsi-ten-day-campaign-segment-08/`. The approved public wording is exactly: "AO has proven governed broad_RSI for public claim publication across the AO stack public-safe 10-day evidence campaign; unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, and forbidden surface expansion remain denied." The campaign completed `2800 / 2800` nodes, the segment-08 Blueprint emitted `28000 SDD slices`, and final public-reader, adversarial wording, Covenant, Architecture, Sentinel, Promoter, Command, rollback/retraction, stale-language, no-repeat, no-abandonment, and eval/regression gates passed.

This does not prove unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/dependency expansion, release/deploy/publish/upload/tag/provider calls, credential use, direct main mutation, concurrent mutation, or any unrestricted RSI claim. This remains prior evidence; the current highest proven live class is `public_safe_bounded_sandboxed_self_change_support_code_eval_four_attempts`, and the next denied class is `unrestricted_self_modification` (`next_denied_class=unrestricted_self_modification`).

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
unrestricted RSI claim. This remains prior evidence. The current highest proven live class is
`public_safe_bounded_sandboxed_self_change_multi_surface_support_eval_negative_controls_four_attempts`; the next
denied class is `unrestricted_self_modification`
(`next_denied_class=unrestricted_self_modification`).

Final gate identifiers: Covenant
`deny_unrestricted_self_modification_allow_bounded_reversible_application`,
Sentinel `clear_bounded_reversible_application_hold_unrestricted_self_modification`,
Promoter
`promote_public_safe_bounded_reversible_self_change_application_rehearsal_keep_unrestricted_self_modification_denied`,
and Command
`public_safe_bounded_reversible_self_change_application_rehearsal_proven_unrestricted_self_modification_denied`.

## Bounded Sandboxed Self-Change Applications

`public_safe_bounded_sandboxed_self_change_applications_non_readback_four_attempts`
is proven from AO Foundry PR #220, commit
`eff03edd62ba32af57defc71a7f3b800f320b8d3`, with tracked public evidence under
`docs/evidence/unrestricted-self-modification-bounded-sandbox-applications/`.
The approved public wording is exactly: "AO has public-safe bounded sandboxed
self-change application evidence across four non-readback exact-scope evidence
tasks under sandbox containment gates; unrestricted self-modification, hidden
instruction mutation, policy-changing autonomy, and forbidden surface expansion
remain denied." The run completed `140 / 140` nodes and four independent
attempts: fixture/schema evidence quality `0.68` -> `0.91`, CI/readiness
diagnostics evidence quality `0.66` -> `0.90`, public-safety rule calibration
evidence quality `0.65` -> `0.89`, and rollback/evidence-link integrity
quality `0.64` -> `0.88`.

This proves only bounded sandboxed self-change application evidence across four
non-readback exact-scope evidence tasks under sandbox containment gates. It
does not prove unrestricted self-modification, hidden instruction mutation,
policy-changing autonomy, forbidden surface expansion, policy/auth/secret/
provider/deploy/release/config/dependency expansion, credential use, provider
calls, release/deploy/publish/upload/tag authority, dependency update
authority, direct main mutation, concurrent mutation, hidden instruction
changes, or any unrestricted RSI claim. This remains prior evidence. The current highest proven live class is
`public_safe_bounded_sandboxed_self_change_multi_surface_support_eval_negative_controls_four_attempts`;
the next denied class is `unrestricted_self_modification`
(`next_denied_class=unrestricted_self_modification`).

Final gate identifiers: Covenant
`deny_unrestricted_self_modification_allow_bounded_sandbox_non_readback_applications`,
Architecture
`approve_bounded_sandbox_non_readback_wording_deny_unrestricted_self_modification_claim`,
Sentinel
`clear_bounded_sandbox_non_readback_applications_hold_unrestricted_self_modification`,
Promoter
`promote_public_safe_bounded_sandboxed_self_change_applications_non_readback_four_attempts_keep_unrestricted_self_modification_denied`,
and Command
`public_safe_bounded_sandboxed_self_change_applications_non_readback_four_attempts_proven_unrestricted_self_modification_denied`.

## Cross-Repo Documentation/Readback Sandboxed Self-Change

`public_safe_bounded_sandboxed_self_change_cross_repo_doc_readback_four_attempts`
is proven from AO Foundry PR #221, commit
`a993f4b6284de711cdb2b3fd6f006bb2706df9c8`, with tracked public evidence under
`docs/evidence/unrestricted-self-modification-cross-repo-doc-readback/`. The
approved public wording is exactly: "AO has public-safe bounded sandboxed
self-change cross-repo documentation/readback evidence across four exact-scope
documentation consistency attempts under sandbox containment gates; unrestricted
self-modification, hidden instruction mutation, policy-changing autonomy, and
forbidden surface expansion remain denied." The run completed `180 / 180`
nodes and passed Architecture source-of-truth consistency evidence quality
`0.70` -> `0.94`, component README readback parity quality `0.68` -> `0.93`,
CI/PR merge evidence linkage quality `0.67` -> `0.92`, and stale-language
denial sweep quality `0.66` -> `0.91`.

This proves only bounded sandboxed self-change cross-repo
documentation/readback evidence across four exact-scope documentation
consistency attempts under sandbox containment gates. It does not prove
unrestricted self-modification, hidden instruction mutation, policy-changing
autonomy, forbidden surface expansion, policy/auth/secret/provider/deploy/
release/config/dependency expansion, credential use, provider calls,
release/deploy/publish/upload/tag authority, dependency update authority, direct
main mutation, concurrent mutation, hidden instruction changes, or any
unrestricted RSI claim. The highest proven live class is
`public_safe_bounded_sandboxed_self_change_support_code_eval_four_attempts`;
the next denied class is `unrestricted_self_modification`
(`next_denied_class=unrestricted_self_modification`).

## Support-Code/Eval Sandboxed Self-Change

`public_safe_bounded_sandboxed_self_change_support_code_eval_four_attempts`
is proven from AO Foundry PR #222, commit
`9938df55959ac904295fd4d0dc0eddc52626c972`, with tracked public evidence under
`docs/evidence/unrestricted-self-modification-support-code-eval/`. The approved
public wording is exactly: "AO has public-safe bounded sandboxed self-change
support-code/eval evidence across four exact-scope reversible support-code and
evaluation attempts under sandbox containment gates; unrestricted
self-modification, hidden instruction mutation, policy-changing autonomy, and
forbidden surface expansion remain denied." The run completed `240 / 240`
nodes and passed support-code fixture validation quality `0.72` -> `0.95`,
eval harness diagnostics quality `0.70` -> `0.94`, rollback automation evidence
quality `0.69` -> `0.93`, and sandbox containment trace quality `0.68` ->
`0.92`.

This proves only bounded sandboxed self-change support-code/eval evidence
across four exact-scope reversible support-code and evaluation attempts under
sandbox containment gates. It does not prove unrestricted self-modification,
hidden instruction mutation, policy-changing autonomy, forbidden surface
expansion, policy/auth/secret/provider/deploy/release/config/dependency
expansion, credential use, provider calls, release/deploy/publish/upload/tag
authority, dependency update authority, direct main mutation, concurrent
mutation, hidden instruction changes, sandbox containment bypass, or any
unrestricted RSI claim. The highest proven live class is
`public_safe_bounded_sandboxed_self_change_support_code_eval_four_attempts`;
the next denied class is `unrestricted_self_modification`
(`next_denied_class=unrestricted_self_modification`).
