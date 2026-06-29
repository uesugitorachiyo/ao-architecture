# AO Agent Orchestration Overview

![AO stack overview](../images/ao-stack-overview.svg)

This documentation explains how the active AO repositories cooperate to run AI-assisted engineering work in a governed, evidence-first way. The target reader is a colleague who needs to understand the stack well enough to review a run, explain the architecture, or decide where a new capability belongs.

The most important design decision is separation of authority. No single repository silently plans work, approves side effects, executes agent changes, stores all evidence, and presents the operator dashboard. Each repository owns one part of the factory, and the handoff between repositories is expressed as contracts, evidence, or read-only status.

## Repository Map

| Repository | Primary role | What to read next |
| --- | --- | --- |
| [AO Blueprint](../ao-blueprint/README.md) | Requirements interview, blueprint pack, sufficiency audit, and build authorization | Start here when an objective is not specified enough to build. |
| [AO Atlas](../ao-atlas/README.md) | Stack-instance, workgraph, context-pack, and Foundry fixture handoff compiler | Use this to understand oversized objective decomposition before Foundry scheduling. |
| [AO Command](../ao-command/README.md) | Read-only operator command center | Start here when someone asks "what is happening?" |
| [AO Foundry](../ao-foundry/README.md) | Portfolio-level engineering operations factory | Use this to understand multi-repo readiness and release trains. |
| [AO Forge](../ao-forge/README.md) | Trusted factory brain for one governed run | Use this to understand GoalRun, factory plans, and release gates. |
| [AO Covenant](../ao-covenant/README.md) | Policy, contract, approval, and trust kernel | Use this to understand side-effect approval and evidence-bound trust. |
| [AO2](../ao2/README.md) | Governed local execution runtime | Use this to understand agent adapters, approvals, artifacts, and closure. |
| [ao2-control-plane](../ao2-control-plane/README.md) | Optional read-only evidence observer | Use this to understand signed ingest, storage, dashboards, and readback. |
| [AO Arena](../ao-arena/README.md) | Deterministic benchmark scoreboard | Use this to understand fixture-mode scoring and promotion evidence. |
| [AO Crucible](../ao-crucible/README.md) | Adversarial hardening layer | Use this to understand resilience probes and remediation gates. |
| [AO Sentinel](../ao-sentinel/README.md) | Safety and regression monitor | Use this to understand regression verdicts, incidents, and promoter holds. |
| [AO Promoter](../ao-promoter/README.md) | Gated active-stack promotion path | Use this to understand activation plans, rollback plans, and dry-run apply. |

## Practical Rule

```text
AO Command shows what is happening.
AO Blueprint decides whether an objective is specified enough to build.
AO Atlas compiles oversized objectives into stack-instance workgraphs and bounded context packs.
AO Foundry coordinates the portfolio.
AO Forge decides the next allowed factory step.
AO Covenant decides whether declared side effects are trusted.
AO2 executes governed work and produces evidence.
ao2-control-plane stores and exposes evidence after the fact.
AO Arena scores whether a candidate beats the baseline.
AO Crucible tries to break candidates before they are trusted.
AO Sentinel watches active-stack safety and regression signals.
AO Promoter activates only when all gates and rollback evidence pass.
```

![Authority boundaries](../images/authority-boundaries.svg)

## How A Run Moves Through The Stack

![Evidence-first workflow](../images/evidence-flow.svg)

1. An operator objective enters AO Blueprint when it needs requirements interview, sufficiency scoring, or build authorization.
2. AO Blueprint emits a blueprint pack and build-authorization packet, or blocks underspecified work before it reaches execution.
3. AO Atlas may compile oversized authorized objectives into stack-instance manifests, workgraphs, factory tasks, and bounded context packs without copying source repositories.
4. AO Foundry decides whether the repository, branch, release train, Atlas import/readback packet, or task is ready for delegated work.
5. AO Forge converts the objective into a factory plan, GoalRun state, release gate, or operator packet.
6. AO Covenant evaluates declared side effects and produces allow, deny, block, or approval-required decisions.
7. AO2 executes the governed run through a bounded adapter such as scripted, Codex, or Claude.
8. AO2 writes run events, artifacts, exact-digest approvals, reviewer concerns, evaluator closure, and an evidence pack.
9. ao2-control-plane may ingest signed AO2 evidence and expose authenticated read APIs or dashboards.
10. AO Arena compares baseline and challenger evidence through deterministic fixture-mode scores.
11. AO Crucible runs adversarial hardening probes and emits hardening gates or remediation briefs.
12. AO Sentinel compares active evidence against trusted baselines and emits clear, incident, or promoter-hold verdicts.
13. AO Promoter consumes Arena, Crucible, Covenant, Foundry, Forge, AO2, and Sentinel evidence to produce activation, rollback, apply dry-run, and operator reports.
14. AO Forge, AO Foundry, and AO Command consume the evidence to explain status, next actions, readiness, and release decisions.

