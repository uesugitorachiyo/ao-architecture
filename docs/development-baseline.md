# AO Cross-Platform Development Baseline

The stable development baseline is a frozen, public-safe input for reproducing
AO development checks on Windows, macOS, and Linux. It records identities and
constraints. The S02 bootstrap may clone the declared repositories and download
the declared native runtime assets into an operator-selected empty root; it
does not install system tools, execute repository gates, or grant operational
authority.

## Contract Files

- `stack/development-baseline-manifest.json` is the frozen baseline instance.
- `docs/contracts/development-baseline-manifest-v1.schema.json` is its closed
  JSON Schema.
- `scripts/verify_development_baseline.py` is the read-only, standard-library
  verifier.
- `scripts/test_verify_development_baseline.py` owns positive and fail-closed
  regression coverage.

The manifest pins fourteen stable repositories at exact commits and binds each
repository's source-owned quality-gate locator and gate-source digest. AO Next
is explicitly excluded from the stable profile.

It also binds seven runtime releases to the protected
`stack/current-release-manifest.json`. AO2 Control Plane v0.1.19 and AO
Covenant v0.1.1 lack platform digests in that protected input, so their missing
digests are frozen with producer GitHub release-API provenance. This does not
authorize a network request during verification. Covenant's macOS arm64 path
uses its declared Darwin amd64 asset through Rosetta 2 and is not a native
arm64 claim.

## Identity Model

The verifier reports two deliberately separate identities:

- `baseline_identity` is the SHA-256 of the canonical full manifest. It is
  independent of JSON formatting, checkout location, and controller commit.
- `controller_source_commit` is the exact AO Architecture commit that ran the
  verifier.

The manifest cannot contain the commit that contains itself, so the controller
commit is evidence-bound at invocation time and excluded from the baseline
hash. A verification record is complete only when it retains both values.

## Toolchains And Overrides

The contract declares version probes and constraints for Git, Python, Go,
Rust/Cargo, Node/npm, PowerShell, and POSIX shell. These declarations are
read-only checks, not installers.

The only platform overrides are Git for Windows Bash for `.sh` gates,
PowerShell 5.1 parsing where a source repository owns that contract, Rosetta 2
for Covenant's Darwin amd64 asset on macOS arm64, and native executable/archive
suffix selection. Any additional override fails validation.

## Verification

From the AO Architecture repository, run:

```text
python3 scripts/test_verify_development_baseline.py
python3 scripts/verify_development_baseline.py --manifest stack/development-baseline-manifest.json --controller-commit <exact-architecture-commit>
python3 scripts/verify_architecture.py
git diff --check
```

Use a lowercase forty-character commit for
`<exact-architecture-commit>`, normally from `git rev-parse HEAD`. A successful
verification prints the controller commit, canonical baseline identity, exact
repository and release counts, and `errors=0`. Errors are sorted, written to
standard error, and cause a nonzero exit without modifying files.

## Native Bootstrap

The standard-library controller has two explicit modes. `materialize` requires
an absent or empty run-owned root, validates all S01 inputs before creating it,
checks out the fourteen repositories at detached exact commits, downloads and
hashes the seven native runtime assets, and retains capability evidence under
`.ao-baseline`. `verify-existing` requires that exact retained root, performs
read-only identity and hash checks, and writes its new result outside the root.

On Windows, invoke the PowerShell 5.1-compatible wrapper:

```powershell
$BaselineRoot = Join-Path $env:TEMP "ao baseline"
$MaterializeResult = Join-Path $env:TEMP "ao-materialize-result.json"
$VerifyResult = Join-Path $env:TEMP "ao-verify-result.json"
scripts/bootstrap-development-baseline.ps1 --mode materialize --manifest stack/development-baseline-manifest.json --schema docs/contracts/development-baseline-manifest-v1.schema.json --release-manifest stack/current-release-manifest.json --controller-commit (git rev-parse HEAD) --root $BaselineRoot --result $MaterializeResult
scripts/bootstrap-development-baseline.ps1 --mode verify-existing --manifest stack/development-baseline-manifest.json --schema docs/contracts/development-baseline-manifest-v1.schema.json --release-manifest stack/current-release-manifest.json --controller-commit (git rev-parse HEAD) --root $BaselineRoot --result $VerifyResult
```

On macOS or Linux, invoke the POSIX wrapper with the same arguments:

```sh
scripts/bootstrap-development-baseline.sh --mode materialize --manifest stack/development-baseline-manifest.json --schema docs/contracts/development-baseline-manifest-v1.schema.json --release-manifest stack/current-release-manifest.json --controller-commit "$(git rev-parse HEAD)" --root '/path/with spaces/baseline' --result '/path/with spaces/materialize-result.json'
scripts/bootstrap-development-baseline.sh --mode verify-existing --manifest stack/development-baseline-manifest.json --schema docs/contracts/development-baseline-manifest-v1.schema.json --release-manifest stack/current-release-manifest.json --controller-commit "$(git rev-parse HEAD)" --root '/path/with spaces/baseline' --result '/path/with spaces/verify-result.json'
```

The deterministic result binds the controller commit, baseline identity,
platform, architecture, exact repository commits, asset hashes, toolchain
probes, retained filesystem capabilities, and all-false authority. Partial
materialization is deliberately preserved on failure for diagnosis; reuse is
not allowed, so retry with a new empty root.

## Final Qualification

`.github/workflows/development-baseline-qualification.yml` is the least-authority
merged-main qualification entry point. It fixes the bootstrap scope to `full`,
runs clean `macos-26` and `windows-2025` hosts from paths containing spaces,
executes every declared repository gate and the credential-free workflow,
compares the two retained semantic results, proves exact cleanup, and writes a
relative-path evidence closure.

The comparison policy is independently frozen at
`stack/development-baseline-normalization-v1.json`; it is not part of the source
baseline manifest and therefore does not change the qualified baseline identity.
Offline closure verification is:

```text
python3 scripts/test_verify_development_baseline_evidence.py
python3 scripts/verify_development_baseline_evidence.py --root <downloaded-proof-root> --source-commit <merged-main-commit> --baseline-identity sha256:add6f39f28eba107732398b7bf86db44b58f80f4a6cea89ec6b97f3b18ab6429 --output <new-output-path>
```

The output inventories every retained file by safe relative path, size, and
SHA-256 and fails closed on missing, extra, drifted, unsafe, residual, or
over-authority evidence.

## Authority Boundary

Every authority flag remains false. The baseline grants no execution,
approval, repository mutation, provider call, credential use, release,
publication, deployment, promotion, compatibility activation, external beta,
or RSI authority. Later campaign slices must preserve this boundary and bind
their evidence to both the baseline identity and controller source commit.
