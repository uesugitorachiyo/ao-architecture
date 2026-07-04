# AO Mission Gateway Sequence

AO Mission gateway inputs are intent/readback only. Telegram and A2A clients can
create operator intents and status requests, but they cannot approve policy,
execute mutation, call providers, schedule repository mutation, publish releases,
or bypass the Blueprint -> Atlas -> Foundry chain.

```mermaid
sequenceDiagram
  participant User as User / Telegram / A2A
  participant Mission as AO Mission
  participant Ledger as AO Mission ledger
  participant Command as AO Command
  participant Atlas as AO Atlas
  participant Foundry as AO Foundry

  User->>Mission: gateway command or A2A method
  Mission->>Mission: validate allowlist, role, and intent-only contract
  Mission->>Mission: classify Telegram freshness as fresh/stale/unknown
  Mission->>Mission: emit A2A fixture server readback when requested
  Mission->>Ledger: append ao.mission.gateway-intent.v0.1
  Mission->>Command: expose read-only gateway readback
  Mission->>Atlas: provide route history and artifact manifest provenance
  Atlas->>Atlas: digest-bind mission record, route history, and artifacts
  Atlas->>Foundry: emit only the first safe Foundry import node
```

The gateway ledger preserves:

- `safe_to_execute=false`
- `executes_work=false`
- `approves_work=false`
- `mutates_repositories=false`
- Telegram freshness classification is readback only; stale or unknown replay
  evidence must not be treated as current authority.
- A2A fixture server readback is local compatibility evidence only; Agent Card
  and JSON-RPC paths do not grant execution authority.

Atlas may consume AO Mission route-history provenance during import, but that
provenance remains readback evidence only. Foundry still applies its own gates
before any bounded implementation task can execute.
