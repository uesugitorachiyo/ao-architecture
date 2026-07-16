# Controlled Self-Improvement Dry-Run Design

Status: dry-run only

This document defines the Month 4 controlled self-improvement loop as a
non-authoritative design and fixture-only dry-run path. It does not grant RSI,
live self-modification, provider execution, promotion, external beta launch,
release, tag, upload, or deployment authority.

## Loop

1. Proposal: a bounded self-change is described as data.
2. Policy classification: AO Covenant classifies authority and risk.
3. Human approval: approval is required and scoped to fixture dry-run only.
4. Dry-run execution: AO2 runs only against a temporary or evidence-scoped
   fixture workspace.
5. Evidence capture: digests, commands, and trace records are captured.
6. Rollback proof: the fixture workspace is restored and rollback evidence is
   recorded.
7. Observation: AO2 Control Plane observes the dry-run evidence event.
8. Operator readback: AO Command presents the dry-run status and denial state.
9. Sentinel wording check: public or operator-facing wording is scanned for
   overclaiming.
10. Promoter verdict: AO Promoter records no promotion and no RSI activation.

## Authority Boundary

- RSI remains denied.
- Live autonomous self-modification remains denied.
- Provider-backed self-change remains denied.
- Dry-run approval does not grant source repository mutation authority.
- Dry-run approval does not grant release, tag, upload, deployment, external
  contact, or credential authority.

## Required Evidence

- Proposal fixture.
- Policy classification fixture.
- Human approval gate fixture.
- Dry-run trace.
- Evidence pack with stable digests.
- Rollback proof.
- Control Plane observation.
- Command operator readback.
- Sentinel wording result.
- Promoter no-promotion and no-RSI verdict.

## Activation State

The activation state is `dry_run_only`. Any future move beyond fixture-only
dry-run would require separate authorization, new source-of-truth design,
policy review, implementation, tests, and explicit approval. This Month 4 work
does not provide that authority.
