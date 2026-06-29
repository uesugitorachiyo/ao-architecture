# AO Atlas Architecture: Stack-Instance Workgraph Layer

![AO stack overview](../images/ao-stack-overview.svg)

AO Atlas is the stack-instance and workgraph layer of the AO orchestration
framework. It turns oversized objectives into public-safe stack-instance
manifests, intake artifacts, workgraphs, factory tasks, bounded context packs,
Foundry fixture handoff/import material, and digest-bound run-link readback.

AO Atlas does not replace AO Blueprint, AO Foundry, AO Forge, AO Covenant, AO2,
AO Command, or ao2-control-plane. Its value is preventing context-window
overflow and bulky duplicated stack folders by compiling small, evidence-bound
factory packets over one shared AO toolchain.

## Search-Friendly Summary

AO Atlas is the AO stack-instance compiler. It decomposes large objectives into
bounded factory-level workgraphs and context packs, emits Foundry-compatible
fixture material, and records readback links without scheduling, executing,
approving, publishing, calling providers, or mutating sibling repositories.

## Component At A Glance

| Field | Value |
| --- | --- |
| Framework layer | Stack-instance manifests, workgraphs, context packs, and Foundry fixture handoff |
| Primary job | Compile oversized objectives into bounded factory tasks and public-safe readback records |
| Owns | Stack-instance contract, intake contract, workgraph contract, factory-task contract, context-pack contract, Foundry handoff/import fixtures, run-link records |
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
when an objective is too large to hand directly to one factory run. It should
emit a Blueprint clarification request, not a ready workgraph, when the
objective is underspecified.

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
5. Foundry import and run-link readback evidence for the next ready task.

`../../ao-foundry/scripts/complex-refactor-workgraph-rehearsal.sh` validates
that model with Atlas workgraph/status commands, Foundry import/readback, Pulse
gate evidence, and AO Command readback. The rehearsal proves decomposition and
readback, not live execution.

The rehearsal now also mirrors Atlas repair and repack behavior for blocked
large work:

- a blocked workgraph node can emit a repair factory task that preserves
  objective, acceptance, safety, dependency, and evidence requirements;
- a `needs_context` run-link can produce a bounded replacement context pack
  with source references, digests, assumptions, exclusions, and the missing
  context reason;
- both artifacts stay fixture/readback material until Foundry chooses a safe
  delegated task.

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
