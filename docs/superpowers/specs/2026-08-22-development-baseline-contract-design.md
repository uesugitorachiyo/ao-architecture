# AO Development Baseline Contract Design

## Purpose

Freeze one strict, public-safe identity for the fourteen repositories in the
stable AO development profile. The contract is the input to later
materialization, gate execution, workflow, parity, and evidence-closure slices.
It does not clone repositories, run gates, approve work, or grant release,
provider, credential, deployment, promotion, compatibility, external-beta, or
RSI authority.

## Bootstrap Identity Model

The baseline manifest is stored in AO Architecture, so it cannot truthfully
contain the Git commit that contains itself. S01 therefore separates three
identities:

1. `baseline_identity` is the SHA-256 of canonical manifest bytes. The manifest
   pins the fourteen target repositories at the upstream `main` commits frozen
   below.
2. `release_input_digest` is the SHA-256 of
   `stack/current-release-manifest.json`. It binds the protected seven-release
   input without modifying that historical source.
3. `controller_source_commit` is the AO Architecture commit running the
   verifier. It is emitted in verification evidence and Mission checkpoint
   material, but excluded from `baseline_identity` to avoid self-reference.

The controller checkout is not a fifteenth baseline repository. A later
controller commit may materialize and verify the same frozen target baseline;
its source commit must always be recorded with the result.

## Frozen Repository Inventory

The source identity was captured with `git ls-remote <upstream>
refs/heads/main` on 2026-08-22. Branch names are provenance only; the forty-character
commit is the identity.

| Repository | Upstream | Frozen commit |
| --- | --- | --- |
| ao-architecture | `https://github.com/uesugitorachiyo/ao-architecture.git` | `c0b6f745049bb10034d98946bad4c45174950c0b` |
| ao-mission | `https://github.com/uesugitorachiyo/ao-mission.git` | `1aeb2cd78c8a7c5df100cdf1bd17d20c478ca47e` |
| ao-blueprint | `https://github.com/uesugitorachiyo/ao-blueprint.git` | `ec6a80b60b54c0c0ac1822f873c1abf337fe5eb5` |
| ao-atlas | `https://github.com/uesugitorachiyo/ao-atlas.git` | `acd162ad1b187a9fe179e36cb0d20be5db874d69` |
| ao-foundry | `https://github.com/uesugitorachiyo/ao-foundry.git` | `028ec4d50847247ee48c1d8d4560a4eda3422550` |
| ao-forge | `https://github.com/uesugitorachiyo/ao-forge.git` | `b17a6dc58d4938b3dbe10ec949b6b1008b192379` |
| ao-covenant | `https://github.com/uesugitorachiyo/ao-covenant.git` | `7d2af0d3446757f096ebf3ce51e0918716daf7ff` |
| ao2 | `https://github.com/uesugitorachiyo/ao2.git` | `880f32ce8d9af5ba6e50aa5885c214c04f23f20d` |
| ao2-control-plane | `https://github.com/uesugitorachiyo/ao2-control-plane.git` | `4e41da173dc9f1ee37f4ae99b85791e5f05ea453` |
| ao-command | `https://github.com/uesugitorachiyo/ao-command.git` | `ffef6d76306e892c3e7a7f39734433d5a832006a` |
| ao-arena | `https://github.com/uesugitorachiyo/ao-arena.git` | `88a52d9a42c5bffe998b45c5046f36be0cf5ea43` |
| ao-crucible | `https://github.com/uesugitorachiyo/ao-crucible.git` | `64227e3ee305cc3399063b567e02a548b5bc1855` |
| ao-sentinel | `https://github.com/uesugitorachiyo/ao-sentinel.git` | `c301b1192c77a6b1833c49a5c9230491be50a258` |
| ao-promoter | `https://github.com/uesugitorachiyo/ao-promoter.git` | `5b103a66476e45bcf0c7fdcf4fffdb82b415ff72` |

AO Next is not a stable-profile member. The contract names it only in the
closed exclusion list and rejects it from `repositories`.

## Manifest Contract

`stack/development-baseline-manifest.json` uses schema
`ao.architecture.development-baseline-manifest.v1`. Every object is closed with
`additionalProperties: false`. Its top-level fields are:

- `schema`, `profile`, and `source_freeze_utc`;
- `repositories`, containing exactly the fourteen ordered entries above;
- `release_input`, binding the protected release-manifest path, schema, and
  SHA-256;
- `runtime_releases`, containing exactly seven release bindings;
- `toolchains`, a closed set for Git, Python, Go, Rust/Cargo, Node/npm,
  PowerShell, and POSIX shell;
- `platform_overrides`, a closed allowlist;
- `excluded_repositories`, containing only `ao-next` for the stable profile;
  and
- `authority`, whose execution, approval, repository mutation, provider,
  credential, release, publication, deployment, promotion, compatibility,
  external-beta, and RSI fields are all false.

