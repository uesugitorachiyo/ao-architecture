# AO Mission Architecture

![AO stack overview](../images/ao-stack-overview.svg)

AO Mission is the central AO user entry point, mission router, continuation
ledger, communication gateway, governance snapshot producer, and scheduler
adapter.

It accepts objectives from CLI, Telegram, and A2A-style local clients, records
durable mission state, and routes the next governed action to AO Blueprint, AO
Atlas, AO Foundry, AO Forge/AO2, AO Command, or a stopped/blocked readback.

## Authority Boundary

AO Mission records, routes, and reads back. It does not approve policy, execute
provider calls, mutate repositories directly, publish releases, deploy, upload,
tag releases, update dependencies, widen auth or config, or grant mutation
authority from Telegram or A2A.

codex-cron remains a scheduler/wakeup adapter only. AO2 Pulse-style semantics
remain the continuation brain. AO Blueprint remains the requirements and build
authorization front door. AO Atlas remains the workgraph/context compiler. AO
Foundry remains the implementation and portfolio execution coordinator.

Denied boundaries remain denied: unrestricted self-modification, hidden
instruction mutation, policy-changing autonomy, forbidden surface expansion,
credential use, provider calls, release/deploy/publish/upload/tag authority,
dependency update authority, direct-main mutation, concurrent mutation,
unrestricted RSI, and broad_RSI.

## Search-Friendly Summary

AO Mission turns operator objectives and gateway intents into durable mission
records, route decisions, governance snapshots, artifact references, scheduler
readbacks, and final rollups. It is the user-facing entry point for mission
state, not an execution authority.

## Component At A Glance

| Field | Value |
| --- | --- |
| Framework layer | User entry, mission routing, continuation ledger, gateway readback, and scheduler adapter |
| Primary job | Record an objective and route the next governed action to the correct AO component |
| Owns | Mission records, operator intents, route decisions, governance snapshots, scheduler requests/readbacks, gateway readbacks, artifact refs, final rollups |
| Does not own | Build authorization, workgraph compilation, implementation scheduling, governed execution, policy approval, provider calls, release publication, sibling repository mutation |
| Main consumers | Operators, AO Blueprint, AO Atlas, AO Foundry, AO Command, Telegram/A2A intent clients |

## Source Context

Source repository: `../../ao-mission`

High-signal source docs:

- `../../ao-mission/README.md`
- `../../ao-mission/docs/sdd/AO-MISSION-V0.1.md`
- `../../ao-mission/docs/contracts/`
- `../../ao-mission/examples/valid/`
- `../../ao-mission/scripts/production-readiness.sh`

## Role In The AO Orchestration Framework

AO Mission answers:

- What objective did the operator start?
- What is the durable mission id and objective digest?
- Which AO component owns the next action?
- Which governance snapshot fields prove no authority boundary widened?
- Which artifacts have been imported as readback evidence?
- Is the mission paused, stopped, active, blocked, or ready for a governed handoff?

The canonical path is:

```text
operator / CLI / Telegram / A2A intent
-> AO Mission record, route decision, and governance snapshot
-> AO Blueprint requirements and build authorization
-> AO Atlas workgraph and context compilation when required
-> AO Foundry implementation coordination
-> AO Forge / AO2 bounded governed execution
-> Covenant, Sentinel, Promoter, Command, Arena, and Crucible readbacks
-> AO Mission artifact refs and final rollup
```

## Architecture

AO Mission is a local-first Go CLI:

- `cmd/ao-mission` is the command entrypoint.
- `internal/mission` implements mission records, route decisions, continuation
  steps, imports, final rollups, gateway readbacks, and scheduler readbacks.
- `docs/contracts` contains the mission and gateway contract schemas.
- `examples/valid` and `examples/invalid` contain public-safe fixtures.
- `scripts/production-readiness.sh` runs the local verification gate.

## Workflows

### Mission Start Workflow

1. Capture an operator objective.
2. Create a mission id and objective digest.
3. Produce the first conservative route decision.
4. Record exact next action and governance snapshot fields.

### Readback Import Workflow

1. Import Blueprint authorization, Atlas workgraph, or Foundry run-link artifacts
   by reference.
2. Record artifact refs with digests.
3. Update the exact next action without setting execution flags.
4. Keep downstream components responsible for their own gates.

### Gateway Workflow

Telegram and A2A clients create intents and readbacks only. Gateway requests do
not become direct mutation authority, do not bypass Blueprint/Atlas/Foundry, and
do not approve policy.

## Contracts And Evidence

AO Mission evidence includes:

- `ao.mission.record.v0.1`;
- `ao.mission.operator-intent.v0.1`;
- `ao.mission.operator-result.v0.1`;
- `ao.mission.route-decision.v0.1`;
- `ao.mission.governance-snapshot.v0.1`;
- `ao.mission.continuation-step.v0.1`;
- `ao.mission.scheduler-request.v0.1`;
- `ao.mission.scheduler-readback.v0.1`;
- `ao.mission.telegram-command.v0.1`;
- `ao.mission.telegram-readback.v0.1`;
- `ao.mission.a2a-agent-card.v0.1`;
- `ao.mission.a2a-task.v0.1`;
- `ao.mission.artifact-ref.v0.1`;
- `ao.mission.import-readback.v0.1`;
- `ao.mission.final-rollup.v0.1`.

Every evidence record keeps AO Mission readback-oriented: schedules, executes,
approves, provider calls, direct-main mutation, and concurrent mutation remain
false unless a separate downstream gate proves otherwise.

## Interactions With Other Repositories

| Repository | AO Mission interaction |
| --- | --- |
| AO Blueprint | Receives underspecified objectives and returns build authorization readbacks. |
| AO Atlas | Receives Atlas-required authorized missions and returns workgraph/readback artifacts. |
| AO Foundry | Receives the first safe Atlas node and returns run-link/final rollup evidence. |
| AO Forge / AO2 | Execute only after downstream governed gates produce bounded packets. |
| AO Covenant | Owns policy and authority decisions; AO Mission only records the readback. |
| AO Sentinel | Emits safety holds or clears; AO Mission records the status. |
| AO Promoter | Emits promotion/no-promotion verdicts; AO Mission records the status. |
| AO Command | Remains read-only and can inspect mission/readback state. |

## Production-Readiness Notes

- Keep gateway clients intent-only.
- Keep scheduler integration as wakeup/readback only.
- Keep `safe_to_execute=false` in AO Mission governance snapshots.
- Treat handoff generation as progress, not completion.
- Preserve all higher-risk denied boundaries until separate evidence proves them.

## FAQ

### Does AO Mission execute work?

No. AO Mission routes, records, snapshots, and reads back. Execution remains in
governed downstream components.

### Why not put this in AO Command?

AO Command is read-only operator status. AO Mission owns mission creation and
continuation ledger state while still keeping execution authority elsewhere.

## Quick Verification

Use the source repository for live verification:

```sh
cd ../../ao-mission
go test ./... -count=1
go vet ./...
go build ./cmd/ao-mission
scripts/production-readiness.sh
```
