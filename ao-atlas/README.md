# AO Atlas Architecture: Stack-Instance Workgraph Layer

![AO stack overview](../images/ao-stack-overview.svg)

AO Atlas is the stack-instance and workgraph layer of the AO orchestration
framework. It turns oversized, mutation-class, and long-running Blueprint
output into public-safe Blueprint imports, stack-instance manifests, intake
artifacts, workgraphs, factory tasks, bounded context packs, Foundry fixture
handoff/import material, and digest-bound run-link readback.

AO Atlas does not replace AO Blueprint, AO Foundry, AO Forge, AO Covenant, AO2,
AO Command, or ao2-control-plane. Its value is preventing context-window
overflow and bulky duplicated stack folders by compiling small, evidence-bound
factory packets over one shared AO toolchain.

## Search-Friendly Summary

AO Atlas is the AO stack-instance compiler. It imports Blueprint packs and
build authorization for oversized, mutation-class, and long-running work,
decomposes large objectives into bounded factory-level workgraphs and context
packs, emits Foundry-compatible fixture material, and records readback links
without scheduling, executing, approving, publishing, calling providers, or
mutating sibling repositories.

## Component At A Glance

| Field | Value |
| --- | --- |
| Framework layer | Blueprint import, stack-instance manifests, workgraphs, context packs, and Foundry fixture handoff |
| Primary job | Compile oversized, mutation-class, and long-running Blueprint output into bounded factory tasks and public-safe readback records |
| Owns | Blueprint import contract, stack-instance contract, intake contract, workgraph contract, factory-task contract, context-pack contract, Foundry handoff/import fixtures, run-link records |
| Does not own | Requirements authorization, portfolio scheduling, governed execution, policy approval, provider calls, release publication, sibling repository mutation |
| Main consumers | AO Foundry, AO Forge, AO Blueprint, operators reviewing workgraph readiness |

## Source Context

Source repository: `../../ao-atlas`

High-signal source docs:

- `../../ao-atlas/README.md`
- `../../ao-atlas/docs/sdd/AO-ATLAS-PRD.md`
- `../../ao-atlas/docs/sdd/AO-ATLAS-ARCHITECTURE.md`
- `../../ao-atlas/docs/sdd/AO-ATLAS-CONTRACTS.md`
- `../../ao-atlas/docs/sdd/AO-ATLAS-STACK-INSTANCES.md`
- `../../ao-atlas/docs/sdd/AO-ATLAS-WORKGRAPH.md`
- `../../ao-atlas/docs/sdd/AO-ATLAS-CONTEXT-PACKS.md`
- `../../ao-atlas/docs/sdd/AO-ATLAS-FOUNDRY-HANDOFF.md`
- `../../ao-atlas/scripts/production-readiness.sh`
- `../../ao-atlas/scripts/atlas-foundry-roundtrip-smoke.sh`

## Role In The AO Orchestration Framework

AO Atlas answers:

- Which logical AO stack instance is this mission targeting?
- Which mission roots, workgraph roots, context roots, evidence roots, and
  worktree roots exist without copying AO source repositories?
- Which factory tasks are ready, blocked, failed, completed, or waiting for
  context?
- Which bounded context pack is small enough and public-safe enough to hand to a
  factory?
- Which Foundry fixture import packet and run-link readback prove the handoff is
  visible without expanding authority?

Atlas sits after AO Blueprint build authorization and before Foundry scheduling
when an objective is too large, mutation-classed, or long-running. It consumes
Blueprint packs through `ao.atlas.blueprint-import.v0.1` and should emit a
Blueprint request/blocked artifact, not a ready workgraph, when authorization
is missing, blocked, stale, or out of scope.
Foundry must not accept direct Blueprint output as ready work for these
classes; Atlas is the mandatory compiler between Blueprint and Foundry.

## Architecture

AO Atlas is a Go CLI:

- `cmd/atlas` is the public command entrypoint.
- `internal/atlas` implements validators, builders, command routing, and tests.
- `schemas` contains the public contract schemas.
- `examples/valid` and `examples/invalid` contain positive and negative
  fixtures.
