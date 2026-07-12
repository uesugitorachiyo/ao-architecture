# AO Stack External-Beta Preflight Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a truthful, reproducible external-beta documentation and preflight package from the completed Month 6 evidence.

**Architecture:** AO Architecture holds the tested-stack manifest, topology, component pages, diagrams, preflight artifacts, and conformance verifier. Each component README owns only local role, commands, maturity, and safety content while linking to canonical Architecture pages.

**Tech Stack:** JSON, Markdown, Python 3 standard library, repository-native Go/Rust/Python verification, GitHub Actions.

## Global Constraints

- No release, deploy, publish, upload, tag, provider call, or credential inspection.
- No dependency update or policy, authentication, configuration, or authority widening.
- No hidden instruction mutation or broad RSI claim; RSI remains denied.
- Preserve the AO Architecture Helix divergence and AO Promoter hardening branch.
- Use isolated branches and PR/CI/merge lifecycle; never mutate `main` directly.
- Capability labels are limited to `implemented`, `executable-tested`, `clean-room-rehearsed`, `fixture-only`, `planned`, and `unauthorized`.

---

### Task 1: Canonical Tested-Stack Manifest

**Files:**
- Create: `stack/external-beta-tested-stack.json`
- Create: `scripts/test_verify_external_beta_preflight.py`
- Create: `scripts/verify_external_beta_preflight.py`
- Modify: `scripts/verify_architecture.py`

- [ ] Write tests that reject a missing repository, unrecognized capability label, mutable evidence reference, promoted state, and launched-beta wording.
- [ ] Run the tests and confirm they fail because the verifier does not exist.
- [ ] Implement manifest validation and repository-head checks using only the Python standard library.
- [ ] Bind the Month 6 launch-readiness path and SHA-256 digest.
- [ ] Run the targeted tests and Architecture verification.

### Task 2: Canonical Product Documentation

**Files:**
- Modify: `README.md`
- Modify: `overview/README.md`
- Modify: `overview/PRODUCTION-READINESS.md`
- Modify: `stack/readiness-inventory.json`
- Create: `components/*.md`
- Modify: `scripts/generate_architecture_svgs.py`
- Modify: `images/*.svg`

- [ ] Replace landing-page campaign chronology with links to the historical evidence catalog.
- [ ] Publish current topology, component roles, maturity, capability labels, and denied authorities from the manifest.
- [ ] Generate current topology and authority diagrams from the same repository-role data.
- [ ] Run architecture, topology, readiness, image, and wording checks.

### Task 3: Component README Contract

**Files:**
- Modify in each component repository: `README.md`
- Create where absent: `scripts/verify_readme_contract.py` or repository-equivalent test fixture.

- [ ] Add canonical Architecture and component-page links to all thirteen READMEs.
- [ ] Add concise Role, Maturity, Install, Quickstart, Safety, and External Beta sections.
- [ ] Remove or relocate landing-page historical campaign prose without deleting evidence.
- [ ] Run each repository's native tests, link checks, public-safety scan, and diff check.
- [ ] Open, verify, merge, sync, and clean one repository PR at a time.

### Task 4: Cross-Repository Conformance And Preflight Package

**Files:**
- Create: `docs/external-beta/README.md`
- Create: `docs/external-beta/checklist.md`
- Create: `docs/external-beta/operator-runbook.md`
- Create: `docs/external-beta/feedback-intake.md`
- Create: `docs/external-beta/security-review-intake.md`
- Create: `docs/external-beta/installation-rehearsal.md`
- Create: `docs/external-beta/rollback-rehearsal.md`
- Create: `.github/workflows/documentation-conformance.yml`

- [ ] Make each rehearsal reproducible from clean pinned checkouts without live actions.
- [ ] Check every local Markdown and image link and every component README contract.
- [ ] Add CI that runs repository-local checks without requiring sibling checkouts.
- [ ] Run the full sibling-repository verifier locally against exact pinned heads.

### Task 5: No-Promotion Closure

**Files:**
- Create: `docs/external-beta/readbacks/sentinel.json`
- Create: `docs/external-beta/readbacks/promoter.json`
- Create: `docs/external-beta/readbacks/command.json`
- Create: `docs/external-beta/readbacks/final-rollup.json`

- [ ] Bind all readbacks to the tested-stack manifest digest.
- [ ] Require `no_promotion_requested`, Command agreement, no launched beta, and RSI denied.
- [ ] Run full Architecture and cross-repository verification.
- [ ] Open the Architecture PR, wait for CI, merge, sync the canonical worktree, and delete the feature branch.

