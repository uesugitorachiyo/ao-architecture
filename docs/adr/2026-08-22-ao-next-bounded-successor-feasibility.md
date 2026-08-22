# Accept AO Next For Bounded Successor Feasibility

- Status: accepted
- Date: 2026-08-22
- Scope: lifecycle and authority inventory only
- AO Next baseline: `3aff41c0c8d27b324d69a6bb65d7b4b23090da63`
- Migration authority: not granted

## Context

AO Next is a hosted experimental repository with strict request intake, deterministic effect admission, one-worker execution, durable recovery, verification, content-addressed evidence, and Mission-compatible readback work. AO Architecture did not list it in the active repository or authority inventories, so AO Mission could not activate the bounded Windows successor-feasibility handoff without contradicting portfolio truth.

AO2 remains the supported execution and rollback baseline. Existing release, cross-host, compatibility, provider, and promotion responsibilities do not move through this decision.

This decision supplements the consolidation boundaries in `docs/adr/2026-07-10-consolidation-topology.md` and is the source for the updated authority inventory.

## Decision

Accept `ao-next` as an `active_hosted` experimental execution candidate. Authorize AO Next to own only the implementation side of one separately authorized Windows successor-feasibility slice:

- objective envelope;
- Windows-native execution with exactly one worker;
- deterministic effect policy;
- durable write-ahead journal and recovery;
- mechanical verification;
- content-addressed evidence; and
- local terminal result.

AO Mission retains durable objective identity, read-only result import, continuation, checkpoints, and operator reconciliation. AO Next does not gain Mission-state, approval, promotion, provider, release, publication, deployment, migration, or production-routing authority.

The feasibility slice must stop after recording one of:

- `ADVANCE_SUCCESSOR_ARCHITECTURE`;
- `KEEP_AO_NEXT_AS_EXECUTION_KERNEL`; or
- `STOP_SUCCESSOR_WORK`.

Only `ADVANCE_SUCCESSOR_ARCHITECTURE` permits a separately authorized follow-on lifecycle decision. This ADR does not select that verdict or authorize later roadmap months.

## Consequences

- AO Next appears in the active hosted instruction layout and quality-gate registry with planned quality-gate adoption.
- The authority inventory records a bounded Windows execution-candidate domain without displacing AO2.
- Current public release manifests, tested-stack manifests, compatibility claims, and architecture diagrams remain unchanged because AO Next has not replaced or joined the supported production baseline.
- Provider calls, credentials, real repository mutation, releases, publication, deployment, promotion, and migration still require separate exact-scope authority.
