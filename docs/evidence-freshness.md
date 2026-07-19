# AO Stack Evidence Freshness And Compatibility Gate Readiness

Status: Month 1 adoption/evidence cycle source of truth  
Current public pair: AO2 `v0.5.2` and AO2 Control Plane `v0.1.17`

## Purpose

This document defines how AO Architecture reads the current evidence base after
the post-stable cycle. It does not publish a release, launch external beta,
request promotion, or change RSI status.

## Freshness Checks

The evidence freshness verifier checks:

- AO2 public release metadata matches `stack/current-release-manifest.json`.
- AO2 Control Plane public release metadata matches
  `stack/current-release-manifest.json`.
- The compatibility matrix has 16 edges.
- All 16 edges are `tested_current_release_pair`.
- Matrix vector and consumer-test counts match the tested edge count.
- Tested edges include canonical vector references and consumer-test
  references.
- Local AO Architecture vector files referenced by the matrix exist.
- Boundary fields keep external beta, promotion, provider pilot, release, tag,
  upload, deployment, live self-modification, and RSI activation denied.

Run:

```sh
python3 scripts/verify_evidence_freshness.py
```

## Gate States

- `false`: evidence exists, but activation criteria are not selected or not
  satisfied.
- `ready`: criteria are satisfied, freshness is verified, and an operator could
  request activation in a later exact-scope task. Ready is not active.
- `active`: explicitly activated under a verified and authorized gate. Month 1
  is not authorized to set this state.
- `blocked`: a required proof is missing, stale, contradictory, or cannot be
  refreshed.
- `denied`: activation is explicitly disallowed by policy or operator boundary.

## Current Gate State

The current gate state is `ready`.

Reason: AO2 `v0.5.2`, AO2 Control Plane `v0.1.17`, and the 16 compatibility
edges are fresh and internally consistent. Activation is not authorized in this
task, so `compatibility_gate_complete` remains false in the matrix.

## Boundaries

- RSI remains denied.
- Live self-modification remains denied.
- External beta has not launched.
- Promotion is not requested or granted.
- Provider pilots did not run.
- No release, tag, upload, deployment, or new binary publication is authorized
  by this readback.
