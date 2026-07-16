# AO Stack Operator Workflow

Status: current source of truth for Month 5 operator workflow hardening.  
Scope: current public release pair, compatibility evidence, dry-run boundaries,
policy gates, support evidence, and next safe action readback.

## Current Stack State

The current public release pair is:

- AO2 v0.5.1, tag target
  `80ec5321f42d4bab17d5e64fdae6aa099ba59d4a`.
- AO2 Control Plane v0.1.15, tag target
  `f1702b387607566cac457458af9adb5871a5c412`.

The Architecture compatibility matrix records 16 tested current-release edges,
16 canonical vectors, and 16 consumer tests. The compatibility gate is ready,
not active. That means the edge evidence is complete and fresh enough for
operator readback, but no external beta launch, promotion, or RSI authority
follows from it.

Month 4 dry-run evidence defines the controlled self-improvement boundary:
fixture-only, human-approved, rollback-verified, observed, read back to the
operator, and denied by Promoter for RSI or promotion activation.

## Denied States

- RSI remains denied.
- Live self-modification is denied.
- Provider pilot did not run.
- External beta is not launched.
- Promotion is not requested or granted.
- Release, tag, upload, deployment, and new binary publication are not part of
  the operator workflow.
- Credentials are not inspected.

## Gates

### Release Gate

The operator starts by reading the current public release pair. A workflow that
requires a new release, tag, upload, deployment, or binary publication is not a
Month 5 operator workflow item.

### Compatibility Evidence Gate

The operator checks the Architecture matrix readback. The current matrix has 16
tested edges and 0 remaining proposed edges, while the compatibility gate is
ready, not active.

### Policy Approval Gate

The operator inspects Covenant policy readback before work starts. Missing
human approval remains denied. Provider-backed work, live repository mutation,
and RSI authority remain denied.

### Dry-Run/Self-Improvement Gate

Self-improvement work is fixture-only and dry-run only. The operator reads the
dry-run evidence and confirms rollback proof before considering any follow-up.

### Observation/Readback Gate

Control Plane observation and Command readback must show the same state:
dry-run only, rollback verified, approval required, no provider execution, no
RSI, and no promotion.

### Promotion/No-RSI Gate

Promoter readback must show `promotion_requested=false`,
`promotion_granted=false`, and `rsi_authorized=false`. Sentinel wording checks
must reject any claim that changes the denied RSI, live self-modification,
external beta, promotion, or provider-pilot states.

## Operator Workflow

1. Read current state from Architecture current-release and compatibility
   evidence.
2. Choose safe next work from Foundry safe-next-work readback.
3. Inspect policy gates in Covenant readback.
4. Run or read dry-run evidence from AO2 when a dry-run is in scope.
5. Inspect rollback and observation through AO2 and AO2 Control Plane evidence.
6. Review Sentinel and Promoter boundaries before communicating status.
7. Collect support evidence if a workflow blocks or fails.

## Support Evidence

When filing or triaging an operator workflow issue, collect public-safe evidence:

- AO2 version.
- Platform.
- Exact command.
- Expected result.
- Actual result.
- Evidence path.
- Approval status.
- Manifest or checksum state.
- Rollback status.
- Observation status.
- Sanitized logs.

Do not paste credentials, tokens, provider secrets, private repository contents,
or raw private logs into support evidence.

## Next Safe Action

Month 5 next safe action is multi-repo product coordination and operator
workflow hardening. Month 6 is only a recommendation for next stable release
train planning and readiness assessment; it is not started by this workflow.