## Core Workflows

### Daily Operator Workflow

Use AO Command for the first read. It is intentionally read-only and gives one command-center surface for status, stack readiness, next actions, GoalRun inspection, and evidence validation.

Then drill into the owning repository:

- AO Blueprint for requirements sufficiency, blueprint packs, and build authorization before work is treated as ready.
- AO Foundry for portfolio readiness, active-stack ledgers, release trains, and multi-repo blockers.
- AO Atlas for stack-instance manifests, workgraphs, context packs, Foundry fixture handoff/import, and run-link readback.
- AO Forge for factory plans, GoalRun transitions, production-readiness scoring, and release gates.
- AO Covenant for why a side effect was allowed, denied, blocked, or required approval.
- AO2 for what actually ran, which adapter participated, what changed, what evidence was produced, and why closure accepted or rejected the run.
- ao2-control-plane for durable observer readback after signed evidence has been published.
- AO Arena for deterministic benchmark scores and promotion gates.
- AO Crucible for adversarial resilience probes and remediation briefs.
- AO Sentinel for regression verdicts, incidents, and promoter holds.
- AO Promoter for activation plans and rollback-safe dry-run promotion reports.

### Governed Implementation Workflow

The governed implementation loop starts with a Blueprint-authorized task or objective and ends with evidence-bound closure. AO Atlas compiles oversized authorized objectives into bounded factory packets when needed. AO Forge plans the work and keeps durable GoalRun state. AO Covenant gates side effects. AO2 executes the work locally, records artifacts, and rejects closure until evidence exists. The control plane is optional and receives evidence after the fact.

### Context Boundary Workflow

AO Atlas handles context at mission scale. It decides how an oversized objective
is split into workgraph nodes, factory tasks, context packs, repair tasks,
context repacks, and Foundry handoff material before any one factory run starts.

AO2 handles context at governed-run scale. It receives the bounded task context
selected by Foundry/Forge, compiles local role context, runs adapters in the
runtime, records transcripts and artifacts, and can shrink or reject the run
when the evidence or context is insufficient.

The boundary prevents two common failure modes: Atlas must not execute a
context pack as if it were a runtime, and AO2 must not absorb an entire
mission-scale workgraph as one oversized run.

### Portfolio Readiness Workflow

AO Foundry watches the active stack as a portfolio. It reads registry records, CI run evidence, release-candidate ledgers, signed-smoke gates, branch-protection status, and production-readiness rollups. It can recommend the next safe delegated action, but it delegates governed execution to AO Forge.

AO Atlas sits upstream of scheduling when a mission is too large for one factory context. It emits public-safe stack-instance and workgraph artifacts, then Foundry validates `ao.atlas.foundry-import.v0.1`, `ao.foundry.atlas-readback.v0.1`, and `ao.foundry.atlas-status.v0.1` observer evidence before treating Atlas material as ready. The current Atlas import path selects only ready nodes, preserves factory assignment, acceptance criteria, safety limits, verification commands, context-pack refs, dependency refs, and required evidence, and emits explicit `schedules_work=false`, `executes_work=false`, and `approves_work=false` boundaries. Atlas does not schedule, execute, approve, publish, call providers, or mutate sibling repositories.

Pulse/event-loop startup is now a gated readback chain, not a direct runner. AO Foundry validates Blueprint/Atlas intake preflight, one-slice PR lifecycle state, and `ao.foundry.pulse-overnight-start-gate.v0.1` before overnight advancement may begin. AO Command can read those three artifacts with `pulse status` and report ready, blocked, or failed while remaining read-only. A blocked Blueprint clarification stops implementation instead of being treated as ready work.