Each repository entry binds its exact sibling path, HTTPS upstream, commit,
moving-branch metadata, source role, and gate contract. A gate contract is an
exact source locator rather than an Architecture-invented command:

- `ao-quality-gates.json#levels.full.steps.<id>` when the exact repository head
  owns a quality manifest; or
- `AGENTS.md#Verification:<ordinal>` for an exact command in the repository's
  Verification section.

Each gate source carries its blob SHA-256. S03 may add validated native argv
arrays, but it must retain these S01 source locators and may not reinterpret
their semantics.

Repository paths are single safe relative names equal to the repository name.
Upstreams are canonical HTTPS GitHub URLs. Commits are lowercase forty-character
hex values. Duplicate names, paths, upstreams, or commits are rejected.

## Runtime Release Binding

The seven release identities are AO2, AO2 Control Plane, AO Mission, AO Command,
AO Atlas, AO Forge, and AO Covenant. The verifier loads the protected current
release manifest, verifies its exact digest, and requires repository, version,
tag, tag target, release URL, draft/prerelease disposition, asset count, and
every available platform digest to agree.

The protected release manifest does not contain platform digest maps for AO2
Control Plane v0.1.19 or AO Covenant v0.1.1. S01 does not rewrite that file.
Instead, the development manifest records supplemental producer provenance from
the corresponding public GitHub release API objects. The following platform
digests are frozen:

### AO2 Control Plane v0.1.19

- Linux x86_64: `588903471152cbc2cae1fc9d514d69b72c153b913a368cb6bf01da09c2789cbf`
- macOS arm64: `06addc587bd282763c47d9ee4e36cb8ebea0c114881296569ef4d0b4dff86972`
- Windows x86_64: `c3528322730afd4a0c3988f9b2a23767f67febbf96b62340988546346ad00e05`

### AO Covenant v0.1.1

- Linux amd64: `f6820fdc7b99873071e7f68fc50d9bfd922750a2e788d9fca5aa8fb37cc8180b`
- Darwin amd64: `9a5ca7c6920c44b6e120d6c5bd8baf190b66e188d43485639c6fc5355190868e`
- Windows amd64: `fd6e3a0033608d3f47dccb60f48191e4c4b2dc4fdce893c87d8ea96199610c5d`

Covenant's macOS arm64 profile explicitly selects the Darwin amd64 asset with
Rosetta 2. That is a declared compatibility boundary, not a native-arm64 claim.
S02 independently downloads and rehashes all selected assets.

## Toolchains And Platform Overrides

Toolchain entries specify a command name, version probe argv, and supported
minimum/maximum or exact major-version constraint. They do not install or
update tools. S02 evaluates the constraints on each host.

The S01 platform-override allowlist contains only:

- Windows `.sh` repository gates through Git for Windows Bash;
- Windows PowerShell 5.1 parsing where a repository owns a Windows PowerShell
  contract;
- Covenant Darwin amd64 through Rosetta 2 on macOS arm64; and
- platform-native executable suffix and release archive format selection.

Any other override fails validation. Normalization of timestamps, durations,
process IDs, roots, and separators belongs to S05 and is not an S01 override.

## Verifier And Identity Digest

`scripts/verify_development_baseline.py` uses only the Python standard library.
It reads bounded regular JSON files, rejects duplicate keys and non-UTF-8 input,
and validates the strict schema plus cross-field invariants. It never follows a
manifest-supplied path outside the Architecture checkout and never performs a
network request.

Canonical identity bytes are UTF-8 JSON with sorted keys, compact separators,
and no generated timestamp or controller commit. Because the manifest contains
only frozen source data, its full canonical object is hashed without omitting a
self-digest field. Successful output is deterministic and includes:

```text
baseline_identity=sha256:<64 lowercase hex>
repositories=14
runtime_releases=7
errors=0
```

Failure output lists stable, sorted error messages and exits nonzero without
changing any file.

## Negative Coverage

Tests create isolated fixture manifests and prove rejection of duplicate JSON
keys, duplicate repositories, missing or extra stable members, malformed or
moving-branch-only commits, upstream drift, unsafe paths, gate-source drift,
release-input digest drift, release tag or platform digest drift, undeclared
platform overrides, AO Next in the stable profile, authority widening, unknown
properties, oversized inputs, and non-UTF-8 input. A valid fixture proves the
identity digest is invariant to host path separators and JSON formatting.

## Review And S01 Checkpoint

S01 is eligible to checkpoint only after focused tests, manifest verification,
Architecture verification, and `git diff --check` pass on a committed source
head. Independent review must confirm the exact inventory, release bindings,
gate-source provenance, controller/baseline identity separation, and authority
boundary. Mission retains the reviewed controller commit, manifest identity,
release-input digest, test summary, and artifact hashes. S02 remains blocked
until that review is recorded.
