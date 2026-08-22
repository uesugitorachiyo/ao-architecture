# AO Cross-Platform Development Baseline

The stable development baseline is a frozen, public-safe input for reproducing
AO development checks on Windows, macOS, and Linux. It records identities and
constraints; it does not clone repositories, install tools, execute gates, or
grant operational authority.

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

## Authority Boundary

Every authority flag remains false. The baseline grants no execution,
approval, repository mutation, provider call, credential use, release,
publication, deployment, promotion, compatibility activation, external beta,
or RSI authority. Later campaign slices must preserve this boundary and bind
their evidence to both the baseline identity and controller source commit.
