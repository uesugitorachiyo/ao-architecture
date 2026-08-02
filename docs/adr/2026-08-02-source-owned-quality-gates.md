# Source-Owned Quality Gates

## Status

Accepted for staged portfolio adoption.

## Decision

AO Stack uses one versioned manifest shape with repository-specific manifests stored at each maintained repository root. AO Architecture owns the schema, lifecycle registry, and read-only compatibility verifier. AO2 is the reference executor. Source repositories retain ownership of their commands, triggers, timeouts, generated paths, and full verification.

Commit and push declarations are deterministic local accelerators. They bind exact staged or outgoing snapshots, disable network and source mutation, and never replace hosted required checks. Hook wrappers contain no selection policy and remain optional.

The registry separates `planned` from `adopted`. Planned entries establish complete portfolio scope without inventing commands for another repository. Adopted entries require a valid source-owned manifest. Any present planned manifest is still validated.

## Consequences

- AO2 cannot hard-code native commands for sibling repositories.
- Architecture cannot claim a repository has adopted the contract until its source manifest exists and validates.
- Fast feedback remains bounded while shared-impact triggers may select broader repository-owned checks.
- Git hook bypass does not weaken branch protection because hosted CI remains authoritative.
- Semantic review, correction, and refactor assessment are separate later contracts.
