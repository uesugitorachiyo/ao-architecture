# AO Mission v0.2 Capability Map

AO Mission v0.2 makes `ao-mission` the operator-facing loop. Blueprint remains
underneath for new authorization or governed-plan requirements, but routine
mission hardening starts from Mission readbacks, Mission search, and Mission
doctor output.

## Capability Bindings

| Capability | Owning repo | Public-safe output | Authority boundary |
| --- | --- | --- | --- |
| Durable mission event search/index | `ao-mission` | Mission event index and filtered search readback for mission, kind, and query inspection. | Read-only event discovery; does not schedule or execute work. |
| A2A streaming/SSE denial fixtures | `ao-mission` | Invalid Agent Card fixtures and denial readbacks for streaming, push, and SSE claims. | A2A remains request/readback only; no push or streaming execution authority. |
| `ao-mission doctor` | `ao-mission` | Local store health and fixture readiness summary. | Diagnostic only; no provider calls, credentials, release, deploy, or repository mutation. |
| Scheduler replay recovery | `ao-mission` | Replay recovery tests for fresh scheduler replay state. | Recovery evidence does not grant scheduling, execution, approval, or concurrency authority. |
| Telegram command replay matrix | `ao-mission` | Replay coverage for allowed commands and denied roles. | Telegram intents remain intent/readback only. |
| Atlas provenance rendering | `ao-atlas` | AO Mission provenance render from workgraph metadata. | Atlas compiles and renders context; it does not schedule, approve, execute, or mutate. |
| Foundry rollup/readiness binding | `ao-foundry` | Mission rollup summary binding final-rollup smoke and readiness ledger. | Foundry records readiness only; execution remains behind governed Foundry/AO2 gates. |
| Command compact mission timeline filters | `ao-command` | Compact filtered mission route-history view by route, status, and query. | AO Command is read-only operator status; it does not start work. |
| Sentinel mission-risk stale wording scan | `ao-sentinel` | Stale-language detector for mission-risk freshness absolutes. | Scanner blocks unsafe public wording; it does not grant promotion. |
| Covenant external-agent intent-only contract | `ao-covenant` | Schema-backed denial that external agents are intent/readback only. | Actual external execution, provider, credential, release, direct-main, concurrent, and mutation authority remain denied. |
| Promoter promotion/no-promotion rollup summary | `ao-promoter` | Promotion/no-promotion summary over Mission gateway no-promotion evidence. | Promotion remains disabled without a separate exact-scope packet and all gates. |
| Architecture AO Mission v0.2 capability map | `ao-architecture` | This map and verifier check. | Documentation only; no operational authority. |

## Safety Boundaries

- No direct main mutation.
- No provider calls.
- No credential use.
- No release, deploy, publish, upload, or tag authority.
- No dependency updates.
- No policy, authorization, or configuration widening.
- No hidden instruction mutation.
- No broad RSI claim.

## Operator Flow

1. Start from AO Mission readiness readbacks, event search, doctor output, and
   mission timeline status.
2. Route through Blueprint only when a new governed plan or authorization is
   required.
3. Route context-heavy or multi-repo sequencing through Atlas.
4. Route bounded implementation work through Foundry, with Covenant, Sentinel,
   Command, Promoter, and Architecture providing denial, scan, readback,
   rollup, and map evidence.
