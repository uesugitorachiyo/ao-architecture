# Mutation Authority Ladder

This page is the architecture mirror for governed live repository mutation
authority across AO Atlas, AO Foundry, AO Covenant, AO Forge, AO2, AO Sentinel,
AO Promoter, and AO Command. It distinguishes dry-run readiness from approved
live mutation and from the still-denied fully unsupervised RSI claim.

The highest proven live mutation class is
`fully_unsupervised_complex_mutation`. That means the stack can point to
governed live rehearsal evidence through the docs-only, test-only, low-risk
code, multi-repo low-risk, 12-node complex mutation, and 26-node fully
unsupervised complex first non-planning classes. It does not mean fully
unsupervised RSI is proven.

| Class or claim boundary | Current public state | What is allowed | What remains denied |
| --- | --- | --- | --- |
| `docs_only_single_file` | Proven live rehearsal class. | Exact-scope docs-only approval, rollback, Sentinel, Promoter, Command readback, CI, PR lifecycle, and merge evidence can support one bounded docs-only live mutation. | Broad docs authority, config/code changes, or unsupervised follow-on mutation. |
| `docs_only_multi_file` | Proven live rehearsal class. | A bounded docs-only multi-file PR can proceed only inside its max-file limit and class gates. | More than the class file limit, code edits, config edits, or automatic class promotion. |
| `docs_config_only` | Modeled mutation class, not a broader live authority claim. | Dry-run classification can identify docs/config-only scope when its gates exist. | Treating config-adjacent files as low-risk code or bypassing Covenant/Sentinel/Promoter. |
| `test_only` | Proven live rehearsal class. | One bounded test-only live rehearsal can be approved when rollback, CI, Sentinel, Promoter, Command readback, and exact class evidence pass. | Production code changes, broad test rewrites, or using test-only success as live code authority. |
| `low_risk_code` | Proven live rehearsal class. | One bounded low-risk code live rehearsal can be approved when lower-class evidence, rollback, CI, Sentinel, Promoter, Command readback, and class ticket evidence pass. | Broad code changes, auth/policy/provider/release/deploy surfaces, or automatic class promotion. |
| `multi_repo_low_risk` | Proven live rehearsal class. | Serialized repo-by-repo live rehearsal can proceed with per-repo rollback, CI, branch cleanup, no concurrent mutation, Sentinel, Promoter, and Command evidence. | Concurrent repo mutation, shared-surface expansion, or unsequenced multi-repo execution. |
| `complex_repo_mutation` | Proven live rehearsal class. | The governed 12-node complex_repo_mutation rehearsal is proven with completed Atlas workgraph, safe node gates, serialized PR/CI/merge evidence, rollback evidence, Sentinel evidence, Promoter evidence, Command readback, and forbidden-surface closure evidence. | Mutation broader than the governed complex rehearsal boundary without the fully unsupervised complex closure evidence. |
| `fully_unsupervised_complex_mutation` | Highest proven live mutation class. | The 26-node first non-planning rehearsal is proven with all nodes completed, every stop gate cleared, per-node PR/CI/merge evidence, branch cleanup evidence, Sentinel/Promoter/Command closure, no concurrent mutation, no forbidden surfaces, and RSI denial preserved. | Fully unsupervised RSI, claim publication, provider calls, credential use, release/deploy/publish/upload/tag authority, or any self-improving RSI claim. |
| Fully unsupervised RSI | Denied. | The stack may claim bounded, governed RSI evidence only when the RSI evidence map passes. | Fully unsupervised RSI remains denied until Covenant claim-publish policy, live mutation authority, rollback evidence, live self-change evidence, observer readback, Command/Forge retention, and all class gates pass. |

## Latest Merged Evidence

- AO Atlas PR #34 upgrades the `complex_repo_mutation` rehearsal fixture beyond
  a simple dry-run shape: it adds low-risk decomposition and rollback graph
  nodes, keeps Atlas classification-only, and proves Foundry import can be
  scoped to a single dependency-safe node.
- AO Foundry PR #117 makes the complex-refactor rehearsal emit and validate a
  Foundry import for exactly one Atlas `workgraph next` node while preserving
  `schedules_work=false`, `executes_work=false`, `approves_work=false`, and
  `mutates_repositories=false`.
- AO Foundry PR #118 hardens the Pulse event-loop policy so it may continue
  without operator Q&A only inside the current proven class with
  `safe_to_execute=true`. It stops on dirty repos, stale evidence, failed CI,
  broadened scope, Sentinel holds, Promoter denial, rollback failure, branch
  cleanup failure, or class-jump attempts.
- The 2026-06-30 complex_repo_mutation mission completed all 12 governed nodes
  and closed promotion with digest-bound run-link, node-gate, rollback,
  Sentinel, Promoter, Command, CI, merge, and forbidden-surface evidence.
- The 2026-07-01 fully_unsupervised_complex_mutation first non-planning mission
  completed all 26 serialized nodes and closed promotion with mission
  completion evidence, Foundry final rollup, Promoter final verdict, and Command
  class-decision readback. The promotion advances the highest proven live class
  to `fully_unsupervised_complex_mutation` and keeps RSI denied.

## Layer Responsibilities

- AO Atlas classifies and maps workgraphs; Atlas does not grant authority.
- AO Foundry composes class gates and Pulse/event-loop policy; Foundry does not
  turn `safe_to_request` into live execution authority or let the event loop
  jump classes without promotion evidence.
- AO Covenant issues exact-scope, expiring, digest-bound, class-bound,
  single-use tickets; a missing or mismatched ticket fails closed.
- AO Forge and AO2 enforce class-bounded execution packet constraints; they must
  not execute outside the class packet.
- AO Sentinel can hold a class on coverage, rollback, diff size, file class,
  stale evidence, or CI status.
- AO Promoter decides whether completed live rehearsal evidence is enough to
  promote to the next class.
- AO Command reads back current class, next class, blockers, required evidence,
  and denial reasons without scheduling or mutating.

## Public Claim Rule

Use this ladder when writing public claims:

- Dry-run readiness means the evidence chain can be inspected or requested; it
  does not mutate repositories.
- Approved live docs mutation means only docs-only classes have live evidence.
- Approved fully unsupervised complex mutation means
  `fully_unsupervised_complex_mutation` is the highest proven live mutation
  class for the governed 26-node first non-planning rehearsal boundary.
- An event-loop continuation policy is not mutation authority; it can only stay
  inside the proven class and must stop on the configured blockers.
- Fully unsupervised complex repository mutation is proven only for the governed
  26-node first non-planning rehearsal boundary.
- Fully unsupervised RSI remains denied.
