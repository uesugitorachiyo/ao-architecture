# AO Mission Contract Map

AO Mission is the user-entry and continuation-ledger layer. Its contracts
provide routing and readback evidence. They do not grant execution authority.

## Contracts

- `ao.mission.record.v0.1` records the durable mission objective, route, phase,
  artifacts, blockers, and exact next action.
- `ao.mission.event-loop-decision.v0.1` records each zero-wait continuation
  decision with `safe_to_execute=false`, `executes_work=false`, and
  `approves_work=false`.
- `ao.mission.scheduler-readback.v0.1` records codex-cron integration as
  scheduler wakeup substrate only.
- `ao.mission.scheduler-recovery-readback.v0.1` records missed and recovered
  wakeups as read-only recovery evidence. It can recommend governed
  continuation but cannot schedule, execute, approve, or mutate repositories.
- `covenant.scheduler-recovery-authority-denial.v1` prevents scheduler recovery
  readbacks from becoming scheduling or execution authority.
- `ao.mission.ledger-compaction-readback.v0.1` records continuation-ledger
  compaction as read-only provenance without changing authority.
- `ao.mission.timeline-compaction-readback.v0.1` records digest-bound route and
  continuation history for Atlas, Foundry, and Command.
- `ao.mission.route-decision.v0.1` records the next route, reason, and exact
  action for read-only Command inspection.
- AO Mission route-history exports are ordered
  `ao.mission.route-decision.v0.1` readbacks.
- `ao.mission.gateway-intent-ledger.v0.1` records Telegram and A2A gateway
  intents. AO Command exposes a read-only summary through
  `ao.command.mission-gateway.v0.1`.
- Telegram freshness classification marks gateway replay timestamps as fresh,
  stale, or unknown. Consumers do not assume freshness.
- The A2A fixture server readback records local Agent Card and JSON-RPC fixture
  paths without creating a running execution authority.
- `ao.mission.gateway-readiness-rollup.v0.1` records gateway replay,
  compatibility, archive-validation, and snapshot-diff provenance. An optional
  `correlation_id` connects this evidence to downstream Atlas and Foundry
  rollups.
- `ao.mission.archive.v0.1` records a digest-bound public-safe Mission archive.
- `ao.mission.archive-validation.v0.1` records archive validation before Atlas
  or Foundry consumes archive material.
- `ao.command.mission-status.v0.1` exposes Mission status to AO Command as
  read-only operator evidence.
- `ao.mission.artifact-manifest.v0.1` records artifact references and digests.
- `ao.atlas.ao-mission-import.v0.1` binds Mission records, Command status,
  artifact-manifest digests, and optional route-history, scheduler-recovery,
  ledger-compaction, timeline-compaction, archive-validation, and gateway
  readiness provenance before Atlas compiles workgraphs. Atlas blocks imports
  when a referenced artifact does not match its declared `sha256:` digest.
- `ao.atlas.ao-mission-workgraph-metadata.v0.1` binds imported Mission context
  to a validated Atlas workgraph and node-count readback.
- `ao.foundry.ao-mission-smoke-readback.v0.1` validates route and governance
  snapshot fixtures before Foundry consumes Mission output.
- `ao.foundry.ao-mission-final-rollup-smoke.v0.1` validates Mission and Foundry
  final-rollup agreement after generated nodes are consumed.
- `ao.foundry.ao-mission-readiness-ledger.v0.1` records final-rollup smoke as
  readiness-only Foundry evidence.
- `ao.foundry.ao-mission-e2e-smoke.v0.1` binds Mission, Atlas, and Foundry
  artifacts without granting execution authority. Foundry blocks schema
  mismatch, mission mismatch, authority drift, and reference-digest mismatch.

## Producer And Consumer Map

