# Uniform AO Public Stack Release Design

## Status

Approved for implementation planning on 2026-08-23. This design authorizes a
bounded public release campaign for AO Mission and AO2, followed by an
Architecture-owned stack refresh and qualification. It does not authorize
provider execution, deployment, promotion, compatibility activation, external
beta, RSI, or changes to unrelated component binaries.

## Problem

The current seven-component public stack is coherent and independently
qualified, but two user-facing capabilities exist only after the published
source targets:

- AO Mission `main` adds read-only AO Next candidate import and evidence-bound
  S01-S07 checkpoints after public `v0.1.5`.
- AO2 `main` adds the qualified physical-Windows profile to the existing
  outbound worker after public `v0.5.11`. The worker is source-owned Python and
  is not currently an installed Windows release entry point.

Publishing every component again would create no-op releases and obscure the
actual compatibility change. Publishing Mission alone would leave the Windows
operator path source-only. The stack therefore needs a targeted release train
and one refreshed mixed-version stack declaration.

## Goals

1. Publish AO Mission `v0.1.6` from one reviewed exact source head.
2. Publish AO2 `v0.5.12` with a supported Windows outbound-worker entry point.
3. Retain existing versions for components whose user binaries did not change.
4. Keep AO2 Control Plane `v0.1.19` when exact compatibility qualification
   passes; publish `v0.1.20` only if its owned version-pair contract must change.
5. Update AO Architecture only after public assets exist and are independently
   rehashed.
6. Freeze and qualify a new 14-repository development baseline and seven-binary
   public stack on Linux, macOS, and Windows.
7. Present users with one canonical stack matrix, install path, and evidence
   set even though component semantic versions differ.

## Non-Goals

- Do not release unchanged AO Command, AO Atlas, AO Forge, or AO Covenant
  binaries merely to align version numbers.
- Do not create releases for Architecture, Blueprint, Foundry, Arena,
  Crucible, Sentinel, or Promoter.
- Do not port the Windows worker to Rust, create a universal installer, or add
  a new package manager.
- Do not rewrite or replace existing releases, tags, assets, historical
  evidence, or the completed cross-platform baseline declaration.
- Do not perform live provider calls, credentialed AO workloads, deployments,
  promotion, compatibility activation, external beta, or RSI.

## Selected Release Set

| Component | Target | Decision |
| --- | --- | --- |
| AO2 | `v0.5.12` | New public release with Windows worker package |
| AO2 Control Plane | `v0.1.19` | Reuse if compatibility passes |
| AO Mission | `v0.1.6` | New public release with additive read-only CLI behavior |
| AO Command | `v0.1.3` | Reuse unchanged |
| AO Atlas | `v0.2.1` | Reuse unchanged |
| AO Forge | `v0.1.5` | Reuse unchanged |
| AO Covenant | `v0.1.1` | Reuse unchanged |

If Control Plane `v0.1.19` rejects AO2 `v0.5.12` solely because of an exact
source-owned version-pair declaration, the campaign may add that pair through
the normal reviewed Control Plane path and publish `v0.1.20`. Any protocol,
schema, storage, authentication, or runtime incompatibility stops the campaign
for a separate design review.

## AO2 Windows Package Contract

The AO2 `v0.5.12` Windows archive retains `ao2.exe` and adds:

- `ao2-windows-outbound-worker.py`, byte-bound to the reviewed source file;
- `ao2-windows-worker.cmd`, a logic-minimal launcher that selects Python 3.11
  or newer, forwards arguments without evaluating them, and fails clearly when
  the required interpreter is unavailable;
- a package inventory entry and digest for each added file.

The worker remains Python standard-library only. The launcher does not discover
credentials, create a listener, modify global configuration, or infer task
authority. Packaging tests must cover paths containing spaces, missing or old
Python, argument forwarding, `--help`, offline bounded-lease validation, and
archive traversal/link rejection. Public qualification invokes only `--help`
and a synthetic offline lease path; it makes no Control Plane or provider call.

