# Development Baseline Credential-Free Workflow Implementation Plan

**Goal:** Execute and validate one exact, component-owned, credential-free AO
fixture journey on the frozen S03 baseline without granting side-effect
authority.

**Design:** `docs/superpowers/specs/2026-08-23-development-baseline-workflow-design.md`

## Task 1: Freeze the fixture contract

- [ ] Add `stack/fixtures/development-baseline-v1/fixture-manifest.json` with the
  exact 14-stage order, repository/source bindings, producer edges, argv arrays,
  expected schemas, terminal results, and denied authorities.
- [ ] Add a README documenting native invocation, private output handling, and
  the no-parity/no-authority boundary.
- [ ] Review the manifest against `stack/development-baseline-manifest.json`.

## Task 2: Add failing contract tests

- [ ] Add `scripts/test_run_development_baseline_workflow.py`.
- [ ] Cover missing producer artifacts, wrong repository/source identity,
  correlation drift, digest mismatch, unknown/duplicate/nonterminal stages,
  unsafe paths, over-authority, provider/publication/promotion/RSI requests, and
  incomplete cleanup ownership.
- [ ] Cover deterministic ordering, bounded logs, native argv execution, and a
  passing local component-fixture chain.

## Task 3: Implement the runner

- [ ] Add `scripts/run_development_baseline_workflow.py` using only the Python
  standard library.
- [ ] Validate completely before starting a command.
- [ ] Execute shell-free argv in the owning repository and preserve partial
  results on failure.
- [ ] Validate and hash every producer artifact, verify repository heads before
  and after execution, and clean only the run-owned temporary root.

## Task 4: Integrate and verify

- [ ] Add the workflow invocation and raw-result upload to
  `.github/workflows/development-baseline-bootstrap.yml`.
- [ ] Run the focused tests, local fixture, baseline verifier, Architecture
  verifier, and `git diff --check`.
- [ ] Merge through normal review, run on clean macOS and Windows roots, retain
  both raw terminal artifacts, independently rehash them, and checkpoint S04 in
  AO Mission.

## Review Decision

The operator's standing campaign approval accepts this plan. The approval does
not authorize provider calls, credentials, release, publication, deployment,
promotion, compatibility activation, external beta, RSI, or AO Office Pool.
