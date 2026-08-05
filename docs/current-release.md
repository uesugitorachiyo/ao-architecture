# AO Stack Current Public Releases

This document records the current independently verified public releases.

## Current Core Pair

- AO2: [v0.5.8](https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.8)
- AO2 tag target: `a879ae7969a26d13432c7cc402174861b2444c05`
- AO2 current main: `50bde9832802adb3505bcf406566b934049f6778`
- AO2 approved asset-manifest digest: `7818def468eb212f949c38480c810cbd8c6e5717b43333767781fef96c2ee135`
- AO2 promotion-plan digest: `9e988764ba7232663ba3ca23bcaabe229f0c915084cdc402fbc4202b624f5f6d`
- AO2 physical-Windows evidence digest: `b0e64aeb386f5a1ca5884b52cb63b9e2bb1ebc98101cb2e0ce06e0bafccdd27c`
- AO2 exact-head CI: [run 30972784151](https://github.com/uesugitorachiyo/ao2/actions/runs/30972784151)
- AO2 stable promotion dry run: [run 30973441678](https://github.com/uesugitorachiyo/ao2/actions/runs/30973441678)
- AO2 post-release verification: [run 30973502699](https://github.com/uesugitorachiyo/ao2/actions/runs/30973502699)
- AO2 public-pair digest audit: [run 30973503994](https://github.com/uesugitorachiyo/ao2/actions/runs/30973503994)
- AO2 Control Plane: [v0.1.19](https://github.com/uesugitorachiyo/ao2-control-plane/releases/tag/v0.1.19)
- AO2 Control Plane tag target: `5de3541e9007e12d95b125e7f911c02932e21479`
- AO2 Control Plane current main: `128fc8b28be5bcc5b0f5d616ba02d016e84899ff`
- AO2 Control Plane post-release verification: [run 30973505420](https://github.com/uesugitorachiyo/ao2-control-plane/actions/runs/30973505420)

AO2 v0.5.8 is public, not draft, not prerelease, and has five approved public
assets. AO2 Control Plane v0.1.19 is public, not draft, not prerelease, and has
seven approved public assets. Each tag and downloaded asset was independently
verified against its frozen source and promotion plan.

The five AO2 asset SHA-256 values are recorded in
`stack/current-release-manifest.json`: Linux x86_64
`d18574504e178a34f43b34336a1b6040716d68bceb3efc56a084570ff3b280e1`,
macOS aarch64
`a893fcf8eef7058fee020d8b3d5fb6f71988173d55d23b37f9deb93bcde31b98`,
Windows x86_64
`793d242ec3968e72a5e580a499b498408281836c57a028ebcb9f6d44a7e94543`,
the promotion plan
`9e988764ba7232663ba3ca23bcaabe229f0c915084cdc402fbc4202b624f5f6d`,
and `SHA256SUMS`
`d086ce352ec8baea7e20567b58b776893569fe84da0e13eae5e03b481df16be4`.

## Tier 1 Operator Tools

- AO Mission: [v0.1.1](https://github.com/uesugitorachiyo/ao-mission/releases/tag/v0.1.1), tag target `8940b7cb319216ae66a8c660fed2948c5b2731b8`
- AO Command: [v0.1.2](https://github.com/uesugitorachiyo/ao-command/releases/tag/v0.1.2), tag target `a728d90077c1340e295468e5017b5e166bc5bc7a`

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
