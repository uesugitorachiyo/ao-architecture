# AO Stack Current Public Releases

This document records the current independently verified public releases.

## Current Core Pair

- AO2: [v0.5.5](https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.5)
- AO2 tag target: `dbaca8904564c4118b27a43356b7968725cd546e`
- AO2 current main: `0598920c5f2712966c4ec8ae415f1bbb91e76209`
- AO2 approved asset-manifest digest: `8268de6f7ccf2f9a194b9123df7a3845cb4660bc10476f6da1df7a5859f48574`
- AO2 promotion-plan digest: `fc0a50b716a2e6866fb442076ec83b0a119866effe3b9ed2cbaab85b014c6c40`
- AO2 physical-Windows evidence digest: `107c49f3b0fd4921a4615b359fc4e3e7616dfdc37b8941ccf4a53ccd9242a5ab`
- AO2 live workflow: [run 30293757188](https://github.com/uesugitorachiyo/ao2/actions/runs/30293757188)
- AO2 post-release verification: [run 30294693422](https://github.com/uesugitorachiyo/ao2/actions/runs/30294693422)
- AO2 consumer smoke: [run 30294695399](https://github.com/uesugitorachiyo/ao2/actions/runs/30294695399)
- AO2 Control Plane: [v0.1.18](https://github.com/uesugitorachiyo/ao2-control-plane/releases/tag/v0.1.18)
- AO2 Control Plane tag target: `6257ec23fde726d4a0133c5b62231881fb6aaa9a`
- AO2 Control Plane promotion-plan digest: `a2f159896eea954e43d6e19914f4ef6b43aa5686ace72016dffdf0ef0ed4f455`
- AO2 Control Plane live workflow: [run 29805048315](https://github.com/uesugitorachiyo/ao2-control-plane/actions/runs/29805048315)

AO2 v0.5.5 is public, not draft, not prerelease, and has five approved public
assets. AO2 Control Plane v0.1.18 is public, not draft, not prerelease, and has
seven approved public assets. Each tag and downloaded asset was independently
verified against its frozen source and promotion plan.

The five AO2 asset SHA-256 values are recorded in
`stack/current-release-manifest.json`: Linux x86_64
`c34aa59f6abc9069d77e51632660a14116ebfad6a77ad8ef8e162fccaf13db95`,
macOS aarch64
`05476d49d3036512aea4fa97ae17af96c84e99dcbb86b78500790112d9c2db3a`,
Windows x86_64
`58374127f50d80716a222f59491070fdf5e1882f088d448ddc90cb2c2a3b8ab0`,
the promotion plan
`fc0a50b716a2e6866fb442076ec83b0a119866effe3b9ed2cbaab85b014c6c40`,
and `SHA256SUMS`
`152d991f0c15eb8c17996873b8849f3a2dc6d45557328f36aee32468b9423b78`.

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
  the current AO2 release is `v0.5.5`.
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
