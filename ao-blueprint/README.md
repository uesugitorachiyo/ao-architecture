# AO Blueprint Architecture: Requirements And Build Authorization Front Door

![AO stack overview](../images/ao-stack-overview.svg)

AO Blueprint is the requirements interview, blueprint compiler, sufficiency
audit, and build-authorization front door for the AO orchestration framework.
It prevents vague objectives from entering AO Atlas, AO Foundry, AO Forge, or
AO2 as ready implementation work.

AO Blueprint does not replace AO Atlas, AO Foundry, AO Forge, AO Covenant, AO2,
AO Command, or ao2-control-plane. Its value is making the question "is this
specified enough to build?" explicit, reviewable, and evidence-bound.

## Search-Friendly Summary

AO Blueprint turns raw operator intent into reviewed blueprint packs and
machine-readable build-authorization packets. It blocks underspecified work
instead of allowing downstream factories to invent requirements during
execution.

## Component At A Glance

| Field | Value |
| --- | --- |
| Framework layer | Requirements interview, blueprint pack, sufficiency audit, and build authorization |
| Primary job | Decide whether an objective is specified enough for Atlas, Foundry, Forge, or AO2 to treat as ready |
| Owns | Blueprint pack contracts, implementation specification, quality profile, readiness audit, build authorization packet |
| Does not own | Stack-instance workgraphs, portfolio scheduling, governed execution, policy approval, provider calls, release publication, sibling repository mutation |
| Main consumers | AO Atlas, AO Foundry, AO Forge, AO Covenant, operators reviewing whether work is ready |

## Source Context

Source repository: `../../ao-blueprint`

High-signal source docs:

- `../../ao-blueprint/README.md`
- `../../ao-blueprint/docs/sdd/AO-BLUEPRINT-PRD.md`
- `../../ao-blueprint/docs/sdd/AO-BLUEPRINT-ARCHITECTURE.md`
- `../../ao-blueprint/docs/sdd/AO-BLUEPRINT-CONTRACTS.md`
- `../../ao-blueprint/docs/sdd/AO-BLUEPRINT-INTERVIEW.md`
- `../../ao-blueprint/docs/sdd/AO-BLUEPRINT-READINESS.md`
- `../../ao-blueprint/docs/sdd/AO-BLUEPRINT-ACCEPTANCE-GATES.md`
- `../../ao-blueprint/scripts/production-readiness.sh`

## Role In The AO Orchestration Framework

AO Blueprint answers:

- What objective is the operator actually authorizing?
- Which constraints, non-goals, security boundaries, contracts, tests, and
  production-readiness exits are required?
- Is the blueprint pack sufficient, or must the operator clarify it first?
- Is there a build-authorization packet that downstream tools can consume?
- Does a proposed Blueprint self-change require separate human and policy
  approval before it can be treated as ready?

The canonical path is:

```text
operator intent
-> AO Blueprint interview, sufficiency audit, and build authorization
-> AO Atlas Blueprint import and stack-instance/workgraph/context-pack compilation when scope is oversized, mutation-class, or long-running
-> AO Foundry portfolio scheduling and readiness loop
-> AO Forge governed factory run
-> AO Covenant policy and side-effect gates
-> AO2 bounded local execution and evidence
-> ao2-control-plane observer readback
-> AO Command read-only operator view
```

## Architecture

AO Blueprint is a local-first Go CLI:

- `cmd/blueprint` is the public command entrypoint.
- `internal/blueprint` implements pack validation, readiness scoring, SDD
  emission, authorization, and inspection.
- `docs/sdd` describes the product requirements, architecture, contracts,
  interview model, readiness scoring, implementation slices, and handoff model.
- `examples/blueprints` contains valid and invalid blueprint packs.
- `scripts/production-readiness.sh` runs the local verification gate.

## Workflows

### Requirements Interview Workflow

1. Capture raw operator intent.
2. Ask only the questions needed to remove build-blocking ambiguity.
3. Update the blueprint pack, implementation specification, and quality profile.
4. Score the pack against sufficiency criteria.
5. Emit a clarification request instead of a ready packet when required
   information is missing.

### Build Authorization Workflow

1. Validate the blueprint pack.
2. Confirm the readiness audit reaches the required sufficiency threshold.
3. Emit a build-authorization packet only when the pack is ready.
4. Route oversized, mutation-class, and long-running authorized objectives to
   AO Atlas for Blueprint import, workgraph, context-pack, candidate-selection,
   and Foundry import compilation.
5. Route bounded implementation slices through AO Foundry and AO Forge before
   AO2 execution.

### Blueprint Self-Change Workflow

AO Blueprint can be improved by the governed stack, but it must not authorize
its own self-change alone. Blueprint self-change requires separate human and AO
Covenant policy approval before Foundry, Forge, or AO2 treats the work as
ready.

## Agent Roles And Skills

- interviewer narrows ambiguous intent;
- sufficiency auditor checks readiness categories and blockers;
- blueprint compiler writes durable build context;
- authorization emitter produces a machine-readable packet;
- handoff preparer routes ready oversized, mutation-class, or long-running work
  through Atlas before Foundry without expanding authority.

## Contracts And Evidence

Blueprint evidence includes:

- implementation specification;
- quality profile;
- readiness audit;
- SDD emission plan;
- build-authorization packet;
- blocked clarification requests for underspecified work.

Downstream tools should consume those artifacts by reference. They should not
turn a transcript or operator idea into ready implementation work without the
authorization evidence.

## Interactions With Other Repositories

![Authority boundaries](../images/authority-boundaries.svg)

| Repository | AO Blueprint interaction |
| --- | --- |
| AO Atlas | Receives authorized oversized objectives and compiles stack-instance workgraphs, context packs, and Foundry handoff material. |
| AO Foundry | Schedules only work that is ready or explicitly authorized; does not let Blueprint authorize Foundry mutations outside the documented packet. |
| AO Forge | Receives governed factory objectives that have enough specification to plan. |
| AO Covenant | Owns policy and side-effect boundaries, including Blueprint self-change approval constraints. |
| AO2 | Executes only after downstream governance routes the authorized work. |
| AO Command | Reads Blueprint-related readiness or handoff evidence without approving or mutating it. |

## Production-Readiness Notes

- Keep Blueprint public-safe and local-first.
- Do not include private interview data in tracked examples.
- Do not let Blueprint schedule, execute, approve policy, publish, call
  providers, or mutate sibling repositories.
- Treat missing requirements as a stop condition, not as permission for a
  downstream factory to invent scope.
- Keep Blueprint self-change outside Blueprint-only approval authority.

## FAQ

### What is AO Blueprint in the AO orchestration framework?

AO Blueprint is the front-door requirements and build-authorization layer. It
turns raw intent into a reviewed, sufficient blueprint pack or blocks the work
until requirements are clear.

### Does AO Blueprint execute implementation work?

No. Blueprint authorizes readiness to build. Atlas compiles oversized work,
Foundry schedules, Forge plans a governed run, Covenant gates side effects, and
AO2 executes.

### Why does Blueprint sit before Atlas?

Atlas should compile bounded context from authorized objectives. It should not
turn an underspecified idea into a workgraph that downstream tools mistake for
approved implementation scope.

## Quick Verification

Use the source repository for live verification:

```sh
cd ../../ao-blueprint
go test ./...
go vet ./...
go run ./cmd/blueprint authorize --pack examples/blueprints/valid/ao-blueprint-self --out tmp/build-authorization.json
scripts/production-readiness.sh
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
