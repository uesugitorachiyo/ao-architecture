# AO Blueprint Design

Date: 2026-06-25

## Purpose

AO Blueprint is the front-door requirements, blueprint, and build-authorization
gate for the AO orchestration framework. It prevents raw ideas from entering an
autonomous factory loop until the user intent, constraints, acceptance criteria,
risks, operations model, and production-readiness definition are specific enough
to build against.

AO Blueprint does not execute implementation work. It interviews, audits,
compiles, and authorizes. Once the blueprint reaches the defined sufficiency
bar, it emits a machine-readable build authorization packet that AO Foundry,
AO Forge, AO Covenant, AO2, AO Arena, AO Crucible, AO Sentinel, and
AO Promoter can consume.

## Problem

The current AO stack can plan, gate, execute, evaluate, harden, monitor, and
promote work, but the quality of the result still depends heavily on the
quality of the initial objective. Short user prompts often omit domain rules,
non-goals, security constraints, operational expectations, edge cases,
acceptance criteria, and release gates. If those details are missing, an
autonomous event loop can produce polished artifacts that satisfy the prompt
literally while failing the real product intent.

AO Blueprint closes that gap by making requirements sufficiency a first-class
gate. A build cannot receive the "go sign" until the blueprint is complete,
traceable, and explicitly approved.

## Position In The AO Stack

AO Blueprint sits before AO Foundry and AO Forge.

```text
raw idea
-> AO Blueprint interview and blueprint pack
-> AO Blueprint build authorization packet
-> AO Foundry portfolio scheduling
-> AO Forge governed factory run
-> AO Covenant policy and side-effect gates
-> AO2 bounded local execution
-> AO Arena benchmark comparison
-> AO Crucible adversarial hardening
-> AO Sentinel safety and regression monitoring
-> AO Promoter gated activation
```

AO Blueprint owns the question "is this idea specified enough to build?"
It does not own portfolio scheduling, implementation execution, policy approval,
benchmark scoring, adversarial testing, active-stack monitoring, or promotion.

## Users

- Product owner who has an idea but not a complete specification.
- Engineer who wants implementation slices that are precise enough for a
  junior engineer or autonomous factory agent to execute.
- Operator who needs evidence that the AO stack should start building.
- Reviewer who needs traceability from user intent to implementation slice,
  test, acceptance gate, and production-readiness exit condition.

## Non-Goals

- AO Blueprint does not write production application code.
- AO Blueprint does not mutate repositories outside its own artifacts.
- AO Blueprint does not bypass AO Covenant policy decisions.
- AO Blueprint does not replace AO Foundry, AO Forge, AO2, or AO2 SDD planner.
- AO Blueprint does not claim that a downstream product is production-ready by
  itself. It defines the production-readiness contract that downstream gates
  must later prove.
- AO Blueprint does not ask endless questions after the sufficiency score is
  met. It stops with either `ready`, `blocked`, or `abandoned`.

## Operating Principles

1. Build nothing from vague intent.
2. Ask the next most valuable question, not every possible question.
3. Convert ambiguous adjectives into measurable criteria.
4. Separate facts, assumptions, preferences, and decisions.
5. Make every implementation slice trace back to at least one requirement.
6. Make every requirement trace forward to acceptance evidence.
7. Prefer machine-readable contracts over prose-only handoffs.
8. Fail closed when required information is missing.
9. Keep local paths, secrets, tokens, and private notes out of public artifacts.
10. Treat 100/100 as a deterministic gate, not a mood.

## Core Workflow

1. The operator starts an interview with a raw idea and optional reference
   files.
2. AO Blueprint creates an interview session with an initial project frame:
   objective, audience, domain, expected deliverable, and constraints.
3. The Intake Conductor asks one focused question at a time.
4. Specialist agents analyze each answer for missing requirements, ambiguity,
   contradictions, risk, and traceability gaps.
5. AO Blueprint updates a requirements graph and sufficiency audit after every
   answer.
6. When all required categories pass, AO Blueprint compiles the blueprint pack.
7. The user reviews the compiled blueprint and explicitly approves or requests
   changes.
8. AO Blueprint emits a build authorization packet only after approval and a
   passing sufficiency audit.
9. AO Foundry or AO Forge consumes the packet to start a governed event loop.

## Interview Model

AO Blueprint uses adaptive questioning rather than a fixed form. Each question
has a reason, target category, expected answer type, and stop condition.

Question categories:

- product goal and success metric;
- target users and roles;
- current pain and desired workflow;
- input and output artifacts;
- domain entities and lifecycle states;
- permissions and trust boundaries;
- integrations and external systems;
- data persistence and migration expectations;
- UI, CLI, API, or automation surface;
- security, privacy, compliance, and public-safety constraints;
- performance, scale, reliability, and portability expectations;
- test, eval, benchmark, and adversarial-hardening expectations;
- release, rollback, monitoring, and operational ownership;
- explicit non-goals and future deferrals.

The interview stops asking once every required category is either answered,
declared not applicable with a reason, or blocked by a user-owned decision.

