# AO Mission Gateway Authority Map

AO Mission is the central user entry point and continuation ledger, but gateway
clients are not execution authorities. Telegram, A2A, and codex-cron can create
or wake readback flows; they cannot approve policy, mutate repositories, call
providers, publish releases, use credentials, widen configuration, or bypass the
Blueprint -> Atlas -> Foundry -> Forge/AO2 gate chain.

## Role Map

| Surface | Allowed role | Denied authority |
| --- | --- | --- |
| AO Mission CLI | Create mission records, route objectives, continue the zero-wait event loop, emit governance snapshots, and expose artifact refs. | Does not approve policy, execute provider calls, mutate repositories outside governed gates, publish releases, change dependencies, or widen denied mutation classes. |
| Telegram gateway | Create allowlisted operator intents and status/readback requests. | Cannot directly execute mutation, approve work, call providers, publish, mutate repositories, or bypass AO Mission routing. |
| A2A gateway | Expose an Agent Card, readback-only skills, task status, messages, cancellation, and artifact refs for external agents. | External agents receive no direct mutation authority and cannot approve policy, execute work, or bypass Foundry/Forge/AO2 gates. |
| codex-cron adapter | Durable scheduler wakeup substrate for mission continuation. | Not the mission brain; cannot decide authority, execute mutation, approve work, or mutate repositories. |
| AO Blueprint | Requirements and build-authorization front door. | Does not execute generated slices or hand oversized, mutation-class, context-heavy, or long-running work directly to Foundry. |
| AO Atlas | Workgraph, context-pack, candidate, rollback, and Foundry-import compiler. | Does not execute or approve live mutation and emits only one ready Foundry import node at a time. |
| AO Foundry | Portfolio implementation coordinator and PR/readiness loop. | Executes only exact gated work through governed downstream paths; does not treat handoff generation as completion. |
| AO Command | Read-only operator status and aggregate readback. | Does not schedule, approve, execute, mutate, publish, call providers, or widen authority. |

## A2A Readback Shape

AO Mission's A2A Agent Card may advertise structured capability detail, but
those capabilities are readback-only:

- `streaming=false`
- `push_notifications=false`
- `state_transition_history=true`
- `artifact_readbacks=true`

The A2A task surface may carry artifact refs so observers can inspect mission
artifacts without receiving execution authority. Artifact refs are digest-bound readbacks;
they are not permission to edit the referenced repository or file.

## Covenant Denial Contracts

AO Covenant publishes gateway denial contracts so downstream tools can prove the
intent boundary without inferring authority from gateway convenience:

- `covenant.gateway-intent-authority-denial.v1`
- `covenant.telegram-intent-authority-denial.v1`
- `covenant.a2a-intent-authority-denial.v1`
- `covenant.scheduler-recovery-authority-denial.v1`

Every denial packet keeps the authority flags false for execution, approval,
repository mutation, provider calls, release or publish actions, credential use,
direct-main mutation, and concurrent mutation.

## Implementation Guidance

Gateway and scheduler integrations should follow the same pattern:

1. Validate identity, allowlists, roles, and command shape.
2. Record an intent or readback artifact.
3. Route through AO Mission, Blueprint, Atlas, Foundry, Forge/AO2, Covenant,
   Sentinel, Promoter, Command, CI, rollback, eval/regression, and Architecture
   wording gates as applicable.
4. Stop on denied authority, unsafe scope drift, stale evidence, failed CI,
   rollback failure, Sentinel hold, or explicit kill switch.

No gateway implementation should add a shortcut that treats chat commands,
external agent requests, scheduler wakeups, handoff generation, or artifact
inspection as completed governed execution.
