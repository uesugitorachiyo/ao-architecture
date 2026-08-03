# AO Stack Supply-Chain Policy

`stack/distributable-inventory.json` classifies all maintained hosted and
local-only repositories without changing lifecycle. Archive, container, and
public-release classes require a deterministic CycloneDX 1.5 SBOM. Source-only
and unpackaged local-only tools remain outside the SBOM producer requirement,
but every maintained repository requires a root license.

Candidate evidence is bound to the exact repository, source SHA, version,
target, compiled-binary SHA-256, Go build-metadata SHA-256, clean Git revision,
archive SHA-256, SBOM SHA-256, generator name and version, dependency lock
SHA-256, completion timestamp, and deterministic regeneration digest.
The verifier rejects malformed or duplicate-key JSON, stale evidence, path
traversal, symlinks, non-regular files, digest substitution, unsupported
targets, binary/metadata substitution, and unexpected components. Candidate
archives carry the exact binary and `go-modules.json`; independent verification
re-extracts build information from that archived binary with the trusted reader
and compares it with the digest-bound metadata.

Validate the source contracts with:

```sh
python3 scripts/verify_supply_chain_policy.py \
  --inventory stack/distributable-inventory.json \
  --policy stack/sbom-policy.json \
  --release-classification stack/component-release-classification.json \
  --validate-contracts
```

Artifact verification additionally requires explicit `--expected-source-sha`,
`--expected-version`, and `--expected-target` values from the candidate build.
The stable inventory classifies repositories and supported targets; it does not
pin a moving candidate identity.

Go producers may build deterministic candidate archives and evidence with
`scripts/build_go_supply_chain_candidate.py`. The tool consumes an already
built binary, exact metadata emitted by
`go run scripts/read_go_binary_metadata.go <binary>`, an exact dependency
input, and a required root `LICENSE`; `NOTICE` is packaged when the producer
owns one. The reader uses Go's `debug/buildinfo` API and remains compatible
with supported toolchains that predate `go version -m -json`. The packager
rejects metadata whose Git revision, modified state, GOOS, or GOARCH does not
match the declared source and target. Synthetic candidate versions are derived
from that validated revision. It also rejects unbound module replacements,
unsummed modules, and dependencies absent from the lockfile. Producer workflows
must compile and test the binary from a clean source tree before checking out
policy tooling or creating other untracked workspace files.

This policy and its readbacks do not authorize release, publication,
deployment, provider calls, credential use, or repository mutation.
