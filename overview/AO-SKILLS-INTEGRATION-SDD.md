# AO Skills Integration SDD

![Authority boundaries](../images/authority-boundaries.svg)

This SDD adapts selected reusable agent-skill patterns into enforceable AO
stack contracts and gates. The goal is not to copy prompt text, role rituals,
or skill procedures into AO. The goal is to extract the durable control idea,
reshape it around AO authority boundaries, and express it as machine-readable
artifacts that AO Blueprint, AO Forge, AO Foundry, AO Sentinel, and AO Covenant
can validate.

## Reviewed Inputs

The reviewed Codex skill library contains reusable workflows that are useful as
design inputs only:

- `write-implementation-spec`: convert a vague request into outcome, scope,
  stack, constraints, and verification before implementation starts.
- `manage-agent-context`: preserve long-running loop state through compact
  handoff packets and context-budget checkpoints.
- `triage-ci-observability`: turn CI, runtime, and AI-system traces into root
  cause, targeted repair, regression proof, and residual-risk summaries.
- `maintain-agent-instructions`: keep agent instructions concise, scoped, and
  consistent across runtime entrypoints.
- `promote-wiki-learning`: promote durable repeated lessons into governed
  skill or instruction updates.
- `distiller`: separate raw intake, distilled knowledge, and durable wiki
  material so raw context does not pollute the main agent loop.
- `design-rag-pipeline`: define future production retrieval architecture when
  AO needs durable evidence search or knowledge retrieval.

The reviewed Claude Code base skill library contains additional reusable
patterns. These are also design inputs only, not prompt text to copy:

- `coding-standards`: keep readability, naming, small functions, type safety,
  and YAGNI as an explicit quality floor.
- `tdd-workflow`: require failing-first tests, deterministic fixtures, and
  coverage expectations before implementation claims success.
- `eval-harness`: treat agentic behavior as eval-driven work with capability
  and regression scorecards.
- `verification-loop`: record build, type/vet, lint, tests, security scan,
  schema validation, and readiness evidence before completion claims.
- `security-review`: check secrets, input validation, authorization,
  dependencies, logging, and public artifact safety for sensitive changes.
- `agent-introspection-debugging`: capture repeated agent failure state,
  diagnose the likely class, and recover with the smallest reversible action.
- `strategic-compact` and `context-mode`: preserve context budget by writing
  durable summaries and processing large outputs outside the main prompt path.
- `product-capability`: turn product intent into explicit constraints,
  invariants, interfaces, and open decisions before planning starts.

## AO Tuning Rules

Every imported idea must be rewritten for the AO stack before implementation:

- Replace prompt-only guidance with schemas, commands, examples, tests, and
  readiness gates.
- Preserve AO authority boundaries: Blueprint asks and authorizes, Foundry
  coordinates, Forge owns GoalRun state, Covenant gates side effects, AO2
  executes, Sentinel monitors, and Promoter activates.
- Fail closed when evidence is missing, stale, unsafe, or outside the owning
  repository's authority.
- Store public-safe, repository-relative artifacts instead of private session
  memory, raw terminal scrollback, or machine-local paths.
- Keep deferred knowledge, RAG, learning, and instruction mutation outside the
  default execution loop until they have explicit contracts and Covenant gates.

## Integration Decision

AO should integrate only the workflows that can be enforced immediately:

| Input pattern | AO owner | AO-tailored contract or gate |
| --- | --- | --- |
| Implementation spec | AO Blueprint | `implementation-spec.md` required before readiness and build authorization, tuned to AO pack artifacts and downstream Foundry/Forge handoff. |
| Quality profile | AO Blueprint | `quality-profile.md` required before readiness and build authorization, tuned to AO code-quality, TDD/eval, verification-loop, and security-review gates. |
| Context handoff | AO Forge, consumed by AO Foundry and AO2 Pulse | `ao.forge.goal-run-context-handoff.v0.1` validated before loop resume, bound to a GoalRun, freshness window, resume guard, and context budget. |
| Verification loop | AO Forge | `ao.forge.goal-run-verification.v0.1` validates build, type/vet, lint, tests, contract schema, security scan, and public-readiness phases before a long-running GoalRun claims readiness. |
| CI and observability triage | AO Sentinel | `ao.sentinel.ci-signal.v0.1` -> `ao.sentinel.ci-triage.v0.1` repair packet, tuned to Forge next-task creation and non-mutating Sentinel authority. |
| Security review | AO Sentinel | `ao.sentinel.security-review-request.v0.1` -> `ao.sentinel.security-review.v0.1` clear/hold packet, tuned as a non-mutating review gate for promotion and Forge repair routing. |
| Instruction maintenance | AO Blueprint plus AO Covenant | Future governed instruction-change packet before mutating agent instructions, tuned as a policy-sensitive change rather than a documentation cleanup habit. |
| Learning promotion | AO Foundry RSI loop plus AO Covenant | Future learning-promotion queue that requires repeated evidence, reuse value, and Covenant approval before creating or updating skills. |
| Agent introspection | AO Forge plus AO Sentinel | Future failure-capture packet for repeated agent loops, tuned to GoalRun backoff and Sentinel incident evidence. |
| Distillation, RAG, and large-output processing | Future AO knowledge plane | Defer until AO needs durable retrieval over evidence and lessons, with permissions, freshness, evals, context-budget, and evidence boundaries first. |

