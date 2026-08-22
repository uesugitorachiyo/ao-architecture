# Safe Development Baseline Materialization Design

## Purpose

Implement S02 of the AO cross-platform development-baseline campaign: create
the same exact fourteen-repository sibling workspace and native runtime asset
set from empty inputs on macOS and Windows, or verify an existing workspace
without modifying it.

This slice performs public Git and release-asset retrieval only. It grants no
provider, credential, execution, approval, repository-mutation-after-checkout,
release, publication, deployment, promotion, compatibility, external-beta,
RSI, or AO Office Pool authority.

## Considered Approaches

### Recommended: one standard-library controller with thin native wrappers

A Python controller owns validation, Git argv, bounded downloads, safe
extraction, preflight, and evidence. PowerShell and POSIX shell wrappers only
locate Python and forward argv unchanged. This gives both hosts one behavioral
implementation while retaining native entry points and PowerShell 5.1 parsing.

### Rejected: separate PowerShell and shell implementations

Two implementations would duplicate path, archive, Git, and digest rules and
make semantic drift likely precisely where the campaign is trying to remove
platform variance.

### Rejected: container-only materialization

A container would hide native Windows filesystem, reparse-point, PowerShell,
locking, executable-suffix, and CRLF behavior. Docker remains useful diagnostic
context but cannot qualify the native baseline.

## Inputs And Modes

The controller is
`scripts/bootstrap_development_baseline.py`. It requires the S01 manifest,
its schema, the protected current-release manifest, an exact lowercase
controller commit, an operator-selected root, and a result path.

Exactly two modes exist:

- `materialize`: the root must not exist or must be an empty, non-symlink,
  non-reparse directory. The controller creates only run-owned paths, clones
  all fourteen repositories, checks out detached exact commits, downloads the
  seven native runtime assets, and writes evidence.
- `verify-existing`: every expected sibling and `.ao-baseline` must already
  exist. The controller performs no write, checkout, fetch, reset, cleanup,
  dependency update, or repair. The result path must be outside the verified
  root.

The controller imports the S01 verifier and revalidates the manifest, schema,
and protected release input before any destination mutation. Its reported
`baseline_identity` must exactly match the S01 canonical digest.

## Root And Path Safety

Before mutation, the controller resolves the destination parent and inspects
every existing path component with `lstat`. It rejects symlinks and Windows
reparse points. It then requires the destination to be absent or an empty
regular directory. Repository names come only from the validated manifest and
must be safe single components.

Every created or inspected repository and `.ao-baseline` path is checked for
containment beneath the selected root before use. Existing materialization
rejects missing entries, extra top-level entries, symlink/reparse entries,
case-fold collisions, and any resolved path outside the root. Paths containing
spaces are ordinary supported inputs.

## Repository Materialization

For each manifest repository in canonical order, the controller uses explicit
argv arrays and a minimal environment:

1. `git clone --no-checkout --no-tags <upstream> <sibling>`
2. `git -C <sibling> checkout --detach <exact-commit>`

Git receives `GIT_TERMINAL_PROMPT=0` and `GCM_INTERACTIVE=Never`. The
controller never reads credential configuration, changes global Git settings,
uses a moving branch as identity, or invokes a shell command string.

After checkout it requires:

- `HEAD` equals the exact frozen commit;
- `symbolic-ref -q HEAD` reports detached state;
- origin matches the canonical upstream;
- tracked and untracked status is empty;
- submodule status contains no missing, modified, or conflicted entry; and
- the repository path remains contained and non-reparse.

A failure preserves the partial run root for diagnosis and writes a failed
result outside it when possible. It never cleans or repairs a failed checkout.

## Runtime Assets

Each host selects exactly one manifest asset per runtime release: `macos` on
macOS, `windows` on Windows, and `linux` for supported local diagnostics.
The download URL is the immutable release URL plus
`/download/<percent-encoded-name>`.

Downloads use HTTPS only, a fixed timeout, a 256 MiB compressed-byte maximum,
bounded streaming, exclusive destination creation, and no credential headers.
The SHA-256 is checked before any extraction.

