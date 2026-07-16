# AO Stack Adoption Month 5 Support Readiness

Status: source of truth for Adoption/Evidence Cycle Month 5 support readiness.

The current public pair is AO2 v0.5.1 and AO2 Control Plane v0.1.16.
The compatibility matrix remains 16 tested edges, 16 canonical vectors, and
16 consumer tests. The compatibility gate is ready, not active.

## Support States

Operators and support fixtures use these states:

- fresh: current release metadata, matrix, vectors, tests, and readbacks match.
- stale: evidence needs refresh before it can support a decision.
- blocked: a required command, artifact, or readback cannot be completed.
- denied: an authority boundary prevents the requested action.
- unsupported: the request is outside the current public pair or support scope.

## Support Package

The current public-pair support package must cover:

- install
- checksum
- manifest mismatch
- approval/replay
- rollback
- Windows-safe rollback
- operator readback issue
- issue-report fields

For each support report, collect AO2 version, platform, exact command,
expected result, actual result, evidence path, approval status, manifest or
checksum state, rollback status, observation status, and sanitized logs.
Operators must not paste credentials, tokens, provider secrets, private
repository contents, or raw private logs.

## Boundaries

RSI remains denied. Live self-modification is denied. External beta is not
launched. Promotion is not requested or granted. Provider pilot did not run.
Release, tag, upload, deployment, and new binary publication are not part of
this support readiness drill. Credentials are not inspected.

Month 6 should assess adoption readiness and the release/no-release decision
using this support readiness package, without activating the compatibility
gate, external beta, promotion, provider execution, or RSI.
