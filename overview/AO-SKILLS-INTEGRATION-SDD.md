# AO Skills Integration SDD

![Authority boundaries](../images/authority-boundaries.svg)

This SDD adapts selected reusable agent-skill patterns into enforceable AO
stack contracts and gates. The goal is not to copy prompt text, role rituals,
or skill procedures into AO. The goal is to extract the durable control idea,
reshape it around AO authority boundaries, and express it as machine-readable
artifacts that AO Blueprint, AO Forge, AO Foundry, AO Sentinel, and AO Covenant
can validate.

## Reviewed Inputs

The reviewed skill library contains reusable workflows that are useful as
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
| Context handoff | AO Forge, consumed by AO Foundry and AO2 Pulse | `ao.forge.goal-run-context-handoff.v0.1` validated before loop resume, bound to a GoalRun, freshness window, resume guard, and context budget. |
| CI and observability triage | AO Sentinel | `ao.sentinel.ci-signal.v0.1` -> `ao.sentinel.ci-triage.v0.1` repair packet, tuned to Forge next-task creation and non-mutating Sentinel authority. |
| Instruction maintenance | AO Blueprint plus AO Covenant | Future governed instruction-change packet before mutating agent instructions, tuned as a policy-sensitive change rather than a documentation cleanup habit. |
| Learning promotion | AO Foundry RSI loop plus AO Covenant | Future learning-promotion queue that requires repeated evidence, reuse value, and Covenant approval before creating or updating skills. |
| Distillation and RAG | Future AO knowledge plane | Defer until AO needs durable retrieval over evidence and lessons, with permissions, freshness, evals, and evidence boundaries first. |

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

## Future Slices

### Slice 4: Governed Instruction Change

AO Blueprint should model instruction changes as first-class build artifacts,
and AO Covenant should treat instruction mutation as policy-sensitive. This
prevents root instruction bloat and contradictory role rules from entering the
active stack.

### Slice 5: Learning Promotion Queue

AO Foundry should collect repeated incident lessons, eval failures, and repair
patterns as learning candidates. AO Covenant should approve promotion only when
the lesson is reusable, evidence-backed, concise, and not already covered by an
existing skill.

### Slice 6: Distilled Knowledge Plane

If AO later needs searchable run history, design a separate AO knowledge plane
that follows the raw -> distilled -> durable knowledge boundary. Retrieval,
RAG, or wiki ingestion must stay outside the core policy and execution path
until it has permissions, evals, and freshness controls.

## Exit Criteria

This integration is ready when the first three slices are implemented with
tests, public-safe examples, and verification commands in their owning
repositories. Later slices should not start until the operator explicitly wants
instruction governance, learning promotion, or knowledge retrieval as product
features.
