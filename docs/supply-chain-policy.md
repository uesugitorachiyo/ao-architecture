# AO Stack Supply-Chain Policy

`stack/distributable-inventory.json` classifies all maintained hosted and
local-only repositories without changing lifecycle. Archive, container, and
public-release classes require a deterministic CycloneDX 1.5 SBOM. Source-only
and unpackaged local-only tools remain outside the SBOM producer requirement,
but every maintained repository requires a root license.

Candidate evidence is bound to the exact repository, source SHA, version,
target, archive SHA-256, SBOM SHA-256, generator name and version, dependency
lock SHA-256, completion timestamp, and deterministic regeneration digest.
The verifier rejects malformed or duplicate-key JSON, stale evidence, path
traversal, symlinks, non-regular files, digest substitution, unsupported
targets, and unexpected components.

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
built binary, `go version -m -json` metadata from that binary, an exact
dependency input, and a required root `LICENSE`; `NOTICE` is packaged when the
producer owns one. It rejects unbound module replacements, unsummed modules,
and dependencies absent from the lockfile. Producer workflows remain
responsible for compiling and testing their binary.

This policy and its readbacks do not authorize release, publication,
deployment, provider calls, credential use, or repository mutation.