## Implemented Slices

### Slice 1: Blueprint Implementation Spec Gate

AO Blueprint must require `implementation-spec.md` in every ready blueprint
pack. The artifact must define outcome, scope, stack, constraints, and
verification so SDD generation has a concrete build contract rather than only a
high-level interview transcript.

Acceptance:

- `blueprint compile` emits `implementation-spec.md`.
- `blueprint readiness audit` blocks when the artifact is missing.
- The valid self-pack includes a public-safe implementation spec.

### Slice 2: Forge Context Handoff Gate

AO Forge must validate context handoffs before overnight or long-running loops
resume. The handoff records current task, completed work, decisions, files
touched, next steps, open questions, and context budget.

Acceptance:

- `forge goal context validate` validates a handoff against a GoalRun.
- Handoffs fail closed when they target the wrong GoalRun, disable the resume
  guard, exceed the budget, use future timestamps, or are older than 24 hours.
- The context handoff schema and example are documented as GoalRun contract
  surface.

### Slice 3: Sentinel CI Triage Packet

AO Sentinel must convert CI and observability signals into deterministic repair
packets. A failing CI signal should become a bounded AO Forge task with root
cause, severity, recommended action, triage steps, and regression-test
requirement.

Acceptance:

- `sentinel triage ci` emits `ao.sentinel.ci-triage.v0.1`.
- Passing signals produce `observed`; failing signals produce
  `repair_required`.
- Contract-schema, timeout, public-safety, flaky-test, and generic CI failures
  are classified without mutating live state.

### Slice 4: Blueprint Quality Profile Gate

AO Blueprint must require a quality profile before authorizing downstream
implementation. This adapts Claude Code base quality, TDD, eval, verification,
and security-review practices into a concise AO-owned artifact.

Acceptance:

- `blueprint compile` emits `quality-profile.md`.
- `blueprint readiness audit` blocks when the artifact is missing.
- The valid self-pack includes a public-safe quality profile.

### Slice 5: Forge GoalRun Verification Evidence

AO Forge must validate non-mutating verification packets before long-running
GoalRuns claim readiness or resume after major implementation work.

Acceptance:

- `forge goal verification validate` validates
  `ao.forge.goal-run-verification.v0.1`.
- The command fails closed when required phases are missing, skipped, failed,
  or lack command/evidence.
- The fixture smoke validates the positive fixture and rejects a semantic
  negative fixture.

### Slice 6: Sentinel Security Review Packet

AO Sentinel must convert requested security scopes and evidence into a clear or
hold packet without mutating live state.

Acceptance:

- `sentinel security review` emits `ao.sentinel.security-review.v0.1`.
- Missing evidence for requested scopes produces a hold and recommended Forge
  repair actions.
- Clear requests produce non-mutating clear packets.

## Future Slices

### Slice 7: Governed Instruction Change

AO Blueprint should model instruction changes as first-class build artifacts,
and AO Covenant should treat instruction mutation as policy-sensitive. This
prevents root instruction bloat and contradictory role rules from entering the
active stack.

### Slice 8: Learning Promotion Queue

AO Foundry should collect repeated incident lessons, eval failures, and repair
patterns as learning candidates. AO Covenant should approve promotion only when
the lesson is reusable, evidence-backed, concise, and not already covered by an
existing skill.

### Slice 9: Distilled Knowledge Plane

If AO later needs searchable run history, design a separate AO knowledge plane
that follows the raw -> distilled -> durable knowledge boundary. Retrieval,
RAG, or wiki ingestion must stay outside the core policy and execution path
until it has permissions, evals, and freshness controls.

## Exit Criteria

This integration is ready when the first six slices are implemented with tests,
public-safe examples, and verification commands in their owning repositories.
Later slices should not start until the operator explicitly wants instruction
governance, learning promotion, agent introspection packets, or knowledge
retrieval as product features.
