# AO Stack Evidence Freshness And Compatibility Gate Readiness

Status: current operational source of truth using Month 1 compatibility evidence
Current public pair: AO2 `v0.5.6` and AO2 Control Plane `v0.1.18`

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
- The matrix labels all 16 edges `tested_current_release_pair`, but freshness is
  evaluated separately against the current public versions.
- 15 edges have current evidence. The AO2 execution-to-observation edge is
  stale because its canonical vector remains pinned to AO2 `v0.5.1`.
- Matrix vector and consumer-test counts match the tested edge count.
- Tested edges include canonical vector references and consumer-test
  references.
- Local AO Architecture vector files referenced by the matrix exist.
- The AO2 canonical vector path and merge commit match the verified historical
  evidence binding; fabricated paths or commits fail validation.
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

The current gate state is `blocked`, and the evidence freshness status is
`stale`.

Reason code: `AO2_COMPATIBILITY_EVIDENCE_VERSION_STALE`.

AO2 `v0.5.6` is current, but the AO2-to-Control-Plane
execution-to-observation edge still uses
`tests/fixtures/compatibility/ao2-execution-receipt-v0.5.1.json` from merge
`5b568830360baac6198a653737f60abab393eec7`. That leaves 15 fresh edges and
one stale edge. Fresh status requires either a separately verified
unchanged-contract bridge from `v0.5.1` to `v0.5.6` or a refreshed fixture and
consumer verification. No such bridge is inferred here, and
`compatibility_gate_complete` remains false.

## Boundaries

- RSI remains denied.
- Live self-modification remains denied.
- External beta has not launched.
- Promotion is not requested or granted.
- Provider pilots did not run.
- No release, tag, upload, deployment, or new binary publication is authorized
  by this readback.
