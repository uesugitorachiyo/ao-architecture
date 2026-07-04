# AO Mission Recovery And Compaction Sequence

AO Mission scheduler recovery, ledger compaction, and timeline compaction are readback/provenance
flows. They preserve mission continuity evidence, but they do not grant work
authority.

```mermaid
sequenceDiagram
  participant Cron as codex-cron
  participant Mission as AO Mission
  participant Ledger as Mission ledger
  participant Command as AO Command
  participant Atlas as AO Atlas
  participant Foundry as AO Foundry

  Cron->>Mission: wakeup readback
  Mission->>Ledger: record ao.mission.scheduler-recovery-readback.v0.1
  Mission->>Ledger: record ao.mission.ledger-compaction-readback.v0.1
  Mission->>Ledger: record ao.mission.timeline-compaction-readback.v0.1
  Mission->>Command: expose ao.command.mission-evidence.v0.1
  Mission->>Atlas: provide optional recovery/compaction provenance
  Atlas->>Atlas: bind readbacks into ao.atlas.ao-mission-import.v0.1
  Atlas->>Foundry: emit Foundry import after workgraph compilation
  Foundry->>Foundry: bind recovery/compaction in ao.foundry.ao-mission-e2e-smoke.v0.1
```

Boundary rules:

- codex-cron remains scheduler wakeup substrate only.
- `ao.mission.scheduler-recovery-readback.v0.1` records missed and recovered
  wakeups and may recommend governed continuation.
- Scheduler recovery does not schedule work by itself.
- Scheduler recovery does not execute mutation, approve policy, mutate
  repositories, call providers, use credentials, publish releases, allow
  direct-main mutation, or allow concurrent mutation.
- `ao.mission.ledger-compaction-readback.v0.1` records compaction of local
  continuation evidence.
- Ledger compaction preserves digest-bound provenance and does not widen
  authority.
- `ao.mission.timeline-compaction-readback.v0.1` records retained route and
  continuation-step timeline digests.
- Timeline compaction preserves digest-bound provenance and does not widen
  authority.
- AO Atlas may import recovery and compaction readbacks only as provenance.
- AO Foundry may bind recovery and compaction readbacks only as e2e smoke
  evidence.
- Any readback that claims scheduling, execution, approval, repository mutation,
  provider, credential, release, direct-main, or concurrent authority must fail
  closed.
