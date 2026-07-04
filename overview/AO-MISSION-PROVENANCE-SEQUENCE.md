# AO Mission Provenance Sequence

AO Mission gateway, scheduler recovery, and ledger compaction outputs are
readback/provenance surfaces. They can be bound into Atlas and Foundry evidence,
then inspected by AO Command, but they do not schedule, execute, approve, mutate
repositories, call providers, use credentials, publish releases, widen direct-main
authority, or widen concurrent mutation authority.

```mermaid
sequenceDiagram
  participant Gateway as Telegram/A2A gateways
  participant Mission as AO Mission
  participant Ledger as Mission ledger
  participant Covenant as AO Covenant
  participant Atlas as AO Atlas
  participant Foundry as AO Foundry
  participant Command as AO Command

  Gateway->>Mission: create intent/readback only
  Mission->>Ledger: record ao.mission.gateway-intent-ledger.v0.1
  Mission->>Ledger: record ao.mission.scheduler-recovery-readback.v0.1
  Mission->>Ledger: record ao.mission.ledger-compaction-readback.v0.1
  Covenant->>Mission: enforce gateway/recovery denial schemas
  Mission->>Atlas: provide digest-bound provenance inputs
  Atlas->>Atlas: compile ao.atlas.ao-mission-import.v0.1
  Atlas->>Atlas: emit ao.atlas.ao-mission-workgraph-metadata.v0.1
  Atlas->>Foundry: import one ready node plus metadata
  Foundry->>Foundry: bind provenance in ao.foundry.ao-mission-e2e-smoke.v0.1
  Foundry->>Command: expose read-only status/evidence
```

## Boundary

This is the gateway/recovery/compaction -> Atlas -> Foundry -> Command readback
path. AO Mission records provenance and next-action evidence; Atlas compiles
context and workgraph metadata; Foundry validates agreement and implementation
gates; Command reads the result. None of those readbacks grant execution
authority.
