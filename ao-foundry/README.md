# AO Foundry Architecture: Multi-Repository AI Agent Operations Factory

![AO Foundry portfolio loop](../images/ao-foundry-portfolio-loop.svg)

AO Foundry is the multi-repository engineering operations factory component of the AO orchestration framework. It coordinates repositories, goals, branches, CI signals, release trains, evidence queues, and overnight advancement loops. It delegates individual governed implementation runs to AO Forge.

Foundry does not replace Forge. Foundry decides which repository or task is ready for a next step; Forge owns the governed run.

## Search-Friendly Summary

AO Foundry is the portfolio-level scheduler for governed AI agent orchestration. It watches active repositories, readiness ledgers, release gates, and CI evidence, then decides which task is safe to delegate next while preserving execution, policy, evidence storage, and operator UX boundaries.

## Component At A Glance

| Field | Value |
| --- | --- |
| Framework layer | Multi-repository operations, scheduling, and readiness coordination |
| Primary job | Decide which repository, release train, evidence queue, or GoalRun needs the next safe step |
| Owns | Active-stack registry, readiness ledgers, portfolio board, pulse events, release handoff evidence |
| Does not own | Governed implementation execution, policy authority, observer storage, operator command UX |
| Main consumers | AO Forge, AO Command, release coordinators, overnight loop supervisors |

## Source Context

Source repository: `../../ao-foundry`

High-signal source docs:

- `../../ao-foundry/README.md`
- `../../ao-foundry/docs/design/AO-FOUNDRY-V0.1.md`
- `../../ao-foundry/docs/operations/AO2-PULSE-EVENT-LOOP.md`
- `../../ao-foundry/docs/operations/ONE-SHOT-FACTORY-RUN.md`
- `../../ao-foundry/docs/operations/READINESS-EXIT-GATE.md`
- `../../ao-foundry/docs/operations/SIGNED-SMOKE-RELEASE-GATE.md`
- `../../ao-foundry/docs/sdd/AO-FOUNDRY-PRODUCTION-READINESS-SDD.md`

## Role In The AO Orchestration Framework

AO Foundry answers:

- Which repository is ready for work?
- Which task, branch, release candidate, or evidence queue is blocked?
- Which CI or production-readiness signal changed?
- Which release-handoff gates are ready or still manual?
- What next delegated factory action is safe?
- Is the active stack still aligned across the seven active repositories that
  now include AO Atlas?

Its scope is portfolio operations. It coordinates the operating picture across repos while preserving repo-local owners for execution, policy, evidence storage, and operator command UX.

## Architecture

AO Foundry is a Go CLI with two command surfaces:

- `cmd/foundry` for portfolio registry, task, readiness, release, goal, pulse, and repo-board commands.
- `cmd/ao` for a small operator-facing status/run/demo surface.
- `internal/cli` implements command parsing and workflow logic.
- `docs/contracts` contains schemas for registry, task, run, readiness, release, GoalRun, pulse, repo health, evals, traces, and signed-smoke artifacts.
- `examples` contains active-stack registries, tasks, goals, readiness ledgers, release candidates, evals, capabilities, runs, and approvals.
- `scripts` contains active-stack readiness loops, GitHub runs reports, branch protection, and readiness rollups.

## Workflows

### Portfolio Board Workflow

1. Read the Foundry registry for active sibling repositories.
2. Classify each repository as active-spine, supporting, or blocked-hygiene.
3. Check local checkout state and expected evidence.
4. Exit non-zero when a registered sibling is dirty or otherwise blocked.
5. Use the board to clean up before strategy work begins.

### Active-Stack Readiness Workflow

1. Validate the registry and tasks.
2. Run README readiness snapshot parity.
3. Run the repo board.
4. Validate release-candidate ledgers.
5. Run loop preflight and GitHub runs report checks.
6. Produce a machine-readable active-stack readiness loop result with first failing check and next actions.
7. Stop autonomous readiness work when goal readiness and competitive readiness are 100/100 and the loop has no `blocking_next_actions`.

The loop keeps `blocking_next_actions` separate from `maintenance_suggestions` so clean readiness does not invent more implementation work. Live Forge attempts, signed-smoke promotion, release promotion, and fresh implementation require explicit operator intent after the exit gate is satisfied.

### Release Handoff Workflow

1. Validate active-spine release-candidate ledgers.
2. Validate signed-smoke release-gate summaries.
3. Emit promotion JSON, candidate notes, and release manifest.
4. Keep signed-smoke as a manual required promotion gate.

