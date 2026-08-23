# AO Cross-Platform Development Baseline Qualification

The refreshed AO stable development baseline is frozen for reproducible,
credential-free qualification on the supported hosted macOS and Windows
profiles. Native qualification is pending from merged `main`. This declaration
grants no operational authority and does not begin AO Office Pool.

## Frozen Candidate Identity

- Baseline identity:
  `sha256:19863fc2888543d815d5ea603fa2fc217c443d0bf323d85a19fafe34738f53f9`
- Qualification controller commit:
  pending merged-main qualification
- Qualification workflow:
  `.github/workflows/development-baseline-qualification.yml`
- Merged-main workflow run: pending
- Correlation ID: `ao-cross-platform-development-baseline-20260822-r2`

The baseline identity is the canonical digest of
`stack/development-baseline-manifest.json`. The controller commit identifies
the merged AO Architecture source that performed the final qualification; it
is deliberately separate from the manifest digest.

The prior qualified baseline is retained as historical evidence: identity
`sha256:add6f39f28eba107732398b7bf86db44b58f80f4a6cea89ec6b97f3b18ab6429`,
controller `91493c1cf05aa36f5812c48b0a8628a37ca243e3`, run `32625826261`.

## Frozen Repositories

| Repository | Commit |
| --- | --- |
| ao-architecture | `7574e39f0582ce135b5fd6c7ec75f901b616f2bc` |
| ao-mission | `f631893906e3bed6f257ac30bc3d0ad2739fe9df` |
| ao-blueprint | `ec6a80b60b54c0c0ac1822f873c1abf337fe5eb5` |
| ao-atlas | `3eec009d7541edd29fb5383d209cfdb480e664bc` |
| ao-foundry | `028ec4d50847247ee48c1d8d4560a4eda3422550` |
| ao-forge | `b17a6dc58d4938b3dbe10ec949b6b1008b192379` |
| ao-covenant | `7d2af0d3446757f096ebf3ce51e0918716daf7ff` |
| ao2 | `68cf6914ae51cb4b638a7441ac05c1b4e86ec6d6` |
| ao2-control-plane | `452ba78d0a2075eddb968536a207bed5a6e7e49e` |
| ao-command | `ffef6d76306e892c3e7a7f39734433d5a832006a` |
| ao-arena | `88a52d9a42c5bffe998b45c5046f36be0cf5ea43` |
| ao-crucible | `64227e3ee305cc3399063b567e02a548b5bc1855` |
| ao-sentinel | `c301b1192c77a6b1833c49a5c9230491be50a258` |
| ao-promoter | `5b103a66476e45bcf0c7fdcf4fffdb82b415ff72` |

AO Next is excluded from this stable profile.

## Frozen Runtime Releases

| Repository | Version | Tag target |
| --- | --- | --- |
| ao2 | v0.5.12 | `68cf6914ae51cb4b638a7441ac05c1b4e86ec6d6` |
| ao2-control-plane | v0.1.19 | `5de3541e9007e12d95b125e7f911c02932e21479` |
| ao-mission | v0.1.6 | `f631893906e3bed6f257ac30bc3d0ad2739fe9df` |
| ao-command | v0.1.3 | `ffef6d76306e892c3e7a7f39734433d5a832006a` |
| ao-atlas | v0.2.1 | `3603a2bb8af5adafcd9ff17b807ab89f32283d18` |
| ao-forge | v0.1.5 | `d1723769949269dcd0589916d83769dcb7275f98` |
| ao-covenant | v0.1.1 | `2fd72a0426a747868826581612fa1dc9727b53b9` |

The exact platform asset names and SHA-256 values are authoritative in the
manifest. This refresh consumes the independently verified AO2 v0.5.12 and AO
Mission v0.1.6 releases; it publishes no additional runtime release.

## Required Host Results

The exact supported qualification profiles are GitHub-hosted `macos-26` and
`windows-2025`. Each host must materialize all 14 repositories into a new root,
verify detached exact commits and runtime assets, complete all 59 declared
repository gates, and complete all 14 credential-free workflow stages with
zero declared gate skips, undeclared differences, or run-owned residue.
Semantic parity may apply only the separately frozen normalization profile
`stack/development-baseline-normalization-v1.json`.

The Windows profile uses Git for Windows Bash for declared POSIX scripts and
Windows PowerShell 5.1 parsing where source contracts require it. The macOS
arm64 profile uses Rosetta 2 only for the frozen AO Covenant Darwin amd64
asset. These are the manifest's declared overrides, not undeclared skips.

## Prior Closed Evidence (Historical)

The prior baseline's final run uploaded 11 artifacts. Their archives were independently
downloaded and rehashed against the GitHub artifact API with zero mismatches.
The reconstructed proof root contained 246 files with no missing, extra,
size-drifted, or digest-drifted entries.

| Evidence | SHA-256 |
| --- | --- |
| macOS host | `sha256:f70ce1c5860edb0a597d944cc95f6033c25391b55e125c9c8f895ea95142db42` |
| Windows host | `sha256:71a629e4419061d8fc83355a99055d4bd3c0349e38d49513286a53d4d0e142a4` |
| macOS gates | `sha256:0ff64d0c1290c68dbd76dc25e6c68fb266e678f5762202808d734d7623559540` |
| Windows gates | `sha256:a237efaeda4b8e986a40f754d3dd570eaaa1c1bd32a2f6b4e9eeed4b80d979ad` |
| macOS workflow | `sha256:f2142a72af5b48b1a392858633d830804ba22396502e41c5e6426ef07834be03` |
| Windows workflow | `sha256:ee1b54346d12d64a950d484510a4fe6c6bae7b1f8ccf61cdc1e9c89d3d7f3223` |
| macOS cleanup | `sha256:7020efc06c55a28eafb81b1b400a7ce137a9e2b5d135ccc74b45ed5e79ff7d82` |
| Windows cleanup | `sha256:cc74c0c3bb069bba7f5f9edc39eaeb63e2dab5217a0b34482bc750619370e3e8` |
| rehash | `sha256:c32409004c6ada233ba6a02ca6ff562f8876b40708ae7af0c686fdeb8acf457b` |
| parity | `sha256:7aa9f01141be6d3c67578c4045edfe04974d3e7e2fa15c4c591beee560fad097` |
| hosted closure | `sha256:cc4ad857ee7723b4c7a5efadff1b7cdf4ee136170d68f5757f39056533210e2a` |
| canonical closure JSON | `sha256:8a1b485fefd2089f2f46ee7109d08b8f88957a309d627ad8bbda8e99018bc3b0` |

The hosted closure and independently regenerated closure are identical as
canonical JSON. Their raw files differ only by LF versus Windows CRLF
serialization in the independent output.

## Limitations And Authority

This is a development-baseline qualification, not a production, release,
deployment, compatibility, provider, credential, or performance claim. Linux
is represented in the contract and runtime inventory but was not a terminal
host profile in this macOS/Windows campaign. The Rosetta 2 Covenant path is not
a native arm64 claim.

Every authority flag remains false. The refreshed dependency foundation becomes
qualified only after the pending merged-main evidence closes. AO Office Pool
has not started and has not been qualified here.