## Agents

### Intake Conductor

Owns session state, chooses the next question, avoids duplicate questions, and
keeps the interview moving toward a build authorization packet.

### Ambiguity Hunter

Finds vague language such as "fast", "secure", "production ready", "simple",
"good UI", "automated", "enterprise", and "best". It converts those words into
measurable requirements or asks for a concrete threshold.

### Domain Modeler

Extracts entities, roles, states, transitions, invariants, permissions, and
edge cases. It produces a domain model that later feeds contracts, examples,
fixtures, and tests.

### Workflow Cartographer

Turns user intent into workflows, state machines, command sequences, and
operator paths. It identifies setup, daily use, failure recovery, release, and
maintenance flows.

### Contract Architect

Defines JSON contracts, CLI/API surfaces, artifact naming, schema versions, and
compatibility rules. It ensures the blueprint can feed AO2 SDD planner and AO
Forge without prose-only interpretation.

### Test And Evaluation Architect

Defines acceptance tests, fixture tests, regression tests, competitive evals,
adversarial probes, public-safety scans, and production-readiness gates.

### Security And Privacy Reviewer

Identifies secrets, local paths, token handling, sensitive inputs, destructive
actions, data retention rules, public/private artifact boundaries, and supply
chain risk.

### Operations Planner

Defines install, smoke, release, rollback, monitoring, support, and clean-clone
expectations.

### Research Watchdog

Audits external claims, cited sources, competitor references, API assumptions,
and time-sensitive facts before they influence the blueprint. Unsupported
claims are downgraded to assumptions or blocked.

### Thinking Watchdog

Audits milestone quality, drift, contradictions, missing prerequisites, weak
exit conditions, and false readiness claims. It blocks downstream authorization
when the plan scores below the required gate.

### SDD Compiler

Turns the approved blueprint into an AO2-compatible SDD plan, implementation
slices, acceptance gates, and an AO Forge or AO Foundry handoff.

### Build Authorization Gatekeeper

Emits `ready`, `blocked`, or `abandoned`. It is the only agent that can produce
the downstream build authorization packet.

## Durable Artifacts

AO Blueprint writes a blueprint pack with these artifacts:

- `project-brief.md`
- `prd.md`
- `requirements.json`
- `non-goals.md`
- `domain-model.md`
- `workflow-map.md`
- `contracts.md`
- `security-privacy.md`
- `operations-runbook.md`
- `test-evaluation-plan.md`
- `risk-register.json`
- `traceability-matrix.json`
- `sufficiency-audit.json`
- `sdd-plan.json`
- `implementation-slices.md`
- `ao-forge-handoff.md`
- `ao-foundry-task.json`
- `build-authorization.json`

Prose artifacts help humans review the plan. JSON artifacts let downstream AO
tools validate, diff, and consume the plan.

## Contract Families

The first implementation should define these contracts:

- `ao.blueprint.session.v0.1`
- `ao.blueprint.question.v0.1`
- `ao.blueprint.answer.v0.1`
- `ao.blueprint.requirement.v0.1`
- `ao.blueprint.assumption.v0.1`
- `ao.blueprint.decision.v0.1`
- `ao.blueprint.risk.v0.1`
- `ao.blueprint.traceability-matrix.v0.1`
- `ao.blueprint.sufficiency-audit.v0.1`
- `ao.blueprint.pack.v0.1`
- `ao.blueprint.sdd-plan.v0.1`
- `ao.blueprint.build-authorization.v0.1`

Each contract must include schema version, stable IDs, created/updated
metadata, public-safety classification, and validation errors that are useful
to a human operator.

## Sufficiency Score

AO Blueprint readiness is scored out of 100. A build authorization packet can
only be emitted at 100/100 with no blocking assumptions.

| Category | Points | Passing requirement |
| --- | ---: | --- |
| Objective and success metrics | 10 | Goal, users, deliverable, and success criteria are explicit. |
| Scope and non-goals | 10 | Included work, excluded work, and deferred work are separated. |
| Domain and workflows | 12 | Entities, roles, states, core flows, and edge cases are modeled. |
| Interfaces and contracts | 10 | CLI/API/UI/artifact surfaces and contract versions are defined. |
| Data and integrations | 8 | Inputs, outputs, persistence, migration, and external dependencies are defined or ruled out. |
| Security, privacy, and public safety | 10 | Secrets, sensitive data, destructive actions, and public/private boundaries are addressed. |
| Tests and evaluation | 12 | Acceptance, fixture, regression, benchmark, and adversarial checks are mapped. |
| Operations and release | 8 | Install, smoke, rollback, monitoring, and support expectations are defined. |
| Traceability | 10 | Every slice traces backward to requirements and forward to acceptance evidence. |
| User approval and build handoff | 10 | User-approved decisions, SDD plan, AO handoff, and exit conditions are present. |

Any hard blocker sets status to `blocked` even if the numeric score is high.
Hard blockers include missing production-readiness definition, unresolved
destructive-action policy, unresolved secret handling, missing acceptance gates,
or a user decision required before scope can be fixed.