- `docs/sdd` describes the product requirements, architecture, contracts,
  implementation slices, acceptance gates, and handoff model.
- `scripts/production-readiness.sh` runs the full local readiness gate.
- `scripts/atlas-foundry-roundtrip-smoke.sh` proves fixture-only Atlas ->
  Foundry import, run-link, and readback visibility against a sibling AO Foundry
  checkout.

## Workflows

### Stack-Instance Workflow

1. Create a logical stack-instance manifest with state roots and a shared AO
   toolchain root.
2. Validate that the manifest records mission, workgraph, context, evidence, and
   worktree roots without copying source repositories.
3. Emit a Foundry-compatible registry fixture when Foundry needs readback.

### Intake And Workgraph Workflow

1. Capture an oversized objective, instruction references, folder references,
   constraints, and target stack instance.
2. Emit a Blueprint request instead of pretending underspecified work is ready.
3. Compile factory-level workgraph nodes and dependency edges.
4. Use `workgraph next`, `workgraph complete`, `workgraph repair-plan`,
   `context-pack repack`, and `mission status` to keep the graph bounded.

### Mission-Scale Context Workflow

Atlas context handling is mission-scale. It manages source references, digests,
summaries, assumptions, exclusions, missing-context protocol, and budget checks
before a ready factory task is handed to Foundry.

AO2 context handling is different: AO2 shrinks and records the context for one
governed runtime slice after Foundry/Forge has selected the task. Atlas should
not run adapters or close AO2 evidence, and AO2 should not take over Atlas's
workgraph, repair-plan, or context-repack responsibilities.

### Foundry Handoff And Readback Workflow

1. Emit `ao.atlas.foundry-handoff.v0.1` and `ao.atlas.foundry-import.v0.1`
   fixture material from ready workgraph nodes.
2. Preserve factory assignment, objective, acceptance criteria, non-goals,
   safety limits, verification commands, context-pack refs, dependency refs,
   required evidence, source paths, and SHA-256 digests.
3. Fail closed when a selected node is blocked, failed, completed, missing
   context, missing factory assignment, has incomplete dependencies, or would
   imply scheduling, execution, or approval authority.
4. Ask AO Foundry to validate the import packet and public `atlas-demo` registry
   fixture.
5. Record Atlas run-link evidence with `ao.atlas.run-link.v0.1`.
6. Ask AO Foundry to emit `ao.foundry.atlas-readback.v0.1` and
   `ao.foundry.atlas-status.v0.1` observer summaries.
7. Keep the roundtrip fixture-only: no scheduling, execution, approval,
   provider calls, publication, or sibling repository mutation.

### Complex Refactor Rehearsal Workflow

AO Foundry now mirrors a realistic Atlas workgraph for a complex refactor in
`../../ao-foundry/examples/complex-refactor-workgraph/`. The fixture shows how
Atlas represents a large job without handing a whole mission to one factory:

1. one completed boundary-audit node;
2. two dependency-ready factory nodes;
3. blocked AO Command readback and stitch/integration nodes;
4. context packs for each bounded task;
5. Foundry import and run-link readback evidence for the next ready task;
6. a separate Atlas `complex_repo_mutation` rehearsal fixture with fourteen
   dry-run nodes, including context repack, repair plans, low-risk
   decomposition, rollback graph, dependency gates, and promotion gates.

`../../ao-foundry/scripts/complex-refactor-workgraph-rehearsal.sh` validates
that model with Atlas workgraph/status commands, Foundry import/readback, Pulse
gate evidence, and AO Command readback. It now also emits and validates a
Foundry import for exactly one Atlas `workgraph next` safe node. The rehearsal
proves decomposition and readback, not live execution.

The rehearsal now also mirrors Atlas repair and repack behavior for blocked
large work:

- a blocked workgraph node can emit a repair factory task that preserves
  objective, acceptance, safety, dependency, and evidence requirements;
