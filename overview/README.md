# AO Agent Orchestration Overview

![AO stack overview](../images/ao-stack-overview.svg)

This documentation explains how the active AO repositories cooperate to run AI-assisted engineering work in a governed, evidence-first way. The target reader is a colleague who needs to understand the stack well enough to review a run, explain the architecture, or decide where a new capability belongs.

The most important design decision is separation of authority. No single repository silently plans work, approves side effects, executes agent changes, stores all evidence, and presents the operator dashboard. Each repository owns one part of the factory, and the handoff between repositories is expressed as contracts, evidence, or read-only status.

## Repository Map

| Repository | Primary role | What to read next |
| --- | --- | --- |
| [AO Command](../ao-command/README.md) | Read-only operator command center | Start here when someone asks "what is happening?" |
| [AO Foundry](../ao-foundry/README.md) | Portfolio-level engineering operations factory | Use this to understand multi-repo readiness and release trains. |
| [AO Forge](../ao-forge/README.md) | Trusted factory brain for one governed run | Use this to understand GoalRun, factory plans, and release gates. |
| [AO Covenant](../ao-covenant/README.md) | Policy, contract, approval, and trust kernel | Use this to understand side-effect approval and evidence-bound trust. |
| [AO2](../ao2/README.md) | Governed local execution runtime | Use this to understand agent adapters, approvals, artifacts, and closure. |
| [ao2-control-plane](../ao2-control-plane/README.md) | Optional read-only evidence observer | Use this to understand signed ingest, storage, dashboards, and readback. |

## Practical Rule

```text
AO Command shows what is happening.
AO Foundry coordinates the portfolio.
AO Forge decides the next allowed factory step.
AO Covenant decides whether declared side effects are trusted.
AO2 executes governed work and produces evidence.
ao2-control-plane stores and exposes evidence after the fact.
```

![Authority boundaries](../images/authority-boundaries.svg)

## How A Run Moves Through The Stack

![Evidence-first workflow](../images/evidence-flow.svg)

1. An operator objective enters through the human workflow, usually surfaced through AO Command or a Foundry queue.
2. AO Foundry decides whether the repository, branch, release train, or task is ready for delegated work.
3. AO Forge converts the objective into a factory plan, GoalRun state, release gate, or operator packet.
4. AO Covenant evaluates declared side effects and produces allow, deny, block, or approval-required decisions.
5. AO2 executes the governed run through a bounded adapter such as scripted, Codex, or Claude.
6. AO2 writes run events, artifacts, exact-digest approvals, reviewer concerns, evaluator closure, and an evidence pack.
7. ao2-control-plane may ingest signed AO2 evidence and expose authenticated read APIs or dashboards.
8. AO Forge and AO Command consume the evidence to explain status, next actions, readiness, and release decisions.

## Core Workflows

### Daily Operator Workflow

Use AO Command for the first read. It is intentionally read-only and gives one command-center surface for status, stack readiness, next actions, GoalRun inspection, and evidence validation.

Then drill into the owning repository:

- AO Foundry for portfolio readiness, active-stack ledgers, release trains, and multi-repo blockers.
- AO Forge for factory plans, GoalRun transitions, production-readiness scoring, and release gates.
- AO Covenant for why a side effect was allowed, denied, blocked, or required approval.
- AO2 for what actually ran, which adapter participated, what changed, what evidence was produced, and why closure accepted or rejected the run.
- ao2-control-plane for durable observer readback after signed evidence has been published.

### Governed Implementation Workflow

The governed implementation loop starts with a task or objective and ends with evidence-bound closure. AO Forge plans the work and keeps durable GoalRun state. AO Covenant gates side effects. AO2 executes the work locally, records artifacts, and rejects closure until evidence exists. The control plane is optional and receives evidence after the fact.

### Portfolio Readiness Workflow

AO Foundry watches the active stack as a portfolio. It reads registry records, CI run evidence, release-candidate ledgers, signed-smoke gates, branch-protection status, and production-readiness rollups. It can recommend the next safe delegated action, but it delegates governed execution to AO Forge.

### Release And Promotion Workflow

Release readiness is intentionally multi-repo:

- AO Covenant provides trust primitives, release verification, signatures, schema validation, and release threat models.
- AO Forge owns release preview, install verify, release verify, rollback, promotion, retained evidence, and production-readiness gates.
- AO2 owns release-readiness evidence for the execution runtime and provider/adaptor surface.
- ao2-control-plane verifies readback for AO2 release evidence and its own release assets.
- AO Foundry rolls the active stack into a release-handoff view.
- AO Command summarizes read-only release rehearsal and governance status.

## Agent Roles And Skills

This stack uses "agent" to mean a bounded role in a governed run, not an unlimited autonomous actor.

| Role | Owned by | Skill or capability |
| --- | --- | --- |
| Operator | Human plus AO Command | Inspect status, choose next action, approve intentional gates. |
| Portfolio coordinator | AO Foundry | Select ready repositories, tasks, release trains, and readiness loops. |
| Factory planner | AO Forge | Decompose objective into GoalRun state, plans, gates, and packets. |
| Policy broker | AO Covenant | Evaluate declared side effects, approval tickets, revocations, and trust evidence. |
| Execution adapter | AO2 | Run scripted, Codex, Claude, or future provider-backed roles in a bounded sandbox. |
| Reviewer | AO2 workflow role | Emit concerns, evidence requirements, and correction requests. |
| Evaluator closer | AO2 and Covenant patterns | Accept or reject only from mapped evidence. |
| Evidence observer | ao2-control-plane | Verify, store, index, and present signed evidence after execution. |

## Contracts And Evidence

The repositories communicate through durable artifacts rather than implicit process memory:

- JSON schemas for contracts, GoalRun state, release candidates, readiness audits, provider registries, evidence packs, and control-plane summaries.
- Canonical digests and sidecar checksums for contracts, artifacts, bundles, and release assets.
- Append-only ledgers or JSONL records for events and run history.
- Operator packets, readiness rollups, release reports, and dashboard readbacks.
- CI artifacts and workflow run IDs used as public or internal evidence.

The recurring production-readiness principle is simple: if a decision matters, it should have a contract, a schema, a digest, a verification command, and a documented owner.

## Source Repositories Inspected

These overview docs were written from the public source repositories:

| Repository | Public source |
| --- | --- |
| AO Command | [uesugitorachiyo/ao-command](https://github.com/uesugitorachiyo/ao-command) |
| AO Covenant | [uesugitorachiyo/ao-covenant](https://github.com/uesugitorachiyo/ao-covenant) |
| AO Forge | [uesugitorachiyo/ao-forge](https://github.com/uesugitorachiyo/ao-forge) |
| AO Foundry | [uesugitorachiyo/ao-foundry](https://github.com/uesugitorachiyo/ao-foundry) |
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
