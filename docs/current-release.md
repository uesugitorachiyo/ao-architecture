# AO Stack Current Public Release Pair

This document records the current public AO2 and AO2 Control Plane release pair after AO2 v0.5.1 publication.

## Current Pair

- AO2: [v0.5.1](https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.1)
- AO2 tag target: `80ec5321f42d4bab17d5e64fdae6aa099ba59d4a`
- AO2 approved manifest digest: `bd8103e7a038f47e1b4fef1a2a19ae65cc221675ea11149d39cfb679ae2a08fc`
- AO2 evidence anchor: `ao2-v0.5.1-stable-patch-release-20260715T174801Z/final-report.md`
- AO2 Windows rollback evidence: https://github.com/uesugitorachiyo/ao2/actions/runs/29445275460/job/87454080941
- AO2 Control Plane: [v0.1.15](https://github.com/uesugitorachiyo/ao2-control-plane/releases/tag/v0.1.15)
- AO2 Control Plane tag target: `f1702b387607566cac457458af9adb5871a5c412`

AO2 v0.5.1 and AO2 Control Plane v0.1.15 are the current public release pair. AO2 v0.5.1 is public, not draft, not prerelease, and has 23 public assets. AO2 Control Plane v0.1.15 is public, not draft, not prerelease, and remains the expected companion release. No Control Plane release was required for AO2 v0.5.1.

## Evidence Scope

The AO2 v0.5.1 evidence verifies public asset download, `SHA256SUMS`, provenance, macOS archive smoke, offline verification, update, rollback, and hosted Windows rollback smoke. The Windows smoke used the public v0.5.1 archive and an extracted rollback runner, then reported `windows_install_rollback=passed` and `windows_install_smoke=passed`.

This is release-pair evidence. It does not mark the full AO Stack compatibility matrix complete.

## Compatibility State

The compatibility matrix remains proposed and fully evidenced:

- `stack/contract-compatibility-matrix.json` status remains `proposed`.
- Canonical vector count is `16`.
- Consumer test count is `16`.
- `compatibility_gate_complete` remains `false`.

The Month 3 compatibility work closed every live matrix edge with canonical
vectors and consumer tests. The compatibility gate remains false under the
current proposed/gated Architecture model; external beta and promotion remain
separate decisions.

## Boundaries

- External beta has not launched.
- Promotion was not requested or granted.
- No provider pilot was run.
- No release, tag, upload, or deployment was performed by this Architecture coordination task.
- RSI remains denied.