- a `needs_context` run-link can produce a bounded replacement context pack
  with source references, digests, assumptions, exclusions, and the missing
  context reason;
- both artifacts stay fixture/readback material until Foundry chooses a safe
  delegated task.

The highest proven live mutation class is now
`fully_unsupervised_complex_mutation`. Atlas can classify and compile
workgraphs through that boundary, including repair/repack and Foundry handoff
artifacts, but it does not execute live mutation or bypass Foundry, Sentinel,
Promoter, Command, rollback, CI, branch cleanup, and class gates.

### First Docs-Only Scope Boundary

AO Atlas can feed the first-live-docs path when oversized work needs
decomposition before a docs-only request is formed. It may provide workgraph,
context-pack, Foundry import, run-link, repair, and repack evidence showing which
bounded docs task is ready and what context it received.

Atlas does not grant mutation authority. It does not approve the docs-only
ticket, schedule the live branch/PR, execute AO2 patches, publish, call
providers, or mutate sibling repositories. Execution authority comes later
through Foundry, Covenant, Forge, AO2, Sentinel, Promoter, and Command evidence.

## Agent Roles And Skills

- intake compiler records broad operator intent without claiming readiness;
- workgraph compiler turns objectives into factory-level nodes and dependencies;
- context packer creates bounded packets with source references, digests,
  assumptions, exclusions, and missing-context protocol;
- Foundry handoff emitter writes fixture material for Foundry validation;
- run-link recorder binds Foundry, Forge, or AO2 evidence paths back to Atlas
  tasks.

The core skill is context discipline: keep large missions decomposed into
bounded, evidence-backed factory packets.

## Contracts And Evidence

Atlas contracts include:

- `ao.atlas.stack-instance.v0.1`;
- `ao.atlas.intake.v0.1`;
- `ao.atlas.workgraph.v0.1`;
- `ao.atlas.factory-task.v0.1`;
- `ao.atlas.context-pack.v0.1`;
- `ao.atlas.foundry-handoff.v0.1`;
- `ao.atlas.foundry-import.v0.1`;
- `ao.atlas.run-link.v0.1`.

Foundry consumes Atlas material through fixture-only readback and emits:

- `ao.foundry.atlas-readback.v0.1`;
- `ao.foundry.atlas-status.v0.1`.

## Interactions With Other Repositories

![Evidence-first workflow](../images/evidence-flow.svg)

| Repository | AO Atlas interaction |
| --- | --- |
| AO Blueprint | Supplies requirements sufficiency and build authorization before Atlas work is treated as ready. |
| AO Foundry | Validates Atlas registry/import/readback/status artifacts and decides whether a task is schedulable. |
| AO Forge | May receive Foundry-selected factory tasks derived from Atlas workgraphs. |
| AO Covenant | Owns policy and claim boundaries for side effects; Atlas does not bypass Covenant. |
| AO2 | Executes governed work only after Foundry/Forge/Covenant route it; Atlas does not execute work directly. |
| AO Command | Can show Atlas-derived status through read-only operator surfaces. |

## Production-Readiness Notes

- Keep generated private/local instance state outside the public repository or
  under ignored paths.
- Reject absolute local paths, home paths, temp paths, credentials, and
  oversized context packs.
- Keep Foundry handoff fixture-only until an explicit governed scheduling path
  exists.
- Treat `scripts/production-readiness.sh` score `100/100` plus
  `scripts/atlas-foundry-roundtrip-smoke.sh` status `ready` as the v0.1
  readiness gate.
- Do not let Atlas schedule, execute, approve, publish, call providers, or
  mutate sibling repositories.

## FAQ

### What is AO Atlas in the AO orchestration framework?

AO Atlas is the stack-instance and workgraph compiler. It turns oversized
objectives into bounded, public-safe factory task packets and readback records.

### Does AO Atlas replace AO Foundry?

No. Atlas compiles workgraph and context material. Foundry remains the portfolio
scheduler and safe next-action selector.

### Why does AO Atlas exist?

