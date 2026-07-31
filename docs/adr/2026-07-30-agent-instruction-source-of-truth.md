# ADR: Repository Agent Instruction Source Of Truth

- Status: Accepted
- Date: 2026-07-30
- Scope: Maintained AO repositories and explicitly excluded legacy checkouts

## Context

AO repositories need durable guidance that is available to different coding-agent providers without turning prose into an enforcement mechanism. Provider-specific files can drift, large always-loaded instruction chains consume finite context, and duplicated operating rules obscure the executable contracts that actually decide whether work is safe and complete.

Codex discovers `AGENTS.md` from the repository root toward the working directory. Claude Code reads `CLAUDE.md` and supports imports. Both systems benefit from concise, concrete, scope-local instructions. Imported content still consumes context.

## Decision

`AGENTS.md` is the canonical provider-neutral repository instruction source. Every maintained repository has a root file containing durable role, authority, source-of-truth, working, verification, and evidence guidance.

Every root or approved nested `CLAUDE.md` is a regular tracked file with exactly:

```text
@AGENTS.md
```

and one final newline. The adapter contains no independent Claude-specific rules. Regular files are used instead of symlinks so the layout behaves consistently on Windows and in tools that do not preserve symlink semantics.

Executable contracts, schemas, policy decisions, tests, approval gates, hooks already owned by a repository, and CI remain authoritative. Instruction prose explains how to work with those controls; it cannot weaken, replace, or grant them.

Multi-step, occasional procedures belong in skills or runbooks. Root instructions stay concise. Nested pairs are limited to materially distinct authority scopes and supplement critical boundaries summarized at the root.

## Lifecycle Treatment

- Active hosted repositories require the root pair, local Claude-state ignores, verified commands, and normal pull-request CI.
- Active local-only repositories require the same instruction shape but remain without remotes or publication authority.
- Archived hosted repositories use short archive-first guidance, identify successors, forbid new product scope, and retain only archive-correction verification.
- `ao-runtime` is a deprecated pre-AO-Stack legacy repository, not an archived AO Stack component. It receives no instruction rollout; the manifest pins its unchanged Git head and the validator rejects tracked drift.
- `ao-covenant-stub-20260617` is an excluded historical local stub. The layout manifest records its exclusion reason and content fingerprint; the campaign must leave it byte-for-byte unchanged.

## Context And Drift Policy

Active root `AGENTS.md` files are limited to 120 lines and 12 KiB. Archived roots are limited to 60 lines and 8 KiB. Nested files are limited to 80 lines and 8 KiB, and a root-to-nested chain is limited to 24 KiB. The exact budgets and scopes are enforced by the versioned layout validator.

Durable command, authority, lifecycle, ownership, or architecture changes must update the applicable `AGENTS.md` in the same pull request. A changed `CLAUDE.md` must remain the exact import adapter. The stack validator rejects missing pairs, drift, unexpected scopes, unsafe paths, secret-like material, excluded-stub modification, and excluded legacy-hosted head or tracked-state changes.

## Consequences

Repositories have one reviewable guidance source and a minimal compatibility adapter. Context remains bounded, scoped rules can be added only where justified, and task procedures can evolve independently in skills. Static validation can prove the layout without a model/provider call or network access.
