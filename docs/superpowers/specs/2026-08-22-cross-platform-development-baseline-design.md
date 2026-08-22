# AO Cross-Platform Development Baseline Design

## Purpose

Create one clean, manifest-bound AO development baseline that a solo developer
can materialize on macOS and Windows before beginning AO Office Pool work. The
baseline must preserve the existing AO architecture and expose equivalent
repository, contract, workflow, policy, evidence, and cleanup behavior on both
platforms.

The current seven-component public release set is already the stable runtime
foundation. Architecture merged-main canary run `32540433860` downloaded those
public assets and passed on Linux x86_64, macOS arm64, and Windows x86_64. This
design does not repeat that release project or reinterpret Windows as generally
unusable. It closes the narrower gap between a working macOS development
workspace and a reproducible full-source Windows development workspace.

## Goals

- Capture the exact clean macOS AO workspace as a reviewed baseline identity.
- Materialize the same repository set and exact commits on clean macOS and
  Windows hosts without copying machine-local state.
- Bind released runtime components to the current public release manifest and
  bind source-used components to exact reviewed commits.
- Run repository-owned development gates and one complete credential-free AO
  workflow on both platforms.
- Compare semantic outcomes while allowing only declared operating-system
  differences.
- Produce closed, digest-bound evidence that supports a cross-platform AO
  development-baseline claim.
- Leave both hosts clean enough to begin a later AO Office Pool project from the
  same AO dependency identity.

## Non-Goals

- Develop, package, qualify, or release AO Office Pool.
- Create a universal AO executable, wrapper command, or product installer.
- Merge the AO repositories or replace their existing component CLIs.
- Publish a new AO release merely to create the development baseline.
- Activate compatibility, promotion, providers, deployments, external beta, or
  recursive self-improvement.
- Promote AO Next to the stable execution path. AO Next remains an optional,
  experimental source entry governed by its bounded successor-feasibility ADR.
- Require byte-identical paths, timestamps, process identifiers, archive
  formats, or logs across operating systems.
- Rewrite historical Windows qualification evidence. Any historical digest
  defect is recorded, and this project creates new canonical evidence.

## Baseline Authority

AO Architecture owns a new machine-readable development-baseline manifest. The
manifest is distinct from `stack/current-release-manifest.json`: the current
release manifest continues to own the seven public binary releases, while the
development manifest owns the full source workspace used for development.

The first baseline is derived from the current clean macOS workspace under the
following fail-closed rules:

1. Every included repository must have an exact 40-character commit, a declared
   upstream repository, no tracked changes, and no unresolved submodules.
2. The commit must exist in the declared upstream repository and have successful
   required default-branch or accepted release-candidate verification.
3. A moving branch name is metadata only; the commit is the identity.
4. For a publicly released component, the manifest records both the source
   commit used for development and the immutable runtime release tag, tag target,
   platform asset, and SHA-256 from `stack/current-release-manifest.json`.
5. For a source-used component, the manifest records the build entry point and
   repository-owned verification commands at the exact source commit.
6. Platform-specific overrides are allowed only in a closed, reviewed list.
7. AO Next is excluded from the stable baseline by default. An optional profile
   may include its exact experimental commit without changing stable succession
   or release claims.

The stable profile includes AO Architecture, AO Mission, AO Blueprint, AO
Atlas, AO Foundry, AO Forge, AO Covenant, AO2, AO2 Control Plane, AO Command, AO
Arena, AO Crucible, AO Sentinel, and AO Promoter. The manifest also records the
tested Git, Python, Go, Rust/Cargo, Node/npm, PowerShell, and shell versions and
the supported version constraints used by preflight.

## Repository Layout

Both platforms materialize the same sibling-repository topology beneath an
operator-selected empty root:

