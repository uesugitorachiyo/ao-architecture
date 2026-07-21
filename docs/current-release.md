# AO Stack Current Public Releases

This document records the independently verified Month 6 public releases.

## Current Core Pair

- AO2: [v0.5.3](https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.3)
- AO2 tag target: `947e566bd3f54ed902f3c14fc0c90e21a24359bc`
- AO2 promotion-plan digest: `5b91f3a8f643bb0c8f160f1718c25f94df31802c89d2d1d26eac5613097cb189`
- AO2 physical-Windows evidence digest: `548992774ff4092c935cf934c82b80886a12dfd23640acfd3a46b3f508426be8`
- AO2 live workflow: [run 29802133424](https://github.com/uesugitorachiyo/ao2/actions/runs/29802133424)
- AO2 Control Plane: [v0.1.18](https://github.com/uesugitorachiyo/ao2-control-plane/releases/tag/v0.1.18)
- AO2 Control Plane tag target: `6257ec23fde726d4a0133c5b62231881fb6aaa9a`
- AO2 Control Plane promotion-plan digest: `a2f159896eea954e43d6e19914f4ef6b43aa5686ace72016dffdf0ef0ed4f455`
- AO2 Control Plane live workflow: [run 29805048315](https://github.com/uesugitorachiyo/ao2-control-plane/actions/runs/29805048315)

AO2 v0.5.3 is public, not draft, not prerelease, and has five approved public
assets. AO2 Control Plane v0.1.18 is public, not draft, not prerelease, and has
seven approved public assets. Each tag and downloaded asset was independently
verified against its frozen source and promotion plan.

## Tier 1 Operator Tools

- AO Mission: [v0.1.0](https://github.com/uesugitorachiyo/ao-mission/releases/tag/v0.1.0), tag target `2901a9cb887b72296a56b70a5a3be7350b28fe65`
- AO Command: [v0.1.1](https://github.com/uesugitorachiyo/ao-command/releases/tag/v0.1.1), tag target `0bcadf5701fdac88f9fd792cba3a9a6686de16e5`

Both operator tools are public, not draft, not prerelease, and each has three
native archives independently matched to its immutable release plan.

## Compatibility State

The compatibility matrix remains proposed and fully evidenced:

- `stack/contract-compatibility-matrix.json` status remains `proposed`.
- Canonical vector count is `16`.
- Consumer test count is `16`.
- `compatibility_gate_complete` remains `false`.

The compatibility evidence is complete and fresh, but activation is not
authorized. External beta, promotion, provider execution, and RSI authority
remain separate denied or unrequested states.

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
