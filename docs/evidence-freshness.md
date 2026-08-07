# AO Stack Evidence Freshness And Compatibility Gate Readiness

Status: current operational source of truth; compatibility evidence fresh
Current public pair: AO2 `v0.5.9` and AO2 Control Plane `v0.1.19`

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
- All 16 edges have current evidence. The AO2 execution-to-observation edge is
  bound to the immutable AO2 `v0.5.9` vector and Control Plane `v0.1.19`
  consumer test.
- Matrix vector and consumer-test counts match the tested edge count.
- Tested edges include canonical vector references and consumer-test
  references.
- Local AO Architecture vector files referenced by the matrix exist.
- The AO2 canonical vector path and merge commit match the verified current
  evidence binding; fabricated paths or commits fail validation.
- `stack/execution-observation-version-skew.json` covers the predecessor public
  pair, current public pair, and current source candidate with an explicit
  freshness window. Schema, version, head, digest, skew, timestamp, and
  authority mutations fail closed.
- Boundary fields keep external beta, promotion, provider pilot, release, tag,
  upload, deployment, live self-modification, and RSI activation denied.

Run:

```sh
python3 scripts/verify_evidence_freshness.py
python3 scripts/verify_execution_observation_version_skew.py
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

The current gate state is `ready`, and the evidence freshness status is
`fresh`. Ready does not activate the gate or grant downstream authority.

Reason code: `AO2_COMPATIBILITY_EVIDENCE_CURRENT`.

AO2 `v0.5.9` uses
`tests/fixtures/compatibility/ao2-execution-receipt-v0.5.9.json` from merge
`09e8eae68f482faae4a1f8c9cd54b8080b4cc555`; AO2 Control Plane consumes the
current receipt contract through merge `85e31c51e76950fd5cb36e5bbbb0f2b45418fd20`.
`compatibility_gate_complete` remains false because this readback establishes
readiness, not activation.

## Boundaries

- RSI remains denied.
- Live self-modification remains denied.
- External beta has not launched.
- Promotion is not requested or granted.
- Provider pilots did not run.
- No release, tag, upload, deployment, or new binary publication is authorized
  by this readback.