```text
ao-development-baseline/
  ao-architecture/
  ao-mission/
  ao-blueprint/
  ao-atlas/
  ao-foundry/
  ao-forge/
  ao-covenant/
  ao2/
  ao2-control-plane/
  ao-command/
  ao-arena/
  ao-crucible/
  ao-sentinel/
  ao-promoter/
  .ao-baseline/
```

`.ao-baseline/` contains generated private evidence, downloaded public assets,
temporary build products, and normalized parity results. It is never committed
to a component repository. Bootstrap rejects a non-empty target, repository
name collisions, path traversal, reparse or symlink traversal at the target
boundary, and a checkout that resolves outside the selected root.

## Bootstrap And Preflight

Architecture provides thin platform entry points backed by one standard-library
Python implementation:

- `scripts/bootstrap-development-baseline.sh`
- `scripts/bootstrap-development-baseline.ps1`
- `scripts/bootstrap_development_baseline.py`
- `scripts/verify_development_baseline.py`

The shell and PowerShell files only establish native argument and executable
handling. The Python implementation owns manifest parsing, cloning, detached
checkout, source identity validation, asset verification, evidence writing,
and deterministic error reporting.

Bootstrap supports two explicit modes:

- `materialize`: require an empty destination, clone declared upstreams, and
  check out the exact commits.
- `verify-existing`: make no repository changes and verify an existing sibling
  workspace against the manifest.

Bootstrap never updates dependencies, changes global Git configuration, reads
credentials, starts a provider-backed workflow, or silently repairs a dirty
checkout. Public runtime downloads are bounded, hash-verified before extraction,
and extracted with path, type, size, and entry-count controls.

Preflight reports native capabilities instead of assuming they are identical.
The Windows profile explicitly covers PowerShell 5.1 and 7 discovery, Git for
Windows Bash for repository-owned `.sh` gates, CRLF checkout behavior, default
non-UTF-8 Python mode, path-with-spaces behavior, long paths, symlink privilege,
file locking, and executable extensions. The macOS profile covers native shell,
filesystem permissions, case behavior, and the declared Covenant Rosetta 2
boundary. A missing required capability fails; a capability-dependent skip is
allowed only when the owning repository already defines that skip contract.

## Verification Layers

### Layer 1: Baseline identity

Validate the manifest schema, repository inventory, exact commits, upstream
containment, tracked cleanliness, runtime asset digests, toolchain constraints,
and platform override allowlist. The normalized identity digest must match on
macOS and Windows.

### Layer 2: Repository-owned development gates

Run each included repository's declared full development gate from its own
`AGENTS.md`, quality manifest, or authoritative verification documentation.
Architecture schedules these commands but does not redefine their semantics.
Every result records repository, commit, command identifier, native argv, start
and finish timestamps, exit status, declared skip classification, and bounded
stdout/stderr digests.

Commands run sequentially by default to minimize machine-resource variance and
to preserve readable failure attribution. A failure stops downstream parity
claims but does not erase earlier results.

### Layer 3: Full-stack credential-free workflow

Run one deterministic fixture through the existing AO contract path:

```text
Mission intake
  -> Blueprint authorization
  -> Atlas workgraph and context pack
  -> Foundry / Forge coordination
  -> Covenant policy decision
  -> AO2 bounded fixture execution
  -> Control Plane observation
  -> Command and Mission readback
  -> Arena / Crucible / Sentinel assurance
  -> Promoter no-promotion decision
```

The fixture performs no provider call, credential access, deployment,
publication, release, upstream mutation, or live self-modification. Each
component consumes producer-owned artifacts and emits its existing schema. If
an edge cannot currently execute from a clean source workspace, that is a
baseline gap to repair in the owning repository rather than bypass in the
runner.

### Layer 4: Semantic parity

Normalize only declared environmental fields: absolute root, path separator,
executable suffix, shell name, timestamps, durations, process identifiers, and
archive format. Compare all contract-significant fields exactly, including:

