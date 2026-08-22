# AO Architecture Agent Instructions

## Status And Role

AO Architecture is the public documentation, topology, contract-map, and claim-boundary source for the AO stack. It describes component authority and evidence; it does not implement component runtime behavior or grant release, deployment, provider, credential, or mutation authority.

## Sources Of Truth

- [README.md](README.md) and [overview/README.md](overview/README.md) define the public stack narrative and component map.
- [stack/authority-inventory.json](stack/authority-inventory.json), [stack/contract-inventory.json](stack/contract-inventory.json), and [stack/contract-owner-registry.json](stack/contract-owner-registry.json) are the machine-readable authority and contract indexes.
- [docs/contract-evolution-policy.md](docs/contract-evolution-policy.md) and [docs/adr](docs/adr/) record compatibility and architecture decisions.
- [docs/agent-instructions/README.md](docs/agent-instructions/README.md) and its versioned manifest/schema define the repository-instruction layout.
- [docs/quality-gates/README.md](docs/quality-gates/README.md), its versioned schema/registry, and root `ao-quality-gates.json` define the source-owned developer-quality contract.
- [overview/PRODUCTION-READINESS.md](overview/PRODUCTION-READINESS.md) states the documentation readiness boundary; it is not a product release approval.

## Ownership And Boundaries

- Keep public claims, repository links, successors, lifecycle labels, and authority boundaries consistent across the README, component mirrors, topology, and machine-readable contracts.
- AO Next is an active hosted experimental execution candidate only for the bounded successor-feasibility decision in `docs/adr/2026-08-22-ao-next-bounded-successor-feasibility.md`. Its inventory entry does not authorize succession, migration, providers, release, publication, deployment, promotion, or Mission-state ownership.
- Treat source repositories as owners of their implementations. A standalone clone must not assume sibling repositories exist; cross-stack commands must require an explicit workspace root.
- Do not reinterpret historical evidence, release manifests, or result records as current authority. Update them only through their owning contract and verifier.
- Generate `images/*.svg` with `python3 scripts/generate_architecture_svgs.py`; do not hand-tune generated markup.
- Do not place repository instructions in component documentation mirrors, evidence material, generated output, or `hackathon/`.
- Keep public files free of secrets, credentials, private hostnames, account identifiers, and user-specific paths.

## Working Method

- Make the smallest coherent documentation or contract change and update every affected producer/consumer reference in the same pull request.
- For instruction-layout changes, update the ADR, guide, manifest, schema, validator, and tests together. Add a nested scope only for a materially distinct authority boundary.
- Keep repository-specific quality commands in each source repository. Architecture validates lifecycle coverage and contract compatibility but does not execute or invent sibling commands.
- Preserve fail-closed parsing, deterministic output, read-only validation, the excluded local-repository fingerprint, and the pinned head, tracked-state, and exact-name classification gates for the four excluded legacy-hosted repositories.
- If durable commands, authority, lifecycle, or architecture guidance changes, update this file in the same pull request.

## Verification

- Instruction layout: `python3 -m unittest scripts.test_verify_agent_instruction_layout`, then `python3 scripts/verify_agent_instruction_layout.py --workspace-root .. --repository ao-architecture`.
- Architecture or public-documentation changes: `python3 scripts/verify_architecture.py`.
- Contract/schema changes: run the matching `scripts/verify_*.py` and `scripts/test_verify_*.py` pair, then the architecture verifier.
- Quality-gate changes: `python3 -m unittest scripts.test_verify_quality_gate_registry`, then `python3 scripts/verify_quality_gate_registry.py --workspace-root .. --repository ao-architecture --repository-root .`.
- Always run `git diff --check`. Report any skipped, failed, network-dependent, or unavailable check explicitly.

## Evidence And Completion

- Completion requires the changed links and contracts to resolve, focused checks to pass, the architecture verifier to pass, and the pull-request CI result to be recorded.
- Do not edit `stack/current-release-manifest.json`, compatibility results, readiness evidence, or historical claim records merely to make prose or a validator pass.
- A documentation change does not authorize a tag, release, deployment, publication, provider call, credential use, or live qualification.
