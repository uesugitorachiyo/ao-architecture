# AO Stack Adoption Month 2 Operator Drill

Status: source of truth for Adoption/Evidence Cycle Month 2 operator drills.

## Current Stack State

The current public pair is AO2 v0.5.1 and AO2 Control Plane v0.1.16.

The compatibility matrix has 16 tested edges, 16 canonical vectors, and 16
consumer tests. The compatibility gate is ready, not active. Ready means the
evidence is fresh enough for an operator to inspect, but this drill does not
activate the gate or grant any broader state.

## Operator Drill

The operator reads current stack state, identifies the current public pair,
checks the compatibility gate, chooses safe next work, inspects policy gates,
reads dry-run observation evidence, and collects support evidence.

The drill checks whether the operator can do that from the public pair,
Architecture evidence, Command readback, Foundry safe-next-work, Forge
run-state, Covenant policy readback, AO2 support guidance, Control Plane
observation readback, Sentinel wording checks, and Promoter no-promotion
readback.

## Support Evidence

Support evidence categories are:

- install
- checksum
- manifest mismatch
- approval/replay
- rollback
- operator readback issue

Support evidence must be public-safe: command, expected result, actual result,
evidence path, approval status, manifest or checksum state, rollback status,
observation status, and sanitized logs. Operators must not paste credentials,
tokens, provider secrets, private repository contents, or private logs.

## Denied States

- RSI remains denied.
- Live self-modification is denied.
- External beta is not launched.
- Promotion is not requested or granted.
- Provider pilot did not run.
- Release, tag, upload, deployment, and new binary publication are not part of
  this drill.
- Credentials are not inspected.

## Next Action

If the drill passes, Month 3 should focus on evidence maintenance automation
using the refreshed evidence base and operator drill results.