AO Foundry now carries a fixture-only oversized-task proof for complex refactor
work. The proof uses `examples/complex-refactor-workgraph/` to model a
multi-slice refactor as Atlas factory tasks with completed, ready, blocked, and
stitch nodes. `scripts/complex-refactor-workgraph-rehearsal.sh` validates the
Atlas workgraph and context packs, Foundry import/readback, Pulse start-gate
evidence, and AO Command readback. Its summary can say that one ready factory
task may start while the overall mission remains blocked until downstream
run-link evidence exists. That is the intended behavior: Atlas decomposes and
records, Foundry gates and schedules, Command reads, and blocked work does not
start.

### First Docs-Only Live-Mutation Boundary

The first live-mutation path is intentionally tiny and docs-only. AO Foundry now
has a request -> Covenant ticket -> approval gate -> Forge guard -> AO2
docs-only patch packet -> worktree preparation -> rollback rehearsal -> Sentinel
-> Promoter -> AO Command dry-run chain for that class, plus a final
`ao.foundry.live-docs-pr-rehearsal-gate.v0.1` decision gate.

The architecture treats this as an approval-bound rehearsal path, not autonomous
mutation authority:

- `safe_to_request=true` means the docs-only class has enough dry-run evidence
  to ask for approval.
- `safe_to_execute=true` can appear only on the PR rehearsal gate when the
  explicit Covenant approval ticket is present and digest-bound.
- AO Foundry PR #98, commit
  `2e40f40cd48b9652c42dd670f9df959c930afd42`, adds the
  `ao.foundry.first-live-docs-readiness-rollup.v0.1` rollup that summarizes the
  request, ticket, gate, guard, patch packet, worktree, rollback, Sentinel,
  Promoter, and Command evidence for this first docs-only class.
- AO Command reads that gate with `live-mutation pr-rehearsal` and remains
  read-only.
- No component has authority to create branches, create worktrees, open PRs,
  merge, publish, upload, call providers, or mutate repositories from readback
  evidence alone.

Fully unsupervised complex live mutation remains outside the proven boundary.

Blocked-node repair and `needs_context` repack remain Atlas-owned artifacts.
They can become explicit factory tasks or bounded replacement context packs,
but they do not schedule or execute themselves. Foundry consumes those artifacts
as rehearsal inputs, and AO Command reads the resulting repair/repack status
from the Foundry summary so operators can see whether the next safe action is
to run one ready task, repair a blocked node, or collect missing context.

The readiness exit gate is stop-oriented. When goal readiness and competitive readiness are 100/100 and the active-stack loop passes with no `blocking_next_actions`, autonomous readiness work stops. Follow-up `maintenance_suggestions` stay separate from blockers, and live execution, signed-smoke promotion, release promotion, or new implementation work requires explicit operator intent.

### Governed RSI Evidence Workflow

The active RSI claim is a bounded, governed RSI evidence chain. AO Foundry
generates AO Foundry RSI candidate evidence, checks it through the AO Foundry
RSI improvement gate, then emits AO Foundry RSI next improvement task evidence
when the candidate and gate support the next bounded action. AO Forge retains
that evidence, AO2 emits claim-readiness plus governed self-change dry-run
summaries with a temporary-workspace rollback rehearsal and a dry-run
`covenant.live-self-change-authority.v1` authority-packet candidate,
ao2-control-plane reads those summaries and the packet back as observer-only
evidence, and AO Command verifies both Foundry pulse -> Forge retention ->
Command health and the architecture manifest's rollback-rehearsal evidence
requirements from read-only inputs.

The executable stack check for that bounded claim is AO Command's
`scripts/rsi-evidence-chain-smoke.sh`. It runs Foundry pulse evidence, checks
the retained Forge RSI proofs through Command health, and confirms the Covenant
RSI claim boundary still denies full autonomous self-mutating RSI wording when
mutation authority, Covenant-approved full-claim rollback evidence, and live
self-change evidence are missing.

This workflow can support a roughly 5 percent local recursive-improvement claim
when the candidate, gate, retained evidence, AO2 dry-run evidence, control-plane
readbacks, and command health checks all pass. It is not a claim of full
autonomous self-mutating RSI. The current architecture now pins the
mutation-authority packet shape through AO2 PR #201 and control-plane readback
through ao2-control-plane PR #73, but mutation authority and live self-change
are not proven for the full claim because that packet remains a dry-run
candidate with `schema_valid_for_claim_publish=false`. The stack keeps
repository mutation outside the default RSI health path until AO
Covenant-approved policy, rollback, live-change evidence, and observer readback
exist.

