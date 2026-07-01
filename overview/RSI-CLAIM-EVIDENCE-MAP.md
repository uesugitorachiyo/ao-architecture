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
The highest proven live class remains `fully_unsupervised_complex_mutation`, the
next denied class remains `RSI`, and broad RSI, unrestricted self-modification,
hidden instruction mutation, and policy/auth/secret/provider/deploy/release/
config/dependency expansion remain denied.

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

The separate mutation authority ladder is narrower than this RSI claim boundary.
The highest proven live mutation class is
`fully_unsupervised_complex_mutation`; docs-only, test-only, low-risk-code,
multi-repo low-risk, governed complex mutation, and fully unsupervised complex
first non-planning live rehearsals do not prove live self-change, observer
readback for a live self-change, or authority to publish the full autonomous
self-mutating RSI claim. Fully unsupervised RSI remains denied.

## Machine-Readable Manifest

The companion manifest is
[`rsi-claim-evidence-manifest.json`](rsi-claim-evidence-manifest.json). It pins
the current cross-repo evidence snapshot, known merged PRs, claim decisions, and
out-of-scope repository map for automated audits.