- repository and runtime identities;
- mission, correlation, goal, workgraph, and action identities;
- authorization and policy outcomes;
- dependency and state transitions;
- execution and evaluator dispositions;
- evidence member paths, logical sizes, and content digests where canonical;
- observation and readback status;
- assurance results;
- promotion, provider, and RSI denial fields; and
- cleanup disposition.

A normalization rule must be named in the manifest and covered by a negative
test. Undeclared disagreement fails parity.

### Layer 5: Cleanup

Stop only processes started by the fixture, close loopback listeners, and
remove only the run-owned temporary root. Preserve source checkouts and final
evidence. Require zero run-owned processes, services, listeners, leases, and
temporary state. Cleanup failure is a failed baseline result, even when the
workflow result passed.

## Evidence Model

Each host writes a canonical JSON result plus a manifest of all retained files.
The host result includes the baseline-manifest digest, platform and architecture,
toolchain readback, repository identities, per-gate results, full-stack result,
normalization profile, cleanup result, and zero-authority counters.

A separate comparison step consumes the two host results, verifies their
manifests and digests, and writes one parity verdict. The comparison does not
trust a host's self-declared pass status. It independently checks required
sections, exact baseline identity, allowed normalization, semantic equality,
and cleanup.

Historical Windows remediation evidence remains immutable. The new result may
reference it as background but must not inherit its readiness status or digest
claims. The new parity evidence is self-contained and internally rehashed.

## Error Handling And Recovery

- Fail before mutation when the destination, manifest, upstream, commit, tool,
  or runtime asset identity is ambiguous.
- Never overwrite, merge into, clean, or reset an existing repository.
- Preserve failed-run evidence and print the exact failed layer and next safe
  diagnostic command.
- A failed comparison is not rerun authority. Correct the owning source or
  manifest through its normal review path, freeze a new baseline identity, and
  execute a fresh qualification.
- Resume is allowed only for read-only evidence comparison. Materialization and
  the full-stack workflow use new run roots.

## Test Strategy

Implementation follows red-green-refactor. Offline tests cover strict manifest
parsing, duplicate repositories, unsafe paths, dirty repositories, missing or
wrong commits, mismatched assets, archive traversal, unsupported tools,
platform-override allowlisting, normalization, semantic disagreement, bounded
logs, partial results, and cleanup classification.

Integration tests use local fixture repositories and archives before any public
download or hosted execution. Native hosted jobs then run the same baseline on
macOS arm64 and Windows x86_64 from empty workspaces and paths containing
spaces. The final comparison job downloads both evidence artifacts and verifies
them independently.

## Completion Criteria

The cross-platform development baseline is complete only when:

1. The baseline manifest is independently reviewed and binds every stable-profile
   repository, source commit, runtime release, asset digest, toolchain policy,
   and platform override.
2. Fresh empty-root materialization succeeds on macOS and Windows.
3. Every required repository-owned development gate passes, with only declared
   capability-dependent skips.
4. The complete credential-free AO workflow reaches the same terminal semantic
   state on both platforms.
5. Independent comparison reports no undeclared differences.
6. Both hosts prove zero run-owned residue.
7. All evidence manifests rehash with zero missing, extra, size, or digest
   failures.
8. Architecture verification and required pull-request checks pass.
9. The final documentation names the exact baseline identity and states that it
   is suitable as the AO dependency foundation for later AO Office Pool
   development without claiming that Office Pool itself has begun.

## Delivery Sequence

1. Export and review the clean macOS reference identity.
2. Add the development-baseline manifest schema and verifier.
3. Add safe materialization and existing-workspace verification.
4. Add repository-gate orchestration and evidence capture.
5. Add the full-stack credential-free fixture.
6. Add semantic normalization and comparison.
7. Run clean hosted macOS and Windows qualification.
8. Repair only observed owning-repository gaps and repeat with a new frozen
   identity when required.
9. Publish the reviewed Architecture baseline declaration and handoff.