Linux and macOS AO2 archives remain binary-only. Documentation must state that
the outbound worker is a Windows operator capability with Python 3.11 as an
explicit prerequisite, not a cross-platform AO2 runtime command.

## AO Mission Release Contract

AO Mission `v0.1.6` includes the exact merged implementations for:

- strict read-only import of `ao.next.live-run-record.v1` as a candidate
  projection; and
- strict, ordered, evidence-bound, idempotent S01-S07 checkpoints.

The release keeps all lifecycle and authority semantics unchanged. Release
tests must prove version output, new command help, one valid checkpoint replay,
invalid order and digest rejection, candidate-import idempotence, and absence
of execution, approval, mutation, provider, publication, or promotion flags.

## Release Flow

Each publishing repository follows its existing source-owned release process:

1. Create release metadata and tests on a task branch.
2. Merge through required pull-request review and CI.
3. Produce exact-head candidates through the non-publishing rehearsal.
4. Independently validate candidate inventory, version output, checksums,
   SBOM/provenance, signatures or attestations, and functional smoke evidence.
5. Run the finalizer in dry-run mode against the exact producer run.
6. Run the live finalizer with the source-owned exact confirmation string.
7. Read back the immutable tag target, release record, asset names, sizes, and
   SHA-256 values through a fresh public download.

AO Mission and AO2 are released independently. AO2 Control Plane compatibility
qualification occurs after AO2 publication and before Architecture declares
the new stack current.

## Architecture Refresh

After all selected public assets pass fresh download verification, AO
Architecture updates the current-release manifest and public release document
with exact tags, tag targets, asset counts, names, sizes, and SHA-256 values.
The development-baseline manifest is regenerated from reviewed current source
heads and the refreshed release input; the resulting canonical digest becomes
a new baseline identity. The previous baseline and declaration remain
historical and unchanged.

The public stack canary must install only the new public manifest. The
development-baseline qualification must materialize only the new exact source
manifest. Neither workflow may silently fall back to local repositories,
moving branches, existing installations, caches, or prior campaign roots.

## Qualification And Evidence

Terminal success requires:

- exact public tag and asset verification for AO Mission `v0.1.6` and AO2
  `v0.5.12`;
- a passing AO2 `v0.5.12` / Control Plane compatibility decision;
- clean public-stack installation on Linux x86_64, macOS arm64, and Windows
  x86_64;
- version and credential-free smoke checks for all seven public components;
- Windows launcher and worker preflight from a path containing spaces;
- a clean 14-repository development-baseline materialization on `macos-26` and
  `windows-2025`;
- every required repository gate and credential-free workflow stage passing;
- zero semantic differences, undeclared skips, run-owned residue, digest
  mismatches, provider calls, credential use, or authority widening;
- independent download, rehash, and closure of all retained evidence; and
- green merged-main CI and clean task-branch cleanup in each changed repository.

Evidence must retain exact source heads, workflow and job IDs, runner labels,
artifact names, byte sizes, SHA-256 values, version output, compatibility
decision, baseline identity, declared skips, cleanup results, and all-false
authority flags. Private paths and credentials must not enter public evidence.

## Failure Handling

- A failed rehearsal or dry-run finalizer creates no tag or public release.
- A failed live finalizer is inspected before retry; the campaign never deletes
  or overwrites a public tag, release, or asset to hide partial publication.
- A published component that fails public download verification is not added to
  Architecture's current stack. Preserve its evidence and repair through the
  repository's release process.
- A Control Plane protocol or runtime incompatibility blocks the stack refresh.
  Only an exact version-pair metadata mismatch permits the conditional
  `v0.1.20` path.
- A failed host, parity, cleanup, or evidence-closure gate blocks the new stack
  declaration. Retry only from a new empty qualification root after the owning
  fix is reviewed and the baseline is regenerated when its source changes.

## Completion Boundary

Completion means the refreshed mixed-version public stack is documented,
publicly downloadable, independently rehashed, compatible, and qualified on
all declared hosts. It does not mean deployment, provider activation,
promotion, external beta, AO Next succession, RSI, or AO Office Pool execution.
