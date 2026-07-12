# AO Stack External-Beta Preflight Closure Design

## Status

Approved for implementation by the operator prompt dated 2026-07-12. This
design authorizes documentation and preflight work only. It does not authorize
a release, deployment, publication, tag, upload, provider call, credential
inspection, authority widening, or RSI claim.

## Source Of Truth

AO Architecture owns one machine-readable tested-stack manifest. The manifest
pins all fourteen repositories, distinguishes Month 6 evidence heads from the
heads tested for this preflight, records maturity and capability labels, and
binds the final Month 6 Atlas launch-readiness artifact by path and digest.

Component repositories continue to own implementation details and local
commands. Their READMEs link to the Architecture topology and component page.
They do not restate the stack topology. Covenant remains the source of policy
and contract truth.

## Workspace Reconciliation

The local AO Architecture `main` branch contains three preserved Helix planning
commits and is behind `origin/main`. Helix is excluded from this external-beta
preflight because it is planned work outside the thirteen active components and
has no beta authority. Work proceeds from an isolated `origin/main` worktree.

AO Promoter's `codex/mission-v02-hardening` branch remains preserved. The
external-beta readback starts from `origin/main`, where the operator
no-promotion rollup was merged separately. No commit from the preserved branch
is rewritten or silently incorporated.

## Documentation Contract

Every component README must expose the same concise fields:

- canonical Architecture topology link;
- repository-specific Architecture component-page link;
- role and implementation boundary;
- maturity and capability classification;
- install and quickstart commands owned by that repository;
- safety and denied-authority statement;
- external-beta status that explicitly says no beta has launched.

Allowed capability labels are `implemented`, `executable-tested`,
`clean-room-rehearsed`, `fixture-only`, `planned`, and `unauthorized`.
Historical campaign detail belongs in the evidence catalog, not landing pages.

## Preflight Package

Architecture owns the reproducible external-beta package: checklist, operator
runbook, feedback intake, security-review intake, installation rehearsal, and
rollback rehearsal. All procedures use clean checkouts and local verification.
They must remain dry-run or rehearsal instructions and must not perform live
beta or release actions.

## Verification And Closure

A cross-repository verifier reads the canonical manifest, resolves sibling
repositories, checks exact pinned heads, validates required README sections and
canonical links, and checks local Markdown/image links. Architecture CI runs
the verifier in repository-only mode; the clean-checkout run verifies the full
workspace.

Final Sentinel, Promoter, and Command artifacts must agree that wording is
clear, no promotion was requested, no beta launched, and RSI remains denied.

