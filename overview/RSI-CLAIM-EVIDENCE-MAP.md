# RSI Claim Evidence Map

This map is the architecture-level index for recursive self-improvement claim
authority across the active AO stack. It separates what the current evidence
allows from what remains denied.

## Claim Levels

| Claim level | Current decision | Evidence status | Authority |
| --- | --- | --- | --- |
| `claim_level=bounded_governed_rsi` | Allowed | Passing local evidence can support this claim when Foundry candidate evidence, the roughly 5 percent Foundry improvement gate, Foundry next-task evidence, Forge retained proofs, Command health, the AO2 claim-readiness audit, and the Covenant boundary check all pass. | AO Foundry produces the pulse evidence, AO Forge retains it, AO Command verifies it, AO2 reports its local claim boundary, and AO Covenant preserves the wording boundary. |
| `claim_level=full_autonomous_self_mutating_rsi` | Denied | Current public artifacts do not prove mutation authority, rollback evidence, live self-change evidence, or an approved Covenant ticket for the full claim. | AO Covenant owns the `claim.publish` side-effect gate for `full-autonomous-self-mutating-rsi`. |

The current stack can describe itself as a bounded, governed RSI workflow. It
must not describe itself as full autonomous self-mutating RSI until the stronger
claim has passed the Covenant gate and the required evidence exists.

## Active Evidence Chain

| Step | Owner | Artifact or command | Claim contribution |
| --- | --- | --- | --- |
| 1 | AO Foundry | `foundry pulse run` | Produces AO Foundry RSI candidate evidence, AO Foundry RSI improvement gate evidence, and AO Foundry RSI next improvement task evidence. |
| 2 | AO Foundry | AO Foundry PR #65, commit `61e8f11fa382e3628f7f6c8f99c0758fd24430a1` | Documents that Foundry produces bounded governed RSI evidence and denies the full autonomous self-mutating RSI claim until stronger evidence exists. |
| 3 | AO Forge | `docs/evidence/goals/ao2-weekend-hardening/20260619T180000Z-verification/ao-foundry-rsi-improvement-gate-retention-proof.json` | Retains the Foundry improvement gate as auditable GoalRun evidence. |
| 4 | AO Forge | `docs/evidence/goals/ao2-weekend-hardening/20260619T180000Z-verification/ao-foundry-rsi-candidate-retention-proof.json` | Retains the Foundry candidate evidence. |
| 5 | AO Forge | `docs/evidence/goals/ao2-weekend-hardening/20260619T180000Z-verification/ao-foundry-rsi-next-improvement-task-retention-proof.json` | Retains the derived next bounded improvement task. |
| 6 | AO Forge | `docs/evidence/goals/ao2-weekend-hardening/20260619T180000Z-verification/ao-command-rsi-health-retention-proof.json` | Retains AO Command RSI health output, including claim-level decisions. |
| 7 | AO Forge | `docs/evidence/goals/ao2-weekend-hardening/20260619T180000Z-verification/bounded-rsi-improvement-chain-retention-proof.json` | Aggregates bounded RSI improvement-chain evidence with retained claim-level decisions. |
| 8 | AO Forge | AO Forge PR #142, commit `037f505a30bcff2536175b76021cfdd5f5f5a562` | Makes retained GoalRun evidence preserve `bounded_governed_rsi` allowed and `full_autonomous_self_mutating_rsi` denied decisions. |
| 9 | AO Command | `scripts/rsi-evidence-chain-smoke.sh` | Runs the executable cross-repo smoke from Foundry pulse through Forge retention, Command health, and the Covenant claim boundary. |
| 10 | AO Command | `docs/contracts/rsi-health-v0.1.schema.json` and `docs/contracts/rsi-health-bundle-v0.1.schema.json` | Requires RSI health outputs to include structured claim levels. |
| 11 | AO Command | AO Command PR #28, commit `90ff82ddcc233e5e565b012e9a2f05a0d1a0d8e0` | Adds read-only `ao-command rsi manifest --manifest` validation for this architecture manifest and wires it into CI and production readiness. |
| 12 | AO Covenant | `examples/full-rsi-claim-boundary/evidence-approved.contract.json` | Shows the allowed path for the full claim only when an approved evidence ticket names mutation authority, rollback evidence, and live self-change evidence. |
| 13 | AO Covenant | AO Covenant PR #55, commit `c5ff915d65b6159bc64df88805b52959052fd397` | Adds the full RSI claim publication boundary fixtures. |
| 14 | AO Covenant | AO Covenant PR #56, commit `60f5b4a45c0b420c9224075edd258170a549416d` | Makes Covenant policy output, operator guidance, public docs, and policy-spine gates use `bounded_governed_rsi` and `full_autonomous_self_mutating_rsi` vocabulary. |
| 15 | AO2 | `npm run rsi:claim-readiness` / `ao2.rsi-claim-readiness-audit.v1` | Emits a local read-only audit that allows `bounded_governed_rsi` and denies `full_autonomous_self_mutating_rsi` until mutation authority, rollback evidence, live self-change evidence, observer readback, and Covenant claim-publish approval exist. |
| 16 | AO2 | AO2 PR #198, commit `af86093758b13303402b825bf3b5849da88cf501` | Adds the AO2 claim-readiness audit, README boundary, and Python guard coverage for the audit contract and public trust boundary. |

## Execution And Readback Repositories

| Repository | RSI role | Current boundary |
| --- | --- | --- |
| `ao2` | Governed local execution runtime for bounded agent workflows, evidence packs, approvals, artifacts, evaluator closure, and local RSI claim-readiness auditing. | AO2 contributes execution and evidence mechanics plus `ao2.rsi-claim-readiness-audit.v1`; the current RSI claim chain does not require AO2 to call deprecated `ao-runtime` and still denies the full self-mutating claim. |
| `ao2-control-plane` | Read-only observer and evidence publication surface for AO2 evidence and release-readiness signals. | It observes completed evidence after the fact and does not approve RSI claims or mutate repositories. |

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
2. Mutation authority evidence that names the repository, branch, allowed write
   surface, exact digest, approval identity, and expiry.
3. Rollback evidence that has been executed or rehearsed against the same change
   class and retained with digests.
4. Live self-change evidence showing the system changed one of its own active
   planning, execution, policy, or verification paths and then re-ran the
   relevant gates.
5. Observer readback evidence from the appropriate AO2 or ao2-control-plane
   surface without transferring approval authority to the observer.
6. Updated AO Command health and AO Forge retained evidence that publish the new
   claim-level decision and remain schema-valid.

Until those six requirements are all present and verified, the architecture
supports only bounded governed RSI wording.

## Machine-Readable Manifest

The companion manifest is
[`rsi-claim-evidence-manifest.json`](rsi-claim-evidence-manifest.json). It pins
the current cross-repo evidence snapshot, known merged PRs, claim decisions, and
out-of-scope repository map for automated audits.