## Build Authorization Packet

`ao.blueprint.build-authorization.v0.1` is the go sign for downstream AO work.

Required fields:

- `schema`
- `project_id`
- `blueprint_pack_digest`
- `status`: `ready`, `blocked`, or `abandoned`
- `score`
- `approved_by_user`
- `approved_at`
- `objective`
- `non_goals`
- `blocking_assumptions`
- `requirements_digest`
- `traceability_digest`
- `sdd_plan_path`
- `ao_forge_handoff_path`
- `ao_foundry_task_path`
- `production_readiness_exit_condition`
- `next_allowed_action`

Downstream AO automation must refuse to start implementation when status is not
`ready`, score is not `100`, approval is false, or any digest does not match.

## Error Handling

AO Blueprint fails closed.

- Missing required answer: ask a targeted follow-up.
- Contradictory answers: show the conflict and ask the user to choose.
- Unsupported external claim: downgrade to assumption or request source.
- Private or secret-like content in public artifact: block compile until
  redacted.
- SDD planner output with uncovered requirements: block authorization.
- User approval missing: compile can succeed, authorization remains blocked.
- Downstream handoff cannot be validated: build authorization remains blocked.

Errors must be emitted as structured diagnostics with code, severity, affected
artifact, human-readable explanation, and next allowed action.

## Security And Privacy

AO Blueprint treats interview answers as potentially sensitive. It must:

- separate private session state from public blueprint artifacts;
- scan durable artifacts for local paths, tokens, credentials, and private
  notes;
- avoid writing raw secrets into requirements or examples;
- record secret needs as named secret references, not secret values;
- default to fixture, dry-run, and read-only downstream examples;
- require explicit user approval before emitting public-ready artifacts;
- keep the build authorization packet free of private content.

## CLI Shape

The initial implementation should be a Go CLI for portability across Ubuntu,
Windows, and macOS.

```text
blueprint interview start
blueprint interview answer
blueprint interview status
blueprint interview next
blueprint compile
blueprint lint
blueprint readiness audit
blueprint sdd emit
blueprint authorize
blueprint pack inspect
```

A React UI can be added later as an operator console, but the CLI and contracts
must remain the source of truth.

## Storage Layout

Recommended repository layout:

```text
cmd/blueprint/
internal/cli/
internal/interview/
internal/contracts/
internal/compile/
internal/readiness/
internal/security/
internal/handoff/
docs/contracts/
docs/design/
examples/sessions/
examples/blueprints/
examples/authorizations/
```

Generated local run output belongs under `tmp/`. Durable examples and schemas
belong under `examples/` and `docs/contracts/`.

## Testing Strategy

The first production-quality implementation must include:

- schema validation tests for every contract;
- valid and invalid fixture coverage for every contract;
- interview state transition tests;
- ambiguity detection tests;
- contradiction detection tests;
- sufficiency scoring tests;
- public-safety scan tests;
- blueprint compile tests;
- SDD plan emission tests;
- build authorization denial tests;
- build authorization ready fixture tests;
- clean-clone smoke tests;
- cross-platform CI on Ubuntu, macOS, and Windows.

## Downstream Integration

AO Blueprint hands off to AO Foundry when the project requires portfolio,
multi-repo, release-train, or active-stack scheduling.

AO Blueprint hands off to AO Forge when the project is a single governed
factory run with clear scope and durable GoalRun state.

AO Blueprint may hand off directly to AO2 only for narrow local execution
experiments where Foundry and Forge orchestration would add no value. The
default path is AO Blueprint -> AO Foundry -> AO Forge -> AO2.

## Production-Readiness Exit Condition

AO Blueprint is production-ready when:

- all contracts have schemas, valid fixtures, invalid fixtures, and tests;
- all CLI commands have help, JSON output where relevant, and non-zero failure
  semantics;
- the interview loop can converge to `ready` and `blocked` from fixtures;
- build authorization fails closed on missing approval, score below 100,
  blocking assumptions, stale digests, and unsafe artifacts;
- generated SDD plans validate and preserve traceability;
- public-safety scan passes from a clean clone;
- cross-platform CI passes on Ubuntu, Windows, and macOS;
- documentation explains stack role, contracts, commands, and handoff process;
- an AO Forge or AO Foundry fixture can consume a ready authorization packet.

## Recommended First Implementation Slice

The first slice should not build the full interview intelligence. It should
establish the contract spine:

1. Go module and CLI skeleton.
2. `blueprint --help` and command routing.
3. JSON schema files for session, question, answer, sufficiency audit, pack,
   SDD plan, and build authorization.
4. Valid and invalid fixtures.
5. `blueprint lint` for contract validation and public-safety checks.
6. `blueprint readiness audit` over a fixture pack.
7. `blueprint authorize` that denies by default and allows only a complete,
   approved, 100/100 fixture pack.

After that, later slices can add adaptive question selection, richer compile
logic, SDD planner integration, and downstream AO handoff commands.
