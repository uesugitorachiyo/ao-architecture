# AO Architecture: AI Agent Orchestration Stack For Evidence-First Agentic Factories

![AO stack overview](images/ao-stack-overview.svg)

AO Architecture documents a multi-repository AI agent orchestration stack for governed autonomous software engineering. It explains how AO Foundry, AO Forge, AO Covenant, AO2, ao2-control-plane, and AO Command work together as an evidence-first agentic factory: choosing work, gating policy, executing bounded agent runs, preserving evidence, exposing read-only status, and stopping when readiness gates are satisfied.

Use this documentation to understand the AO stack's architecture, authority boundaries, agent workflows, contracts, production-readiness gates, and evidence trails. The focus is practical orchestration: how agent work moves from portfolio scheduling to governed factory planning, local execution, policy decisions, control-plane readback, and operator-facing status.

## What Is The AO Stack?

The AO stack is a set of open architecture documents for building and operating governed AI agent systems. Instead of treating agent automation as a single chat session or unbounded background worker, the stack splits responsibility across small tools with clear boundaries:

- AO Foundry coordinates multi-repository engineering operations and readiness loops.
- AO Forge turns an objective into a governed factory run with durable GoalRun state.
- AO Covenant gates policy, trust, side effects, release bundles, and evidence contracts.
- AO2 executes bounded local agent workflows and records artifacts, decisions, approvals, and evaluator closure evidence.
- ao2-control-plane publishes observer evidence without becoming an approval authority.
- AO Command gives operators a read-only status and command surface for the active stack.

That separation is the core idea: AI agent orchestration should be inspectable, evidence-backed, policy-gated, and stoppable.

## Architecture Video

[![AO Architecture video walkthrough](https://img.youtube.com/vi/P0JbsTKItEA/maxresdefault.jpg)](https://youtu.be/P0JbsTKItEA?si=KYaWmZbymO4kRMlK)

Watch the video walkthrough: [AO Architecture on YouTube](https://youtu.be/P0JbsTKItEA?si=KYaWmZbymO4kRMlK). The walkthrough introduces the active AO agent orchestration architecture, including repository roles, evidence-first workflow, policy boundaries, and production-readiness gates.

## AO Stack At A Glance

| Repository | Role in the AI agent orchestration stack | Start here |
| --- | --- | --- |
| `ao-foundry` | Engineering operations factory for multi-repo scheduling, readiness, release trains, and autonomous loop stop conditions. | [AO Foundry Architecture](ao-foundry/README.md) |
| `ao-forge` | Governed factory brain for GoalRun state, factory plans, Covenant gates, AO2 delegation, and operator evidence packets. | [AO Forge Architecture](ao-forge/README.md) |
| `ao-covenant` | Policy and trust layer for side-effect decisions, release bundles, signatures, schemas, and evidence contracts. | [AO Covenant Architecture](ao-covenant/README.md) |
| `ao2` | Governed local execution runtime for bounded agent workflows, approvals, artifacts, evidence packs, and evaluator closure. | [AO2 Architecture](ao2/README.md) |
| `ao2-control-plane` | Read-only observer and evidence publication surface for AO2 and release-readiness signals. | [ao2-control-plane Architecture](ao2-control-plane/README.md) |
| `ao-command` | Operator-facing status and command surface for viewing the active stack without crossing approval boundaries. | [AO Command Architecture](ao-command/README.md) |

## Start Here

1. [Overview](overview/README.md) explains how all repositories interact.
2. [Production Readiness Checklist](overview/PRODUCTION-READINESS.md) explains the quality bar for this documentation pack.
3. Read individual repository guides when you need implementation detail:

| Folder | Guide |
| --- | --- |
| `ao-command` | [AO Command Architecture](ao-command/README.md) |
| `ao-covenant` | [AO Covenant Architecture](ao-covenant/README.md) |
| `ao-forge` | [AO Forge Architecture](ao-forge/README.md) |
| `ao-foundry` | [AO Foundry Architecture](ao-foundry/README.md) |
| `ao2` | [AO2 Architecture](ao2/README.md) |
| `ao2-control-plane` | [ao2-control-plane Architecture](ao2-control-plane/README.md) |

## Why This Architecture Matters

Most AI coding agent systems struggle with the same production questions: who is allowed to act, what evidence proves the action happened, which policy gate approved or denied it, when should the loop stop, and how can an operator inspect the result later? AO Architecture answers those questions with explicit repository ownership and machine-readable contracts.

The stack is designed around:

- evidence-first agent workflows;
- policy-gated side effects;
- bounded local execution instead of unbounded autonomy;
- production-readiness and release-readiness gates;
- clean separation between execution, policy, orchestration, observer storage, and operator UX;
- stop conditions that prevent autonomous loops from inventing work after readiness is satisfied.

## Visual Map

Shared images are stored in [images](images/). Each repository guide references at least one diagram from this shared folder.

![Evidence-first workflow](images/evidence-flow.svg)

## Documentation Scope

These docs describe the target folders as architecture documentation mirrors. The source repositories inspected are:

| Source repository | Architecture guide |
| --- | --- |
| [ao-command](https://github.com/uesugitorachiyo/ao-command) | [ao-command](ao-command/README.md) |
| [ao-covenant](https://github.com/uesugitorachiyo/ao-covenant) | [ao-covenant](ao-covenant/README.md) |
| [ao-forge](https://github.com/uesugitorachiyo/ao-forge) | [ao-forge](ao-forge/README.md) |
| [ao-foundry](https://github.com/uesugitorachiyo/ao-foundry) | [ao-foundry](ao-foundry/README.md) |
| [ao2](https://github.com/uesugitorachiyo/ao2) | [ao2](ao2/README.md) |
| [ao2-control-plane](https://github.com/uesugitorachiyo/ao2-control-plane) | [ao2-control-plane](ao2-control-plane/README.md) |

The documentation does not copy every source README. It extracts the operational model colleagues need: role, architecture, workflows, agent boundaries, skills or capabilities, contracts, evidence, and production-readiness expectations.

## FAQ

### Is AO Architecture an AI agent framework?

AO Architecture is a documentation mirror for a stack of AI agent orchestration repositories. The implementation lives in the linked source repositories. This repository explains the architecture, authority boundaries, workflows, contracts, and evidence model across the stack.

### What makes AO different from a single autonomous coding agent?

AO separates portfolio scheduling, factory planning, policy decisions, execution, evidence publication, and operator status into different repositories. That makes agent work easier to inspect, test, stop, and review.

### What is an evidence-first agent workflow?

An evidence-first workflow records structured artifacts for the work an agent performed: plans, policy decisions, approvals, command output, changed files, test results, reports, evidence packs, readiness audits, and closure decisions. The operator can inspect evidence instead of trusting terminal scrollback.

### Where should I start?

Start with [Overview](overview/README.md), then read [AO Foundry Architecture](ao-foundry/README.md) for the portfolio-level factory loop, [AO Forge Architecture](ao-forge/README.md) for governed factory runs, and [AO2 Architecture](ao2/README.md) for local execution and evidence capture.

## License

AO Architecture is licensed under `Apache-2.0`. See `LICENSE`.