It avoids copying whole AO stack folders for every large mission. Multiple stack
instances become lightweight logical manifests over one shared AO toolchain.

## Quick Verification

Use the source repository for live verification:

```sh
cd ../../ao-atlas
go test ./...
go vet ./...
go build ./cmd/atlas
scripts/production-readiness.sh
scripts/atlas-foundry-roundtrip-smoke.sh
```

`public_safe_guided_evidence_application_four_attempts` is proven from AO Foundry PR #193, commit
`4ec509fd64d1fc1ea41ea7f22aae900ba79e09a1`, with tracked public evidence under
`docs/evidence/recursive-improvement-guided-evidence-application/`. Four public-safe
guided evidence-application attempts are tracked with baseline and post-change
measurements: guided candidate-fit evaluation quality (`0.67` -> `0.92`),
reviewer-blocker triage quality (`0.65` -> `0.91`), cross-evidence dependency
selection quality (`0.64` -> `0.90`), and safe-next-evidence prioritization
quality (`0.62` -> `0.89`). The highest proven live class is
`public_safe_guided_evidence_application_four_attempts` and the next denied class is
`broad_RSI`. Stronger recursive-improvement wording remains denied, `broad_RSI`
remains denied, unrestricted self-modification remains denied, hidden instruction
mutation remains denied, and policy-changing autonomy remains denied.
`public_safe_bounded_recursive_improvement_wording_generality_evidence` is proven from AO Foundry PR #197, commit `166398641b655f0da97817659acc771026b204e7`, with tracked public evidence under `docs/evidence/recursive-improvement-bounded-wording-generality/`. The approved public wording is exactly: "AO has public-safe bounded recursive-improvement wording generality evidence showing reviewer-approved bounded wording can transfer across additional public-safe review tasks under independent gates; broad_RSI remains denied." The highest proven live class is `public_safe_bounded_recursive_improvement_review_durability_evidence` and the next denied class is `broad_RSI`.

This does not prove `broad_RSI`, unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/dependency expansion, or unbounded stronger recursive-improvement claims.
### Review Durability Evidence Readback

`public_safe_bounded_recursive_improvement_review_durability_evidence` is proven from AO Foundry PR #199, commit `12d524b60c200cab643e44f9105169b045602798`, with tracked public evidence under `docs/evidence/recursive-improvement-review-durability/`. The approved public wording is exactly: "AO has public-safe bounded recursive-improvement review durability evidence showing bounded recursive-improvement wording remains stable across delayed re-review, adversarial drift checks, stale-language sweeps, and reproducibility retests under independent gates; broad_RSI remains denied." The highest proven live class is `public_safe_bounded_recursive_improvement_review_durability_evidence` and the next denied class is `broad_RSI`.

This does not prove `broad_RSI`, unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/dependency expansion, or unbounded stronger recursive-improvement claims.

## Broad RSI Ten-Day Governed Campaign First Segment Readback

`public_safe_broad_RSI_governed_campaign_first_segment_state_evidence` is proven from AO Foundry PR #203, commit `b7523031d61b11df374e2203bdf44927e2d8432a`, with tracked public evidence under `docs/evidence/broad-rsi-ten-day-governed-evidence-campaign/`. The approved public wording is exactly: "AO has public-safe broad_RSI governed campaign first-segment state evidence showing a 10-day evidence campaign can start from mission-state, no-repeat, sufficiency, Pulse reliability, context-repack, rollback, and claim-gate readbacks while broad_RSI remains denied." The highest proven live class is `public_safe_broad_RSI_governed_campaign_first_segment_state_evidence` and the next denied class is `broad_RSI`.

This does not prove `broad_RSI`, full 10-day campaign completion, final repeated independent broad evidence, final cross-repo generality proof for `broad_RSI`, exact `broad_RSI` public-reader approval, exact `broad_RSI` Covenant or Architecture approval, unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/dependency expansion, release/deploy/publish/upload/tag/provider calls, credential use, direct main mutation, concurrent mutation, or unbounded stronger recursive-improvement claims.
