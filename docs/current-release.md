# AO Stack Current Public Releases

This document records the current independently verified public releases.

## Current Core Pair

- AO2: [v0.5.10](https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.10)
- AO2 tag target: `9f4f8a8cf596127a982627b4af25c90a9a842095`
- AO2 current tested main: `269b7e8e5901f1984fae7f9d2c11144e67d958b3`
- AO2 approved asset-manifest digest: `a44bb65d59f46f3c3bf469dc7b26f0688fbf640f4f04ee9932a5a8fe186aeee3`
- AO2 promotion-plan digest: `0e1ae4663eb09c3135b66326177855cb8d93bab84d776b130114c5d2c344dd21`
- AO2 physical-Windows evidence digest: `a46f869c2c3512746ae686d65935b1612c1ef1ac0788f16bcd7de0d719268d81`
- AO2 publication and independent verification: [run 31279647320](https://github.com/uesugitorachiyo/ao2/actions/runs/31279647320)
- AO2 Control Plane: [v0.1.19](https://github.com/uesugitorachiyo/ao2-control-plane/releases/tag/v0.1.19)
- AO2 Control Plane tag target: `5de3541e9007e12d95b125e7f911c02932e21479`
- AO2 Control Plane current tested main: `4e41da173dc9f1ee37f4ae99b85791e5f05ea453`
- AO2 Control Plane post-release verification: [run 30973505420](https://github.com/uesugitorachiyo/ao2-control-plane/actions/runs/30973505420)

AO2 v0.5.10 is public, not draft, not prerelease, and has five approved public
assets. AO2 Control Plane v0.1.19 is public, not draft, not prerelease, and has
seven approved public assets. Each tag and downloaded asset was independently
verified against its frozen source and promotion plan.

The five AO2 asset SHA-256 values are recorded in
`stack/current-release-manifest.json`: Linux x86_64
`fd1ff2aaa86e72238f8a3d3a9ab7be296aff4bc8017b3ec626b6501fe4e42318`,
macOS aarch64
`e29122f3d330e8b84949c24f65cf50a9b6387e04d902f148897afd283b2af31b`,
Windows x86_64
`37eb8d06a90ad705cffa51ce3d9dc9bce4f0ac162d95b4d524ffc97b8e284d33`,
the promotion plan
`0e1ae4663eb09c3135b66326177855cb8d93bab84d776b130114c5d2c344dd21`,
and `SHA256SUMS`
`6485b289c8ec1aeaf005017313003f6b30ce165922f345b108dca31b3dd1b1af`.

## Tier 1 Operator Tools

- AO Mission: [v0.1.3](https://github.com/uesugitorachiyo/ao-mission/releases/tag/v0.1.3), tag target `2d4d24e6eb998066b537048516c9fb0c1bbc4f2a`
- AO Command: [v0.1.2](https://github.com/uesugitorachiyo/ao-command/releases/tag/v0.1.2), tag target `a728d90077c1340e295468e5017b5e166bc5bc7a`

AO Mission current tested main is `c2dc4791f59173ffc61dca4e4655e0301924406c` and
AO Command current main is `6fc2a26a0a62b4cc9d23ad039ac205f8f11fb3d9`.

Both operator tools are public, not draft, not prerelease, and each has three
native archives independently matched to its immutable release plan.
AO Mission v0.1.3 archive SHA-256 values are Linux
`ff5f4cf3c5cd1892ae2367cfb624607e0cedea59bf4d5b01e96444b4f8fef65d`,
macOS `85031d253f12712b715d8f99560fd4237d431bec5367dee825c7928fcf2d7443`,
and Windows `2ac052285126b2737d6d846ebab730f5615ad4baef4cc1a0596dceebf86465cc`.

Mission's dry-run and live workflows each built fresh candidates, so their
archive digests differ. The public assets match the live run's immutable
promotion plan exactly; this release does not claim dry-run candidate reuse.

## Compatibility State

The compatibility matrix remains proposed:

- `stack/contract-compatibility-matrix.json` status remains `proposed`.
- Canonical vector and consumer-test counts are both `16`.
- Current freshness is `16` fresh edges and `0` stale edges.
- AO2 v0.5.10 and Control Plane v0.1.19 are the current public pair. The native
  AO2 v0.5.10 execution-to-observation vector and Control Plane v0.1.19
  consumer test bind the current pair, so
  the compatibility gate is ready but not active.
- `compatibility_gate_complete` remains `false`.

## Unreleased Tested Source Changes

- AO2 `269b7e8e5901f1984fae7f9d2c11144e67d958b3` is the tested unreleased
  v0.5.11 candidate paired with Control Plane v0.1.19. Its immutable promotion
  plan has SHA-256
  `8a739be7b0bf43d89452a912e6878301d621787bd4a2887b08812a43a8febebb`,
  and its physical-Windows evidence has SHA-256
  `d01d32d9b3c51d4b855ba39dbbf5072df36f54312eb08b5b1444420ac5506a3a`.
  Control Plane current source
  `4e41da173dc9f1ee37f4ae99b85791e5f05ea453` retains v0.1.19 as the
  qualified companion. Neither source head changes the published versions
  above, and v0.5.11 requires separate release authorization.
- AO Mission `c2dc4791f59173ffc61dca4e4655e0301924406c` is the tested unreleased
  v0.1.4 candidate. It fixes stale Atlas closure actions, adds immutable
  release-finalizer validation, preserves correlation identity in compaction
  readbacks, and binds committed v0.1.4 release notes. Rehearsal run
  [31297366031](https://github.com/uesugitorachiyo/ao-mission/actions/runs/31297366031)
  and finalize dry run
  [31297477754](https://github.com/uesugitorachiyo/ao-mission/actions/runs/31297477754)
  passed without attempting publication. These changes are not part of public
  v0.1.3 and require separate release authorization.
- No unreleased source head, passing test, or ready readback changes the current
  public versions or grants release, deployment, publication, or activation.

The compatibility gate is ready and not active. External beta, promotion,
provider execution, and RSI authority remain separate denied or unrequested
states.

## Tier 2 Releases And Boundaries

- AO Blueprint was assessed independently as `no_release_needed`.
- AO Atlas [v0.1.0](https://github.com/uesugitorachiyo/ao-atlas/releases/tag/v0.1.0)
  is a historical tag at `3e2027972760b66971714e1f27ab7689db07662e`
  with no downloadable release assets. Current Atlas source
  `e19acf2619588b6257b37ebd0fcf7219645284f3` documents the source-only
  v0.2.0 candidate qualified from runtime source
  `9a0814817ef54a34e99e2c6c1d41812b011e1661`. Publication-disabled
  [rehearsal run 31321287357](https://github.com/uesugitorachiyo/ao-atlas/actions/runs/31321287357)
  produced an immutable promotion plan with SHA-256
  `347e69a926439d84edf16eb20f2c1ddb99306c690c40ca73e193e2add3232fdb`;
  native macOS aarch64, Linux x86_64, hosted Windows x86_64, and physical
  Windows lifecycle checks passed. This is not a public v0.2.0 release and
  requires separate release authorization.
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
