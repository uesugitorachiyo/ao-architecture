# AO Stack Current Public Releases

This document records the current independently verified public releases.

## Current Core Pair

- AO2: [v0.5.8](https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.8)
- AO2 tag target: `a879ae7969a26d13432c7cc402174861b2444c05`
- AO2 current main: `3309137c762407862f20ed88e0469325fb187460`
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

AO Mission current main is `eb6ea4421cee1a5442cc804a2b835b7faa8e7113` and
AO Command current main is `6fc2a26a0a62b4cc9d23ad039ac205f8f11fb3d9`.

Both operator tools are public, not draft, not prerelease, and each has three
native archives independently matched to its immutable release plan.

## Compatibility State

The compatibility matrix remains proposed:

- `stack/contract-compatibility-matrix.json` status remains `proposed`.
- Canonical vector and consumer-test counts are both `16`.
- Current freshness is `16` fresh edges and `0` stale edges.
- The AO2 v0.5.8 execution-to-observation vector binds the current public
  AO2 and Control Plane release pair.
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
