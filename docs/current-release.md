# AO Stack Current Public Release Pair

This document records the current public AO2 and AO2 Control Plane release pair after AO2 v0.5.2 and AO2 Control Plane v0.1.17 publication.

## Current Pair

- AO2: [v0.5.2](https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.2)
- AO2 tag target: `732a97950121321b3cfad29d86526df9c0b5fad5`
- AO2 approved manifest digest: `8268de6f7ccf2f9a194b9123df7a3845cb4660bc10476f6da1df7a5859f48574`
- AO2 evidence anchor: `ao-stack-qualification-release-dsa-20260718-20260718T224504Z/publish-ao2-v052-result.json`
- AO2 hosted Windows release smoke evidence: https://github.com/uesugitorachiyo/ao2/actions/runs/29690626068/job/88202569707
- AO2 Control Plane: [v0.1.17](https://github.com/uesugitorachiyo/ao2-control-plane/releases/tag/v0.1.17)
- AO2 Control Plane tag target: `6336801eedc4a8402d12b306b98603ce0a6fb6b5`

AO2 v0.5.2 and AO2 Control Plane v0.1.17 are the current public release pair. AO2 v0.5.2 is public, not draft, not prerelease, and has 23 public assets. AO2 Control Plane v0.1.17 is public, not draft, not prerelease, and has the six expected public release assets.

## Evidence Scope

The AO2 v0.5.2 evidence verifies public asset download, `SHA256SUMS`, provenance, Docker Linux x86_64 substitution for unavailable native Ubuntu, macOS rollback, Windows rollback, release comparison, and Workbench comparison export smoke. The Control Plane v0.1.17 evidence verifies fresh public downloads, checksum closure, strict asset parity, and the AO2 v0.5.2 plus Control Plane v0.1.17 public release pair.

This is release-pair evidence. It does not mark the full AO Stack compatibility matrix complete.

## Compatibility State

The compatibility matrix remains proposed and fully evidenced:

- `stack/contract-compatibility-matrix.json` status remains `proposed`.
- Canonical vector count is `16`.
- Consumer test count is `16`.
- `compatibility_gate_complete` remains `false`.

The Month 3 compatibility work closed every live matrix edge with canonical
vectors and consumer tests. The compatibility gate is ready, not active:
evidence is complete and fresh, but activation is not authorized. External
beta, promotion, and RSI authority remain separate denied or unrequested
states.

## Boundaries

- External beta has not launched.
- Promotion was not requested or granted.
- No provider pilot was run.
- No release, tag, upload, or deployment was performed by this Architecture coordination task.
- RSI remains denied.
