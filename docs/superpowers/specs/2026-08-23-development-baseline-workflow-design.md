# Development Baseline Credential-Free Workflow Design

## Purpose

S04 proves that the frozen development baseline can exercise the complete AO
contract path from Mission intake through a Promoter no-promotion result on a
clean macOS or Windows source workspace. The proof is deterministic,
credential-free, and non-authoritative. Architecture records and validates the
journey; each component remains the producer of its own output.

## Contract

`stack/fixtures/development-baseline-v1/fixture-manifest.json` is the only
accepted fixture. It binds the S03 baseline identity, correlation ID, exact
repository source commits, ordered stage inventory, component-owned command
argv, producer inputs, output locators, expected schemas and terminal states,
and the closed authority counters.

The ordered stages are exactly:

1. Mission intake
2. Blueprint authorization
3. Atlas workgraph
4. Foundry coordination
5. Forge coordination
6. Covenant decision
7. AO2 bounded scripted fixture
8. Control Plane observation
9. Command readback
10. Mission readback
11. Arena assurance
12. Crucible assurance
13. Sentinel assurance
14. Promoter no-promotion

Every stage names one repository from the frozen baseline and one argv array.
Arguments are executed directly with `shell=False`. The runner substitutes only
declared run-root and producer-artifact placeholders; it never interprets shell
syntax, adds approval flags, or rewrites component output.

When an owning CLI requires outputs beneath its current `tmp` directory, the
manifest may declare a shell-free source build into the run-owned stage root and
execute that binary with the stage root as its working directory. This preserves
the component's output-containment contract without writing generated state into
the source checkout.

## Validation

Before execution the runner fails closed on:

- unknown or duplicate properties, stages, repositories, or outputs;
- missing stages or a changed stage order;
- a repository commit or upstream that differs from the baseline manifest;
- an unsafe path, symlink/reparse traversal, non-regular producer artifact, or
  an output outside the new run root;
- a missing producer edge, future/self dependency, digest mismatch, or
  correlation mismatch;
- an argv that is empty, contains shell metacharacter dispatch, uses a shell,
  requests a provider, publication, deployment, promotion, release, credential,
  compatibility activation, external beta, or RSI action;
- an environment containing AO/provider credential variables; or
- authority fields that are missing, unknown, non-boolean, or true.

Each completed stage must emit one bounded JSON object. The runner independently
hashes it, validates the declared schema and terminal result, confirms the exact
correlation and source identity, and records the producer edge. A nonzero exit,
timeout, malformed JSON, nonterminal state, or unexpected side-effect counter
stops the journey while preserving the deterministic partial result.

## Execution And Cleanup

The output path must not exist. The runner creates one run-owned directory and
sanitizes the child environment to platform/toolchain variables plus explicit
run-local state roots. Native Windows compilation retains only the non-secret
MSVC and Windows SDK discovery variables required by Cargo; provider tokens,
API keys, and credential variables remain absent. It captures bounded stdout/stderr hashes, not unbounded
transcripts. Only processes started by a component command may be stopped, and
only the run-owned temporary directory may be removed. Source checkouts are
read-only inputs and are checked for source-head drift before and after every
stage.

The retained result contains stage identities, artifact digests, semantic
terminal states, zero authority counters, and cleanup disposition. S04 records
the two raw native results separately. It does not claim semantic parity; S05
owns normalization and comparison.

The hosted workflow defaults to the full materialization, repository-gate, and
workflow sequence. A bounded `workflow-only` dispatch is permitted only for an
S04 repair after S03 is durably checkpointed. It still uses new clean native
roots, exact materialization, the complete fixture, artifact upload, and exact
cleanup; it skips only the already-accepted S03 gate rerun and its gate rehash.

## Review Decision

The operator's standing campaign approval accepts this bounded design for S04.
It authorizes implementation and qualification only; all release, publication,
deployment, provider, credential, promotion, compatibility, external-beta, and
RSI authority remains denied.
