# Mutation Authority Ladder

This page is the architecture mirror for governed live repository mutation
authority across AO Atlas, AO Foundry, AO Covenant, AO Forge, AO2, AO Sentinel,
AO Promoter, and AO Command. It distinguishes dry-run readiness from approved
live mutation and from the still-denied fully unsupervised RSI claim.

The highest proven live mutation class is `test_only`. That means the stack can
point to governed live rehearsal evidence through the docs-only classes and one
bounded test-only class. It does not mean broad code mutation, multi-repo live
mutation, complex repository mutation, or fully unsupervised RSI is proven.

| Class or claim boundary | Current public state | What is allowed | What remains denied |
| --- | --- | --- | --- |
| `docs_only_single_file` | Proven live rehearsal class. | Exact-scope docs-only approval, rollback, Sentinel, Promoter, Command readback, CI, PR lifecycle, and merge evidence can support one bounded docs-only live mutation. | Broad docs authority, config/code changes, or unsupervised follow-on mutation. |
| `docs_only_multi_file` | Proven live rehearsal class. | A bounded docs-only multi-file PR can proceed only inside its max-file limit and class gates. | More than the class file limit, code edits, config edits, or automatic class promotion. |
| `docs_config_only` | Modeled mutation class, not a broader live authority claim. | Dry-run classification can identify docs/config-only scope when its gates exist. | Treating config-adjacent files as low-risk code or bypassing Covenant/Sentinel/Promoter. |
| `test_only` | Highest proven live mutation class. | One bounded test-only live rehearsal can be approved when rollback, CI, Sentinel, Promoter, Command readback, and exact class evidence pass. | Production code changes, broad test rewrites, or using test-only success as live code authority. |
| `low_risk_code` | Dry-run/request boundary only. | Foundry may report safe-to-request for a dry-run design when lower-class evidence, rollback, CI, Sentinel, Promoter, Command readback, and class ticket evidence pass. | `low_risk_code` remains `safe_to_execute=false`; no approved low-risk live code mutation is proven. |
| `multi_repo_low_risk` | Dry-run rehearsal boundary only. | Atlas, Foundry, and Command can model serialized repo-by-repo state with per-repo rollback and no concurrent unsafe execution. | `multi_repo_low_risk` remains dry-run-only; no live multi-repo low-risk rehearsal is proven. |
| `complex_repo_mutation` | Atlas dry-run rehearsal only. | Atlas can classify and model a fourteen-node complex workgraph with blocked nodes, context repack, repair, low-risk decomposition, rollback graph, dependency gates, Sentinel/Promoter/Command evidence, and promotion gates. Foundry can select only the Atlas `workgraph next` safe node for import. | `complex_repo_mutation` remains dry-run-only until every lower class has required live evidence and all gates pass. |
| Fully unsupervised complex repository mutation | Denied. | No public claim may describe this as proven. | Fully unsupervised complex repository mutation remains denied. |
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
- Approved test-only mutation means `test_only` is the highest proven live
  class.
- Approved low-risk code mutation is not proven.
- Multi-repo rehearsal is not live.
- Complex mutation is not live.
- An event-loop continuation policy is not mutation authority; it can only stay
  inside the proven class and must stop on the configured blockers.
- Fully unsupervised complex repository mutation remains denied.
- Fully unsupervised RSI remains denied.
