# AO Stack Current Public Releases

This document records the current independently verified public releases.

## Current Core Pair

- AO2: [v0.5.9](https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.9)
- AO2 tag target: `fec09515dfe4e550eeaddc7da497b1fe912012b4`
- AO2 current main: `1ea4c482ad105227a5701f6b8eafcd16c42d06e9`
- AO2 approved asset-manifest digest: `5f82c24b239c50dadb72e2bfafe1a310b04724cfacff5acee88f5164ec3c59cd`
- AO2 promotion-plan digest: `4e61e689432e9eddb7885448bd7bf2a70ccb46cc8ca5103be76ec9814d09c591`
- AO2 physical-Windows evidence digest: `df4384874bb2f89c67fe0b5c588cfbcbb89d2e50b123595dd5d1ca4a5b38a8f0`
- AO2 publication: [run 31210590627](https://github.com/uesugitorachiyo/ao2/actions/runs/31210590627)
- AO2 post-release verification: [run 31214323411](https://github.com/uesugitorachiyo/ao2/actions/runs/31214323411)
- AO2 public-release consumer smoke: [run 31214325492](https://github.com/uesugitorachiyo/ao2/actions/runs/31214325492)
- AO2 Control Plane: [v0.1.19](https://github.com/uesugitorachiyo/ao2-control-plane/releases/tag/v0.1.19)
- AO2 Control Plane tag target: `5de3541e9007e12d95b125e7f911c02932e21479`
- AO2 Control Plane current main: `eb420864794ceb9ebadef8f3f551772095edb758`
- AO2 Control Plane post-release verification: [run 30973505420](https://github.com/uesugitorachiyo/ao2-control-plane/actions/runs/30973505420)

AO2 v0.5.9 is public, not draft, not prerelease, and has five approved public
assets. AO2 Control Plane v0.1.19 is public, not draft, not prerelease, and has
seven approved public assets. Each tag and downloaded asset was independently
verified against its frozen source and promotion plan.

The five AO2 asset SHA-256 values are recorded in
`stack/current-release-manifest.json`: Linux x86_64
`b710ce6d5a125dce382de72376a7c7266413efd5578955a21fb5fa82ee61d4f6`,
macOS aarch64
`2726b1da29c066fa5c16398eee8c4d679e08627b32b4e1b34d6e6f7debf4250f`,
Windows x86_64
`14ab915d3b8adec4c26c72a30f9e0ffcc974fb7a28b0a991e4ae89b02c124cc4`,
the promotion plan
`4e61e689432e9eddb7885448bd7bf2a70ccb46cc8ca5103be76ec9814d09c591`,
and `SHA256SUMS`
`721b83b86edb4b39b8c87a6d7f1c6beac157989e41e8bd6e30c2f8435c11ba7e`.

## Tier 1 Operator Tools

- AO Mission: [v0.1.2](https://github.com/uesugitorachiyo/ao-mission/releases/tag/v0.1.2), tag target `582bdb830851039846ac5f760ef5f6774e453f17`
- AO Command: [v0.1.2](https://github.com/uesugitorachiyo/ao-command/releases/tag/v0.1.2), tag target `a728d90077c1340e295468e5017b5e166bc5bc7a`

AO Mission current main is `45747af3ca16e2ed596a57c8fbc25a49e78bbc6a` and
AO Command current main is `6fc2a26a0a62b4cc9d23ad039ac205f8f11fb3d9`.

Both operator tools are public, not draft, not prerelease, and each has three
native archives independently matched to its immutable release plan.
AO Mission v0.1.2 archive SHA-256 values are Linux
`948041ab395b140b46fb588356a99a9de628b0a329ebeabd15f104dd8f8f5615`,
macOS `74752b1a7e9abfdf0ca754738b9f0b7635b11318cb4e9486ee773b649637c90c`,
and Windows `8e1ea30d2184a367272d432d6810bc53f0af1fedd079981cbfcb22a71e09334e`.

## Compatibility State

The compatibility matrix remains proposed:

- `stack/contract-compatibility-matrix.json` status remains `proposed`.
- Canonical vector and consumer-test counts are both `16`.
- Current freshness is `16` fresh edges and `0` stale edges.
- AO2 v0.5.9 and Control Plane v0.1.19 are the current public pair, but the
  proposed compatibility matrix is not an active qualification gate.
- `compatibility_gate_complete` remains `false`.

The compatibility gate is ready but not active. External beta, promotion,
provider execution, and RSI authority remain separate denied or unrequested
states.

## Tier 2 Releases And Boundaries

- AO Blueprint and AO Atlas were assessed independently as `no_release_needed`.
- AO Forge: [v0.1.4](https://github.com/uesugitorachiyo/ao-forge/releases/tag/v0.1.4), tag target `e104b47c2e14b6c0927b885e137907ad227aeb5c`, current main `4bf267bc7cbd9d6289728ebcaefa939135ddfb00`.
- AO Covenant: [v0.1.1](https://github.com/uesugitorachiyo/ao-covenant/releases/tag/v0.1.1), tag target `2fd72a0426a747868826581612fa1dc9727b53b9`, current main `7d2af0d3446757f096ebf3ce51e0918716daf7ff`.
- These Tier 2 releases were independently published and verified; no further
  release is needed for their documentation-only reconciliations.

## Boundaries

- Tier 3 components remain artifact-only, and AO Architecture remains
  binary-free.
- External beta has not launched.
- Promotion was not requested or granted.
- No provider pilot was run.
- This Architecture update creates no tag, release, upload, or deployment.
- RSI remains denied.