| Contract | Producer | Consumer | Authority boundary |
| --- | --- | --- | --- |
| `ao.mission.route-decision.v0.1` | AO Mission | AO Command, AO Atlas | Next-route readback only; does not execute the route. |
| AO Mission route history | AO Mission | AO Command | Ordered route-decision readback only; no scheduling, execution, or approval. |
| `ao.mission.gateway-intent-ledger.v0.1` | AO Mission | AO Command, AO Atlas | Gateway intent ledger only; no scheduling, execution, approval, or repository mutation. |
| `ao.mission.gateway-readiness-rollup.v0.1` | AO Mission | AO Atlas, AO Foundry, AO Command | Provenance only; correlation IDs do not grant authority. |
| `ao.mission.archive.v0.1` | AO Mission | AO Atlas, AO Foundry | Digest-bound archive evidence only; no scheduling, execution, approval, or repository mutation. |
| `ao.mission.archive-validation.v0.1` | AO Mission | AO Atlas, AO Foundry | Archive-validation provenance only; no execution, provider, credential, release, direct-main, or concurrent-mutation authority. |
| `ao.command.mission-gateway.v0.1` | AO Command | Operators | Read-only gateway summary; no mutation authority. |
| `ao.mission.scheduler-recovery-readback.v0.1` | AO Mission | AO Command, AO Atlas, AO Foundry | Recovery provenance only; no scheduling, execution, approval, provider, credential, release, direct-main, or concurrent-mutation authority. |
| `covenant.scheduler-recovery-authority-denial.v1` | AO Covenant | AO Mission, AO Command, AO Atlas, AO Foundry | Schema-backed denial of scheduling, execution, approval, mutation, provider, credential, publication, concurrency, and direct-main authority. |
| `ao.mission.ledger-compaction-readback.v0.1` | AO Mission | AO Command, AO Atlas, AO Foundry | Compaction provenance only; no scheduling, execution, approval, or repository mutation. |
| `ao.mission.timeline-compaction-readback.v0.1` | AO Mission | AO Command, AO Atlas, AO Foundry | Timeline provenance only; no scheduling, execution, approval, or repository mutation. |
| A2A fixture server readback | AO Mission | AO Atlas, AO Foundry, operators | Local fixture readiness only; no execution authority. |
| Telegram freshness classification | AO Mission | AO Atlas, AO Foundry, AO Command | Freshness readback only; freshness does not grant authority. |
| `ao.command.mission-evidence.v0.1` | AO Command | Operators | Read-only recovery and compaction summary; no work authority. |
| `ao.command.mission-status.v0.1` | AO Mission | AO Command, AO Atlas | Operator status readback only; no scheduling, execution, or approval. |
| `ao.mission.artifact-manifest.v0.1` | AO Mission | AO Command, AO Atlas, AO Foundry | Artifact references and digests only; no repository mutation authority. |
| `ao.atlas.ao-mission-import.v0.1` | AO Atlas | AO Atlas workgraph compiler | Digest-bound Mission import only; Atlas cannot execute work. |
| `ao.atlas.ao-mission-workgraph-metadata.v0.1` | AO Atlas | AO Foundry | Workgraph provenance only; Foundry gates execution separately. |
| `ao.foundry.ao-mission-e2e-smoke.v0.1` | AO Foundry | AO Command, operators | Cross-artifact agreement readback only; no authority. |

## Related Documentation

- [AO Mission Gateway Sequence](AO-MISSION-GATEWAY-SEQUENCE.md)
- [AO Mission Gateway Authority Map](AO-MISSION-GATEWAY-AUTHORITY-MAP.md)
- [AO Mission Recovery And Compaction Sequence](AO-MISSION-RECOVERY-COMPACTION-SEQUENCE.md)
- [AO Mission Provenance Sequence](AO-MISSION-PROVENANCE-SEQUENCE.md)
- [AO Mission v0.2 Capability Map](AO-MISSION-V0.2-CAPABILITY-MAP.md)

Telegram and A2A gateways remain intent and readback surfaces. They cannot
approve policy, execute mutation, call providers, publish releases, widen
repository authority, or bypass the AO governance chain.
