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
Version 2 evidence, emitted by generator version 1.2.0, is a self-contained
download bundle: artifact paths are regular basenames resolved relative to the
evidence file, so independent verification does not depend on the producer
workspace layout.
The verifier rejects malformed or duplicate-key JSON, stale evidence, path
traversal, symlinks, non-regular files, digest substitution, unsupported
targets, binary/metadata substitution, and unexpected components. Candidate
archives carry the exact binary and `go-modules.json`; independent verification
re-extracts build information from that archived binary with the trusted reader
and compares it with the digest-bound metadata. Archive member count, type,
name, compressed size, and aggregate expanded size are bounded during streaming
extraction. The archive must contain exactly the binary, metadata, SBOM,
dependency lock, license, and optional notice. Its SBOM, lock, and metadata must
match the downloadable bundle byte for byte. SBOM components and lock entries
are then derived from and checked against the archived binary metadata instead
of trusting the evidence's component list.

The resulting provenance strength is `embedded_build_metadata` and
`cryptographic_source_attestation` is false. The verifier proves that the
downloaded binary embeds the declared clean Git revision and target and that
the evidence digests bind that binary. It does not claim that the source
identity was cryptographically attested by the build platform. Adding such an
attestation requires a separately governed permission and workflow decision.

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
with supported toolchains that predate `go version -m -json`. It projects the
runtime structs into an owned canonical JSON shape so independent readers on
different supported Go versions produce byte-identical metadata. The packager
rejects metadata whose Git revision, modified state, GOOS, or GOARCH does not
match the declared source and target. Synthetic candidate versions are derived
from that validated revision. It also rejects unbound module replacements,
unsummed modules, and dependencies absent from the lockfile. Producer workflows
must compile and test the binary from a clean source tree before checking out
policy tooling or creating other untracked workspace files.

This policy and its readbacks do not authorize release, publication,
deployment, provider calls, credential use, or repository mutation.
