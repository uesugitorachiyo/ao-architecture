# AO Stack Current Public Releases

This document records the current independently verified public releases.

## Current Core Pair

- AO2: [v0.5.6](https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.6)
- AO2 tag target: `5706ec9cf3a108d20984973975c2a56b905a8173`
- AO2 current main: `bd61f2a1d7e541636bbc58c42a805f93011c5d7b`
- AO2 approved asset-manifest digest: `f3d7a5040de8e6fd2703791235fa67841db480d3401c7deadfb3288464d31a45`
- AO2 promotion-plan digest: `5b1e1aec01a107d36a118265ba2a046a2995aa6a9e7be9048dc9d04320d60a67`
- AO2 physical-Windows evidence digest: `00d102508ba75904aebc61962c19e63f74da95109437072f200e8cc806c8e6ba`
- AO2 live workflow: [run 30402777601](https://github.com/uesugitorachiyo/ao2/actions/runs/30402777601)
- AO2 post-release verification and consumer smoke: [run 30403560528](https://github.com/uesugitorachiyo/ao2/actions/runs/30403560528)
- AO2 Control Plane: [v0.1.18](https://github.com/uesugitorachiyo/ao2-control-plane/releases/tag/v0.1.18)
- AO2 Control Plane tag target: `6257ec23fde726d4a0133c5b62231881fb6aaa9a`
- AO2 Control Plane promotion-plan digest: `a2f159896eea954e43d6e19914f4ef6b43aa5686ace72016dffdf0ef0ed4f455`
- AO2 Control Plane live workflow: [run 29805048315](https://github.com/uesugitorachiyo/ao2-control-plane/actions/runs/29805048315)

AO2 v0.5.6 is public, not draft, not prerelease, and has five approved public
assets. AO2 Control Plane v0.1.18 is public, not draft, not prerelease, and has
seven approved public assets. Each tag and downloaded asset was independently
verified against its frozen source and promotion plan.

The five AO2 asset SHA-256 values are recorded in
`stack/current-release-manifest.json`: Linux x86_64
`e20856c1bf09e2b4c781cd8c990c0edfc4f1e4fecf6fc977f7326de9de4fde77`,
macOS aarch64
`1d647e69b25163cce60a76423ae28d11bcf567bc5f99e3cfe671f7026fbda10c`,
Windows x86_64
`7d0427a9acb491ded35dd45b15f5f0a618b1fbd5282316b5f7adbaa82c04bff2`,
the promotion plan
`5b1e1aec01a107d36a118265ba2a046a2995aa6a9e7be9048dc9d04320d60a67`,
and `SHA256SUMS`
`ee923316aa684bec8316aac410cf504a6e30bd1b820ac8eeaf532ad79a4ab66b`.

## Tier 1 Operator Tools

- AO Mission: [v0.1.0](https://github.com/uesugitorachiyo/ao-mission/releases/tag/v0.1.0), tag target `2901a9cb887b72296a56b70a5a3be7350b28fe65`
- AO Command: [v0.1.1](https://github.com/uesugitorachiyo/ao-command/releases/tag/v0.1.1), tag target `0bcadf5701fdac88f9fd792cba3a9a6686de16e5`

Both operator tools are public, not draft, not prerelease, and each has three
native archives independently matched to its immutable release plan.

## Compatibility State

The compatibility matrix remains proposed:

- `stack/contract-compatibility-matrix.json` status remains `proposed`.
- Canonical vector and consumer-test counts are both `16`.
- Current freshness is `15` fresh edges and `1` stale edge.
- The AO2 execution-to-observation evidence remains pinned to `v0.5.1` while
  the current AO2 release is `v0.5.6`.
- `compatibility_gate_complete` remains `false`.

The compatibility gate is blocked pending either a separately verified
unchanged-contract bridge or refreshed AO2 compatibility evidence. External
beta, promotion, provider execution, and RSI authority remain separate denied
or unrequested states.

## Boundaries

- Tier 2 components AO Blueprint, AO Atlas, AO Forge, and AO Covenant were
  assessed independently as `no_release_needed`.
- Tier 3 components remain artifact-only, and AO Architecture remains
  binary-free.
- External beta has not launched.
- Promotion was not requested or granted.
- No provider pilot was run.
- This Architecture update creates no tag, release, upload, or deployment.
- RSI remains denied.