### Pulse Workflow

Foundry's pulse command writes a local evidence bundle with readiness, GoalRun, Forge brief, Forge packet, policy gate, optional live Forge attempt, control-plane readback, run record, eval, trace, demo, release dry-run, competitive audit, and a final pulse-event summary. It is a scheduler and evidence loop only; live implementation remains delegated to AO Forge.

Before autonomous overnight advancement starts, Foundry now requires a
Blueprint/Atlas-aware intake and lifecycle gate chain:

1. `foundry pulse intake-preflight` reads Blueprint build authorization or a
   blocked Blueprint clarification request and requires Atlas handoff/readback
   evidence for oversized work.
2. `foundry pulse lifecycle inspect` confirms the target repo is clean on
   synced `main`, has no active current-slice PR/check blocker, and has no
   incomplete merged-branch cleanup.
3. `foundry pulse overnight-start-gate` composes those artifacts into
   `ao.foundry.pulse-overnight-start-gate.v0.1`, requires digest-bound source
   evidence, and fails closed on failed preflight, stale digests, pending or
   failing checks, dirty worktrees, unsynced main, or cleanup gaps.

The start gate decides whether a loop may start, block, or stop. It does not
start implementation, schedule work, approve work, call providers, publish, or
mutate repositories.

Foundry also has two fixture-only proofs for the Blueprint -> Atlas -> Foundry
-> Command path:

- `scripts/blueprint-atlas-pulse-e2e-dry-run.sh` proves that a ready Blueprint
  authorization and Atlas handoff can reach a ready runner start decision while
  a blocked Blueprint request cannot produce `pulse-event.json`.
- `scripts/complex-refactor-workgraph-rehearsal.sh` proves that an oversized
  refactor can be represented as Atlas workgraph nodes, context packs, Foundry
  import/readback, Pulse start-gate evidence, and AO Command readback.
- `scripts/overnight-rehearsal-runner.sh` keeps that proof dry-run-only by
  validating the start gate, lifecycle state, Atlas import, repair/repack
  evidence, and Command-readable status before any implementation would start.
- `scripts/atlas-stress-readiness.sh` validates the larger Atlas stress
  workgraph fixture so Foundry can prove sequencing, blocked nodes, and ready
  imports without copying stack folders.

The complex refactor rehearsal reports that a next ready factory task may start
when its dependency and Pulse gate evidence are ready, while blocked downstream
tasks remain denied until completed run-link evidence exists. This is a
control-surface proof, not direct implementation. The current rehearsal also
emits and validates a one-task Foundry import for the Atlas `workgraph next`
safe node, so multiple ready nodes do not become unsafe parallel execution.

When the readiness exit gate is satisfied, the pulse summary records a stop-oriented next action instead of generating another autonomous task.

### First Docs-Only Live-Mutation Role

AO Foundry is the coordinating owner for the first tiny docs-only live-mutation
request path. It emits the operator approval request, validates the exact-scope
Covenant approval ticket, composes the approval gate, prepares worktree and
rollback rehearsal evidence, runs the approved dry-run chain, evaluates the
docs-only PR rehearsal gate, and records the
`ao.foundry.first-live-docs-readiness-rollup.v0.1` summary.

That role is still gatekeeping and coordination. Foundry does not grant policy
approval, execute AO2 patches, bypass Sentinel or Promoter, create the live
branch/PR from readback evidence alone, or broaden the approval from docs-only
to complex live mutation. `safe_to_request=true` means the request is ready for
operator review; `safe_to_execute=true` is conditional on an explicit
exact-scope approval artifact and all downstream gates.

### Mutation-Class Event-Loop Policy

Foundry's Pulse event-loop policy is a read-only continuation gate, not mutation
authority. It may continue without operator Q&A only inside the current proven
mutation class and only when class-gate, promotion-state, rollback, CI, repo
hygiene, evidence freshness, Sentinel, Promoter, branch cleanup, and scope
evidence all pass. It stops on dirty repos, stale evidence, failed CI,
broadened scope, Sentinel holds, Promoter denial, rollback failure, branch
cleanup failure, or class-jump attempts. The current proven class is
`test_only`; live `low_risk_code`, live `multi_repo_low_risk`, live
`complex_repo_mutation`, and fully unsupervised complex mutation remain denied.

## Agent Roles And Skills

Foundry coordinates higher-level operating roles:

