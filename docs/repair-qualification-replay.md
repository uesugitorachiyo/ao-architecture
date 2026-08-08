# Replay A Repair Qualification

This procedure checks a completed, sanitized repair bundle without running the
repair or contacting the upstream repository. It uses the AO2 verifier and
AO Mission's read-only terminal views. Download the public source inputs and
the sanitized qualification directory before disconnecting the test
environment from the network.

Use the checksum-verified public archives for
[AO2 v0.5.10](https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.10)
and [AO Mission v0.1.3](https://github.com/uesugitorachiyo/ao-mission/releases/tag/v0.1.3).
Record both release tags and tag-target SHAs in the replay evidence.

## Offline Replay

1. Verify the downloaded source archive and dependency-cache SHA-256 values
   against the bundle. Reject a mismatch before extracting or executing
   anything.
2. Reproduce the reported failure with the declared command and platform. Keep
   repair and verification network-disabled, without credentials or Git
   history, when the bundle declares those boundaries.
3. Run the focused regression against the baseline and candidate. Require a
   nonzero baseline result and a zero candidate result.
4. Run the declared full suites for both trees and compare their strict
   summaries. A clean candidate comparison is evidence, not approval.
5. Verify the candidate seal, patch and tree digests, independent-review
   readback, and operator-fork draft capture. The draft must remain open,
   unmerged, and bound to the exact candidate head.
6. Run the installed AO2 verifier:

   ```sh
   ao2 issue repair-qualification verify \
     --bundle <qualification-directory>/bundle.json --json
   ```

   The bundle and its seven sibling JSON artifacts must satisfy the strict
   [AO2 repair qualification contract](https://github.com/uesugitorachiyo/ao2/blob/main/docs/contracts/GITHUB-ISSUE-REPAIR-PACK.md#repair-qualification).
7. Import the verified Atlas canonical terminal index into an operator-owned
   AO Mission home, then inspect all four views:

   ```sh
   ao-mission terminal-index inspect --state <terminal-state.json>
   ao-mission terminal-index checkpoint --state <terminal-state.json>
   ao-mission terminal-index event-index --state <terminal-state.json>
   ao-mission terminal-index command-readback --state <terminal-state.json>
   ```

   Require one shared index digest, canonical payload agreement, and four
   independently valid surface-specific state digests.
8. Interpret `repair_qualified` narrowly: the supplied evidence proves the
   bounded repair under the declared policy. It does not approve a merge,
   recommend maintainer acceptance, grant promotion authority, or authorize a
   release, deployment, publication, provider call, or upstream mutation.

## Negative Check

Change one copied artifact byte without updating the bundle digest and rerun
step 6. The verifier must return `repair_rejected` and exit nonzero. Keep the
original evidence unchanged.

## Current Controlled-Beta State

The operator-fork drafts for
[`mikefarah/yq#2796`](https://github.com/uesugitorachiyo/yq/pull/2),
[`sharkdp/fd#2053`](https://github.com/uesugitorachiyo/fd/pull/1), and
[`pallets/click#3571`](https://github.com/uesugitorachiyo/click/pull/1) are
evidence-only drafts. Their presence does not authorize an upstream pull
request, issue comment, merge, release, or publication.

For broader adoption context, see the
[AO Stack production adoption roadmap](superpowers/specs/2026-08-01-ao-stack-production-adoption-roadmap.md).