AO Covenant now treats full autonomous self-mutating RSI wording as a governed
`claim.publish` side effect. The `full-autonomous-self-mutating-rsi` resource is
denied unless an approved evidence ticket covers mutation authority, rollback
evidence, and live self-change evidence. That keeps the public architecture
aligned with the evidence actually produced by the stack. AO Covenant now
publishes `covenant.live-self-change-authority.v1` for the mutation authority
packet, but live self-change execution and observer readback remain unproven.
AO2 PR #201 emits that packet as a dry-run candidate, and ao2-control-plane PR
#73 verifies the packet hash and denial boundary without approving RSI claims,
publishing claims, applying AO2 patches, or mutating repositories.
Its retained-rollback
fixture also makes explicit that rollback rehearsal evidence alone is not enough
to publish the full self-mutating RSI claim.

Use [RSI Claim Evidence Map](RSI-CLAIM-EVIDENCE-MAP.md) for the current
cross-repo snapshot. AO Forge also retains AO Command's manifest-validation
proof so the architecture can audit the rollback rehearsal markers after the
original command run has completed, and AO Command now fails closed when those
Forge and Covenant retained evidence pins are absent. AO Forge's
`goalrun.architecture_rsi_pin_readback` production-readiness gate now also
proves this architecture pins those retained Forge RSI proofs, and AO Command
PR #33 fail-closes the manifest when that Forge PR #144 readback is absent. The
AO Command PR #34 validator also fail-closes the manifest when AO Covenant PR
#58's `covenant.live-self-change-authority.v1` authority packet schema and
fixture pins are absent. The architecture manifest now also pins AO2 PR #201's
dry-run authority-packet candidate and ao2-control-plane PR #73's observer-only
authority-packet readback so the next AO Command validator can fail-close on
those newer pins. The
companion
[`rsi-claim-evidence-manifest.json`](rsi-claim-evidence-manifest.json) pins the
known PRs, source commits, artifact paths, claim-level decisions, and deprecated
or out-of-scope repositories that must not be used as active RSI evidence.

### Release And Promotion Workflow

Release readiness is intentionally multi-repo:

- AO Covenant provides trust primitives, release verification, signatures, schema validation, and release threat models.
- AO Forge owns release preview, install verify, release verify, rollback, promotion, retained evidence, and production-readiness gates.
- AO2 owns release-readiness evidence for the execution runtime and provider/adaptor surface.
- ao2-control-plane verifies readback for AO2 release evidence and its own release assets.
- AO Arena proves benchmark wins before promotion.
- AO Crucible proves resilience against adversarial fixture probes before trust increases.
- AO Sentinel blocks promotion when public-safety or regression signals fail.
- AO Promoter combines these gates into dry-run activation and rollback evidence.
- AO Foundry rolls the active stack into a release-handoff view.
- AO Command summarizes read-only release rehearsal and governance status.

## Agent Roles And Skills

This stack uses "agent" to mean a bounded role in a governed run, not an unlimited autonomous actor.

| Role | Owned by | Skill or capability |
| --- | --- | --- |
| Operator | Human plus AO Command | Inspect status, choose next action, approve intentional gates. |
| Requirements authorizer | AO Blueprint | Interview, compile blueprint packs, score sufficiency, and emit or deny build authorization. |
| Stack-instance compiler | AO Atlas | Turn oversized objectives into bounded workgraphs, context packs, Foundry fixture import material, and run-link readback. |
| Portfolio coordinator | AO Foundry | Select ready repositories, tasks, release trains, and readiness loops. |
| Factory planner | AO Forge | Decompose objective into GoalRun state, plans, gates, and packets. |
| Policy broker | AO Covenant | Evaluate declared side effects, approval tickets, revocations, and trust evidence. |
| Execution adapter | AO2 | Run scripted, Codex, Claude, or future provider-backed roles in a bounded sandbox. |
| Reviewer | AO2 workflow role | Emit concerns, evidence requirements, and correction requests. |
| Evaluator closer | AO2 and Covenant patterns | Accept or reject only from mapped evidence. |
| Evidence observer | ao2-control-plane | Verify, store, index, and present signed evidence after execution. |
| Operator gate reader | AO Command | Read Pulse intake preflight, PR lifecycle, and overnight start-gate artifacts without starting loops or mutating repositories. |
| Benchmark scorer | AO Arena | Compare baseline and challenger outcomes from deterministic fixture evidence. |
| Adversarial probe runner | AO Crucible | Exercise candidates against controlled failure scenarios before promotion. |
| Regression monitor | AO Sentinel | Watch trusted baselines and emit holds when safety or behavior regresses. |
| Promotion activator | AO Promoter | Convert passing gates into activation, rollback, dry-run apply, and reports. |