- portfolio coordinator reads registry and readiness ledgers;
- scheduler chooses safe next tasks or backoff;
- release-train coordinator validates candidate and promotion evidence;
- repo-health reader surfaces hygiene blockers;
- overnight loop supervisor runs bounded advancement loops;
- eval and trace collector turns loop activity into evidence.

The core skill is multi-repo operating judgment: decide where attention goes next without crossing into execution or approval authority.

## Contracts And Evidence

Foundry contracts include:

- registry, task, run, and capability matrix;
- active-stack readiness and production-readiness rollup;
- release candidate, release promotion, release manifest;
- GoalRun and goal-readiness audit;
- pulse event, loop event log, loop lease, trace, eval result, eval scorecard;
- signed-smoke ingest, preflight, result, and summary;
- Pulse intake preflight, PR lifecycle, and overnight start-gate results;
- Blueprint/Atlas/Pulse e2e dry-run and complex-refactor workgraph rehearsal summaries;
- first docs-only approval request, approval gate, approved dry-run chain, and PR rehearsal gate;
- mutation-class event-loop policy with promotion-state and rollback stop gates;
- control-plane readback and Forge live attempt.

The active-stack readiness ledger is the central source for explaining whether
AO Foundry, AO Atlas, AO Forge, AO Command, AO2, ao2-control-plane, and AO
Covenant are ready.

## Interactions With Other Repositories

![AO stack overview](../images/ao-stack-overview.svg)

| Repository | AO Foundry interaction |
| --- | --- |
| AO Atlas | Supplies validated stack-instance, workgraph, Foundry import, run-link, and status readback material; Foundry validates ready-node imports but remains the scheduler. |
| AO Forge | Delegates individual governed factory runs and consumes run/gate outcomes. |
| AO Command | Reads active-stack status, Pulse gate artifacts, live-mutation readiness, and first docs-only PR rehearsal gate artifacts for read-only operator summaries. |
| AO2 | Consumes execution readiness, Pulse evidence, and release evidence. |
| ao2-control-plane | Consumes observer readback and hosted evidence signals. |
| AO Covenant | Relies on policy spine and trust evidence for release and run gates. |

## Production-Readiness Notes

- Keep Foundry local-first and public-safe by default.
- Do not push, tag, publish, upload evidence, or mutate sibling repositories in normal verification paths.
- Preserve the active-stack ledger and README snapshot parity.
- Keep archived operator/runtime/conductor/swarm repositories out of the active registry.
- Treat 100/100 readiness with no `blocking_next_actions` as a stop signal, not a reason to continue autonomous hardening.
- Treat signed-smoke promotion as manual required evidence before production promotion.

## FAQ

### What is AO Foundry in the AO orchestration framework?

AO Foundry is the portfolio operations factory. It coordinates active AO repositories, readiness ledgers, CI evidence, release handoffs, and autonomous loop stop conditions.

### Does AO Foundry execute implementation tasks directly?

No. AO Foundry decides what should happen next at the portfolio level, then delegates governed implementation runs to AO Forge.

### Why does AO Foundry stop at 100/100 readiness?

The AO framework treats readiness with no blocking next actions as an exit gate. Foundry records that state and stops autonomous hardening instead of inventing maintenance work.

## Quick Verification

Use the source repository for live verification:

```sh
cd ../../ao-foundry
go test ./...
go run ./cmd/foundry registry validate --registry examples/registry/local-ao-stack.foundry-registry.json
go run ./cmd/foundry repo board --registry examples/registry/local-ao-stack.foundry-registry.json
scripts/active-stack-readiness-loop.sh --out tmp/active-stack-readiness-loop.json
scripts/verify-branch-protection.sh
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
`public_safe_bounded_recursive_improvement_wording_generality_evidence` is proven from AO Foundry PR #197, commit `166398641b655f0da97817659acc771026b204e7`, with tracked public evidence under `docs/evidence/recursive-improvement-bounded-wording-generality/`. The approved public wording is exactly: "AO has public-safe bounded recursive-improvement wording generality evidence showing reviewer-approved bounded wording can transfer across additional public-safe review tasks under independent gates; broad_RSI remains denied." The highest proven live class is `public_safe_bounded_recursive_improvement_wording_generality_evidence` and the next denied class is `broad_RSI`.

This does not prove `broad_RSI`, unrestricted self-modification, hidden instruction mutation, policy-changing autonomy, policy/auth/secret/provider/deploy/release/config/dependency expansion, or unbounded stronger recursive-improvement claims.
