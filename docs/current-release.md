# AO Stack Current Public Releases

This document records the current independently verified public releases.

## Current Core Pair

- AO2: [v0.5.7](https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.7)
- AO2 tag target: `a3d8d19cef8f3aa69ea14e46ef94cc9706a502a7`
- AO2 current main: `e7f8e391f57a57c0f8056426e7d3f696c1d093ac`
- AO2 approved asset-manifest digest: `f726e2cac6581ee9422965faec4c9892ec508c6291c732cec8d48c4900908e55`
- AO2 promotion-plan digest: `8e058f6a891d837db856916083a7b2ba9bc53f997b96c5522e8b0a552f6b7be7`
- AO2 physical-Windows evidence digest: `18bf31d6aba7021ce30b5d5aeed22055f42712c5bd208bb31764c184509a26b8`
- AO2 live workflow: [run 30684627433](https://github.com/uesugitorachiyo/ao2/actions/runs/30684627433)
- AO2 post-release verification: [run 30688624711](https://github.com/uesugitorachiyo/ao2/actions/runs/30688624711)
- AO2 public consumer smoke: [run 30688625596](https://github.com/uesugitorachiyo/ao2/actions/runs/30688625596)
- AO2 Control Plane: [v0.1.18](https://github.com/uesugitorachiyo/ao2-control-plane/releases/tag/v0.1.18)
- AO2 Control Plane tag target: `6257ec23fde726d4a0133c5b62231881fb6aaa9a`
- AO2 Control Plane promotion-plan digest: `a2f159896eea954e43d6e19914f4ef6b43aa5686ace72016dffdf0ef0ed4f455`
- AO2 Control Plane live workflow: [run 29805048315](https://github.com/uesugitorachiyo/ao2-control-plane/actions/runs/29805048315)

AO2 v0.5.7 is public, not draft, not prerelease, and has five approved public
assets. AO2 Control Plane v0.1.18 is public, not draft, not prerelease, and has
seven approved public assets. Each tag and downloaded asset was independently
verified against its frozen source and promotion plan.

The five AO2 asset SHA-256 values are recorded in
`stack/current-release-manifest.json`: Linux x86_64
`4760705d9cedc32beaa7d3694731ed02eca8c9ec7adbc55ac187d3b9f86447ee`,
macOS aarch64
`2355fba5fa61fb078649534ef38c8cb0aa137d50e41df94b819822c0f8833910`,
Windows x86_64
`c5924999d89dd090579dc9f9851990afee8c8dbb61baccdb50c5a333b50cb7f8`,
the promotion plan
`8e058f6a891d837db856916083a7b2ba9bc53f997b96c5522e8b0a552f6b7be7`,
and `SHA256SUMS`
`58e9a135f0e113a091dc9d7246b3596df7671f2e1273caee43e4937113fe1fc1`.

## Tier 1 Operator Tools

- AO Mission: [v0.1.0](https://github.com/uesugitorachiyo/ao-mission/releases/tag/v0.1.0), tag target `2901a9cb887b72296a56b70a5a3be7350b28fe65`
- AO Command: [v0.1.1](https://github.com/uesugitorachiyo/ao-command/releases/tag/v0.1.1), tag target `0bcadf5701fdac88f9fd792cba3a9a6686de16e5`

Both operator tools are public, not draft, not prerelease, and each has three
native archives independently matched to its immutable release plan.

## Compatibility State

The compatibility matrix remains proposed:

- `stack/contract-compatibility-matrix.json` status remains `proposed`.
- Canonical vector and consumer-test counts are both `16`.
- Current freshness is `16` fresh edges and `0` stale edges.
- The immutable AO2 v0.5.6 execution-to-observation vector remains valid for
  v0.5.7 through the verified unchanged-contract bridge.
- `compatibility_gate_complete` remains `false`.

The compatibility gate is ready but not active. External beta, promotion,
provider execution, and RSI authority remain separate denied or unrequested
states.

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
