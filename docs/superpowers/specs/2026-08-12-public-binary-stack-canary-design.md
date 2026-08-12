# Public Binary AO Stack Canary Design

## Purpose

Prove that a new operator can assemble and inspect the supported seven-component AO Stack from public GitHub releases on Linux x86_64, macOS aarch64, and Windows x86_64 without private context, credentials, provider calls, or repository mutation.

The canary covers these fixed releases:

- AO2 `v0.5.11`
- AO2 Control Plane `v0.1.19`
- AO Mission `v0.1.4`
- AO Atlas `v0.2.0`
- AO Command `v0.1.2`
- AO Forge `v0.1.4`
- AO Covenant `v0.1.1`

## Design

Add one standard-library Python runner, one offline unit-test file, and one GitHub Actions workflow. The runner owns a static manifest of public URLs, asset names, and SHA-256 digests for each supported target. It downloads each selected asset into a temporary directory, verifies the digest before extraction, rejects unsafe archive entries, and installs only the expected executable inventory.

The runner executes component-owned, credential-free identity and read-only smoke commands. It verifies the seven pinned versions, uses Atlas to build and verify a terminal index, imports that index through Mission's four read-only surfaces, and has Command validate a status record for the same Mission identity. Mission owns the Command-compatible terminal readback; Command v0.1.2 does not import terminal indexes directly. AO2's separate native release verification remains the source of truth for its full install, doctor, disposable fixture, and uninstall contract; this canary checks its public binary identity and its place in the assembled stack rather than duplicating that qualification.

The macOS lane runs on an arm64 hosted runner. Covenant v0.1.1 publishes only a Darwin amd64 executable, so that one binary runs through Rosetta 2 and the report records the translation explicitly. Every other macOS binary is native arm64. This is the exact supported public asset set, not a claim that Covenant v0.1.1 has a native arm64 artifact.

Each run writes one JSON result containing the target, public URLs, byte counts, digests, commands, exits, timing, and cleanup outcome. The workflow runs the same runner on `ubuntu-latest`, `macos-latest`, and `windows-latest` and uploads one result per platform. Generated results stay outside source control.

## Trust Boundaries

The canary fails closed on download errors, digest drift, duplicate or missing files, path traversal, absolute paths, symlinks, bounded download or expansion limits, wrong versions, unexpected command exits, runner/target mismatches, and reconciliation mismatches. ZIP and tar extraction use Python's standard library and copy only validated regular files.

The workflow receives no repository token beyond GitHub's default read-only checkout access and no AO or provider credentials. Child processes receive an allowlisted system environment plus a temporary Mission home, not the runner environment. The workflow does not create releases, tags, deployments, issues, pull requests, or repository writes. Terminal reconciliation remains read-only evidence and grants no downstream authority.

## Tests

Offline unit tests cover manifest completeness, per-target asset selection, digest rejection, safe tar and ZIP extraction, unsafe-path rejection, raw executable installation, command-result recording, and deterministic result validation. Implementation follows red-green-refactor. Local macOS validation then uses the real public assets. Hosted GitHub Actions supplies native Linux, macOS, and Windows evidence.

## Completion

The change is complete when offline tests and Architecture verification pass locally, the pull request is reviewed and merged with all three hosted canaries green, each uploaded result is independently downloaded and digest-verified, and the evidence is bound into the release campaign manifest. The canary does not publish or promote any component.