## Contracts And Evidence

The repositories communicate through durable artifacts rather than implicit process memory:

- JSON schemas for contracts, GoalRun state, release candidates, readiness audits, provider registries, evidence packs, and control-plane summaries.
- Atlas contracts for stack instances, intake, workgraphs, factory tasks, context packs, Foundry handoff/import, run links, and Foundry observer status.
- Foundry Pulse contracts for intake preflight, one-slice PR lifecycle, overnight start gates, and read-only Command status summaries.
- Canonical digests and sidecar checksums for contracts, artifacts, bundles, and release assets.
- Append-only ledgers or JSONL records for events and run history.
- Operator packets, readiness rollups, release reports, and dashboard readbacks.
- CI artifacts and workflow run IDs used as public or internal evidence.

The recurring production-readiness principle is simple: if a decision matters, it should have a contract, a schema, a digest, a verification command, and a documented owner.

## Skills Integration

Selected reusable Codex and Claude Code agent skills are promoted into AO only
when they can become enforceable contracts or gates. The current integration
plan is documented in [AO Skills Integration SDD](AO-SKILLS-INTEGRATION-SDD.md):
AO Blueprint owns implementation-spec and quality-profile gates, AO Forge owns
context handoff and GoalRun verification validation, AO Sentinel owns CI triage
and security-review packets, and future instruction, learning, distillation,
agent-introspection, or RAG work remains deferred until explicitly needed.

## Source Repositories Inspected

These overview docs were written from the public source repositories:

| Repository | Public source |
| --- | --- |
| AO Blueprint | [uesugitorachiyo/ao-blueprint](https://github.com/uesugitorachiyo/ao-blueprint) |
| AO Atlas | [uesugitorachiyo/ao-atlas](https://github.com/uesugitorachiyo/ao-atlas) |
| AO Command | [uesugitorachiyo/ao-command](https://github.com/uesugitorachiyo/ao-command) |
| AO Arena | [uesugitorachiyo/ao-arena](https://github.com/uesugitorachiyo/ao-arena) |
| AO Covenant | [uesugitorachiyo/ao-covenant](https://github.com/uesugitorachiyo/ao-covenant) |
| AO Crucible | [uesugitorachiyo/ao-crucible](https://github.com/uesugitorachiyo/ao-crucible) |
| AO Forge | [uesugitorachiyo/ao-forge](https://github.com/uesugitorachiyo/ao-forge) |
| AO Foundry | [uesugitorachiyo/ao-foundry](https://github.com/uesugitorachiyo/ao-foundry) |
| AO Promoter | [uesugitorachiyo/ao-promoter](https://github.com/uesugitorachiyo/ao-promoter) |
| AO Sentinel | [uesugitorachiyo/ao-sentinel](https://github.com/uesugitorachiyo/ao-sentinel) |
| AO2 | [uesugitorachiyo/ao2](https://github.com/uesugitorachiyo/ao2) |
| ao2-control-plane | [uesugitorachiyo/ao2-control-plane](https://github.com/uesugitorachiyo/ao2-control-plane) |

The target folders in this repository are documentation-only mirrors for explaining the system to colleagues.

## Documentation Quality Gate

This documentation set is considered production-ready when:

- each target folder has a Markdown guide;
- every guide includes at least one image from `../images`;
- every guide explains role, architecture, workflows, agents or skills, contracts, operations, and boundaries;
- the overview explains cross-repository interaction;
- all image references resolve;
- no guide claims a repository owns authority that the source repository explicitly excludes.