Tar and ZIP extraction rejects absolute paths, drive/UNC paths, `..`
traversal, empty or duplicate names, symlinks, hard links, devices, FIFOs,
unknown member types, more than 1,024 members, any member larger than 256 MiB,
or total expanded bytes above 512 MiB. Extracted paths are containment-checked
before exclusive writes. Plain Covenant executables are copied only after
digest verification. No archive permission may introduce setuid/setgid bits.

Assets live beneath
`.ao-baseline/assets/<repository>/<asset-name>`; extracted files live beneath
`.ao-baseline/runtime/<repository>`.

## Native Preflight

Preflight executes the manifest's fixed version argv without a shell and
evaluates exact-major or minimum version constraints. It records Git, Python,
Go, Rust, Cargo, Node, npm, PowerShell, and Bash versions.

Capabilities record, without changing the host:

- OS and architecture;
- filesystem case behavior;
- symlink capability and classification;
- Windows reparse, long-path, CRLF, file-locking, executable-suffix,
  PowerShell 5.1/7, and Git Bash observations;
- macOS permission behavior and the Covenant Rosetta 2 requirement; and
- path-with-spaces success.

A required tool or declared override prerequisite that is absent fails S02.
Capability-dependent observations are never silently converted to skips.
Filesystem capability probes run only in the materializer-owned
`.ao-baseline/` area. `verify-existing` revalidates the retained probe evidence
and may run read-only version commands, but it never creates a probe file.

## Deterministic Evidence

The result is strict JSON with:

- schema, mode, status, correlation and slice;
- controller commit and canonical baseline identity;
- platform and architecture;
- canonical repository entries with commit, origin, detached and clean status;
- seven selected assets with name, expected/actual digest, bytes, and
  extraction disposition;
- toolchain and native capability readbacks;
- bounded command summaries;
- failure category and exact safe diagnostic when failed; and
- the complete all-false authority object.

Absolute roots, timestamps, durations, process identifiers, and private host
details are excluded from the canonical identity section. The result file is
written atomically only to the explicit result path.

The hosted workflow uploads the host result and a SHA-256 manifest. Cleanup
runs after artifact staging, removes only the matrix job's unique runner-temp
root, proves it absent, and uploads a cleanup result. A separate job downloads
both host artifacts, independently rehashes every retained file, and emits one
rehash report.

## Native Wrappers And Workflow

`scripts/bootstrap-development-baseline.ps1` parses under Windows PowerShell
5.1, selects `py -3` or `python`, and forwards all arguments as an array.
It sets no policy, credentials, execution mode, or global state.

`scripts/bootstrap-development-baseline.sh` uses POSIX shell syntax, selects
`python3` or `python`, and `exec` forwards argv exactly.

`.github/workflows/development-baseline-bootstrap.yml` is
`workflow_dispatch` only. Its matrix is exactly `macos-26` and
`windows-2025`; each job uses a unique empty runner-temp root, invokes the
native wrapper in materialize mode, verifies the same baseline identity and
fourteen repositories, uploads evidence, and performs exact-root cleanup.
The independent rehash job has no repository mutation or authority.

## Failure And Recovery

All input, manifest, root, and containment checks occur before destination
mutation. Once materialization begins, failures retain partial content and
produce bounded evidence. Rerun requires a new empty root; there is no resume,
overwrite, merge, reset, or automatic cleanup path.

`verify-existing` returns nonzero on any mismatch and leaves the workspace
byte-for-byte unchanged.

## Testing

Offline standard-library tests use local temporary Git repositories, synthetic
archives, and loopback-free byte streams. They cover:

- empty-root and exact sibling enforcement;
- detached exact-commit and origin verification;
- dirty, missing, extra, and upstream-drift repositories;
- symlink/reparse traversal and capability classification;
- tar/ZIP traversal, unsafe member types, counts, sizes, and digest drift;
- bounded downloads and exclusive writes;
- spaces, case behavior, CRLF evidence, and file locking;
- version parsing and toolchain constraint failures;
- deterministic result ordering and false authority; and
- PowerShell 5.1 parser compatibility.

Required local gates are the focused test file, Windows PowerShell parser,
Architecture verifier, and `git diff --check`. Hosted S02 passes only when
both native jobs, both cleanup results, and the independent rehash report close
with the exact S01 baseline identity.

## Approval

The operator granted standing approval on 2026-08-22 to complete S02-S07
proactively. This approval does not relax any technical, evidence, cleanup, or
denied-authority gate.
