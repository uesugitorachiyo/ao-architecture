# AO Cross-Platform Development Baseline Qualification

The refreshed AO stable development baseline is frozen for reproducible,
credential-free qualification on the supported hosted macOS and Windows
profiles. Native qualification is closed from merged `main`. This declaration
grants no operational authority and does not begin AO Office Pool.

## Frozen Candidate Identity

- Baseline identity:
  `sha256:2045d7aa1f10447fda8c629224ae9645d58205d06803c9378ff785e4cb6eda45`
- Qualification controller commit:
  `97c632cb0fd6c62271520f5c2147bc28110db84d`
- Qualification workflow:
  `.github/workflows/development-baseline-qualification.yml`
- Merged-main workflow run:
  [32664324625](https://github.com/uesugitorachiyo/ao-architecture/actions/runs/32664324625)
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
| ao-architecture | `4b64328f05f2f9a2a267538487553bf2b796e2e2` |
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

## Closed Evidence

Merged-main run `32664324625` passed both native hosts, the independent rehash,
semantic parity comparison, cleanup checks, and final evidence closure. Each
host completed all 59 declared repository gates and all 14 credential-free
workflow stages. The reconstructed proof root contained 246 files with zero
missing, extra, size-drifted, or digest-drifted entries.

| Evidence | SHA-256 |
| --- | --- |
| macOS host | `sha256:d48bc276df6a4becb535e1f80fd8101a74321210b5b7fa4a173b61c2cd663603` |
| Windows host | `sha256:3a9caf52986ceaf6fe2e90ae047a907d58fff041b73a973cbcbdb664a6203765` |
| macOS gates | `sha256:926d3af5c77d1a7e934fb4781953cec29613a91e53e0d8d2b7fcafd3eab68775` |
| Windows gates | `sha256:240c28427f49a1727af5b18f4b4dcc265378334948f8102ac128edb7c84a7be8` |
| macOS workflow | `sha256:7d3ac0f6cf68c392162dfb815c024a1be0c41282ee373a388491e46f88649861` |
| Windows workflow | `sha256:93c7eaa39e08d2986b8602e24da5221e0b8765bbd5563cf4875c4b97525db304` |
| macOS cleanup | `sha256:0e3a583c7563146d745aa5714581e860bdf8c660a489f64c073504554c04aa99` |
| Windows cleanup | `sha256:7596a5b50ef5f9b8ff7838083001cce947a789cc42449b1f005d3300723c937f` |
| rehash | `sha256:f9115e6f39085f22d67e8fcb3fbf14e5d1be5144082dcaf9a44e2153dbc9cdc2` |
| parity | `sha256:8881e0086f5b00c83cf20e607215445800c3f0ee3c77fb7f85fe0dcd222bc652` |
| hosted closure | `sha256:63df13f1f84dd6db08e231056970d9de2c14e1976be98ba0848f7a5164d5b367` |
| independently regenerated closure | `sha256:50883eb724e5bbadac25f79a7f5c68f5861ad0e1a80dfa6a3854fab4fb117c88` |

The hosted and independently regenerated closures are identical as canonical
JSON; their raw hashes differ only by serialization.

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
qualified by the closed merged-main evidence above. AO Office Pool has not
started and has not been qualified here.
