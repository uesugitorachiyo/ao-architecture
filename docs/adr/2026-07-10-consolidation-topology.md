# ADR: Consolidation-First AO Product Topology

- Status: accepted for roadmap execution, migration not started
- Date: 2026-07-10
- Scope: the 13 active AO repositories and this Architecture repository
- Decision owner: AO Architecture, with repository owners retaining current authority

## Decision

AO will reduce release-train coordination from thirteen active component
repositories to five proposed product boundaries over the July 10, 2026 to
January 9, 2027 roadmap. This ADR records a target topology and migration
sequence. It does not claim that repositories have been moved, that a shared
workspace exists, or that any new runtime authority has been granted.

The proposed boundaries are:

| Proposed product boundary | Current repositories | Boundary responsibility |
| --- | --- | --- |
| `ao-control` | AO Mission, AO Blueprint, AO Atlas, AO Foundry, AO Forge, AO Command | Objective lifecycle, requirements, workgraph/context compilation, scheduling, per-run orchestration, and read-only operator presentation. |
| `ao2` | AO2 | Isolated local execution runtime and provider adapters. |
| `ao-covenant` | AO Covenant | Independent contract, policy, approval, trust, revocation, and key-rotation authority. |
| `ao2-control-plane` | AO2 Control Plane | Observer-only evidence ingest, durable indexed storage, verification, metrics, and read APIs. |
| `ao-assurance` | AO Arena, AO Crucible, AO Sentinel, AO Promoter | Benchmarking, adversarial probes, monitoring, and promotion decisions without activation authority. |

The current repositories remain the source of implementation truth until a
component-specific migration ADR, compatibility gate, and rollback path are
accepted. The proposed boundary names must not appear as release artifacts,
package imports, or deployment targets before those gates pass.

## Current authority map

- AO Mission owns durable mission state, routing, continuation, checkpointing,
  recovery, and lifecycle metrics. It does not approve or execute mutation.
- AO Blueprint owns requirements sufficiency, traceability, implementation
  specifications, and build authorization.
- AO Atlas owns authorized import, decomposition, context packs, workgraphs,
  and Foundry handoff material.
- AO Foundry owns portfolio readiness and one-safe-node scheduling. It does not
  grant Covenant permission or execute repository changes.
- AO Forge owns one governed GoalRun and delegates only through its gates.
- AO Command owns read-only operator presentation.
- AO Covenant owns policy decisions, approvals, trust, revocation, and contract
  authority independently of the control workspace.
- AO2 owns bounded local execution after an exact approval and transactional
  mutation guard.
- AO2 Control Plane observes and verifies evidence. Stored evidence never
  becomes approval authority.
- AO Arena and AO Crucible evaluate, AO Sentinel monitors, and AO Promoter
  decides promotion readiness. Promoter does not activate by readback alone.

## Migration order

1. Publish the stack lockfile and contract-owner registry from the checked-out
   repositories.
2. Add producer/consumer compatibility tests and canonical JSON vectors.
3. Introduce `ao-control` package boundaries behind compatibility wrappers while
   keeping the current CLIs usable.
4. Move generated evidence to an indexed observer catalog after replayable
   fixtures and retention rules are verified.
5. Consolidate the assurance packages only after independent benchmark,
   adversarial, and monitoring checks run in CI.

Every migration step requires an isolated branch, a reversible change, local
verification, CI, a reviewable PR, and post-merge branch cleanup. No step may
add provider calls, direct-main mutation, release/deploy/publish/upload/tag
authority, dependency updates, policy/auth widening, or hidden instruction
mutation.

## Rejected alternatives

- Keep thirteen independent release trains: preserves names but leaves the
  current contract and release drift unresolved.
- Continue broad RSI and mutation-ladder campaigns: increases evidence volume
  before a repeatable product path exists.
- Move immediately to a monorepo: consumes the roadmap without first defining
  stable contract ownership, rollback, and deployment boundaries.

## Exit gates for this ADR

This decision is ready for migration planning only. A migration may begin only
when all of the following are current and digest-bound:

- stack lockfile covers every active repository;
- every gate-critical contract has one producer owner and a consumer test;
- Architecture readiness includes Mission and Blueprint;
- Mission metrics distinguish implementation completion from handoff evidence;
- Arena, Crucible, and Sentinel have truthful CI/readiness coverage;
- AO2 provider execution remains explicitly opt-in and disabled for this wave;
- Promoter records `no_promotion_requested`, `promotion_granted=false`, and
  RSI remains denied.
