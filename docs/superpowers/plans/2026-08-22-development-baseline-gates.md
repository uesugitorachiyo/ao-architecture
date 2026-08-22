# Development Baseline Repository Gates Implementation Plan

**Goal:** Freeze, execute, and independently qualify every unconditional
repository-owned development gate for the exact fourteen-repository baseline.

**Architecture:** Extend the closed baseline manifest with literal gate argv,
then use one standard-library Python controller for sequential native execution,
bounded log hashing, tracked-state drift detection, and read-only result
verification. Extend the existing dispatch-only native workflow and rehash job.

---

### Task 1: Closed Gate Inventory

- Add failing manifest-verifier tests for missing/duplicate IDs, command
  strings, unsafe shell policy, invalid timeout/environment, conditional skip,
  and authority-bearing argv.
- Add `development_gates` to each repository and to the closed schema using
  exact-head quality manifests or unconditional `AGENTS.md` full gates.
- Run the S01 verifier tests, manifest verifier, Architecture verifier, and
  `git diff --check`; commit the regenerated baseline identity.

### Task 2: Sequential Gate Runner

- Add failing offline tests for unknown repository/gate, shell mismatch,
  timeout, nonzero exit, undeclared skip, tracked/index drift, output bounds,
  partial preservation, deterministic ordering, and Windows shim/Git Bash
  resolution.
- Implement explicit argv execution, exact workspace revalidation, sequential
  fail-closed control, exclusive bounded logs, deterministic results, and
  read-only retained-result verification.
- Run focused tests and Architecture gates; commit.

### Task 3: Hosted Integration And Evidence

- Add failing workflow contract tests requiring gate execution after
  materialization, host artifact upload before cleanup, gate-aware rehash, and
  no authority-bearing triggers or inputs.
- Extend the two-host workflow and independent rehash controller.
- Run all focused/local Architecture gates and commit.

### Task 4: Reviewed Native Proof And Mission Checkpoint

- Push through normal pull-request review and require all PR checks green.
- Dispatch only the merged-main source commit. Require every declared gate to
  pass on both hosts, exact regenerated baseline identity, zero tracked drift,
  root-absent cleanup, and zero independent rehash mismatch.
- Import public-safe S03 evidence linked to S02, create the evidence-bound
  checkpoint, replay it idempotently, and confirm unchanged Mission lifecycle
  plus all-false authority before S04.
