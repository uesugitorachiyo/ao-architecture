# Uniform AO Public Stack Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish AO2 `v0.5.12` and AO Mission `v0.1.6`, retain compatible unchanged component releases, and qualify one refreshed seven-component public stack plus 14-repository development baseline on macOS and Windows.

**Architecture:** AO2 owns the Windows worker archive contract, Mission owns its additive read-only lifecycle release, Control Plane performs a read-only exact-pair compatibility decision, and Architecture becomes current only after fresh public downloads are independently rehashed. The campaign advances through S01-S07 checkpoints; every slice ends with focused tests, full applicable gates, a commit or immutable public readback, and an explicit stop on ambiguity.

**Tech Stack:** Rust/Cargo, Python 3.11 standard library and pytest/unittest, Go 1.26, Windows batch and PowerShell, Bash, GitHub Actions, GitHub CLI, JSON, SHA-256.

**Spec:** `docs/superpowers/specs/2026-08-23-uniform-public-stack-release-design.md`

---

## Global Constraints

- Execute inline with `superpowers:executing-plans`; do not dispatch subagents.
- Work only from isolated `codex/` branches and preserve all pre-existing uncommitted/generated state.
- Never delete, replace, retarget, or edit an existing public tag, release, or asset.
- Public release authority is limited to AO2 `v0.5.12`, AO Mission `v0.1.6`, and the conditional Control Plane `v0.1.20` metadata-only path defined below.
- Keep AO Command `v0.1.3`, AO Atlas `v0.2.1`, AO Forge `v0.1.5`, and AO Covenant `v0.1.1` unchanged.
- Do not call providers, use provider credentials, deploy, promote, activate compatibility, launch beta, run RSI, or enter AO Office Pool.
- Generated `.ao-mission/`, `.ao2/`, `.tmp/`, `tmp/`, `target/`, `scripts/__pycache__/`, downloaded artifacts, and campaign ledgers remain uncommitted.
- A failed or ambiguous slice stops before the next slice. Escalate only that bounded slice for diagnosis; do not widen scope.

## Planned File Map

### AO2

- Modify `crates/ao2-cli/src/release_package.rs`: add the Windows-only worker and launcher to the deterministic archive, checksums, manifest, and verification report.
- Modify `crates/ao2-cli/tests/release_packaging.rs`: prove target-specific archive inventory and checksum coverage.
- Modify `scripts/release-archive-hosted-smoke.ps1`: execute the packaged launcher from a path containing spaces and retain credential-free evidence.
- Modify `tests/test_windows_outbound_worker.py`: cover packaged help, offline lease validation, interpreter failure, and argument forwarding.
- Modify `Cargo.toml`, `Cargo.lock`, and `package.json`: bump the exact release version to `0.5.12`.
- Modify `docs/release/release-train.json` and `tests/test_public_stabilization.py`: move the release train to the new patch pair without changing Control Plane.
- Create `docs/release/v0.5.12-stable.md`: publish the bounded Windows packaging notes and authority boundaries.
- Modify `README.md`, `docs/INSTALL.md`, `docs/VERIFICATION.md`, `docs/windows-outbound-worker.md`, and `AGENTS.md`: document the archive-root launcher and Python 3.11 prerequisite.

### AO Mission

- Create `docs/release/V0.1.6-RELEASE-NOTES.md`: describe candidate import and S01-S07 checkpoints as additive read-only behavior.
- Modify `internal/mission/release_rehearsal_workflow_test.go`: prove the v0.1.6 notes and release command evidence include the new surfaces without authority flags.
- Modify `README.md` only if the current command table does not already expose both features.

### AO2 Control Plane

- First use `docs/release/release-train.json`, `scripts/public_release_pair_verify.py`, and their tests read-only with explicit `v0.5.12` / `v0.1.19` inputs.
- Modify the release-train manifest, exact-pair fixtures/tests, release notes, and package version only if the sole failing condition is an exact version-pair metadata rejection. Any runtime/protocol/schema/storage/authentication failure requires a new design instead.

### AO Architecture

- Modify `scripts/test_verify_current_release_manifest.py`, `scripts/verify_current_release_manifest.py`, `stack/current-release-manifest.json`, and `docs/current-release.md`: bind fresh public release records.
- Modify `scripts/test_run_public_stack_canary.py` and `scripts/run_public_stack_canary.py`: pin the new AO2 and Mission assets and exercise the Windows launcher.
- Modify `docs/stack-assembly.md` and `docs/operator-workflow.md`: present one canonical mixed-version install matrix.
- Regenerate `stack/development-baseline-manifest.json`; update the exact baseline identity in `.github/workflows/development-baseline-qualification.yml`, `docs/development-baseline.md`, and `docs/development-baseline-qualification.md`.
- Modify any exact-version Architecture regression discovered by `rg` only when it describes current public truth; historical evidence remains unchanged.

## S01: Freeze Clean Inputs and Campaign Ledger

**Files:**
- Read: all changed repositories' `AGENTS.md`, release workflows, and current release metadata.
- Generated outside source: `$env:TEMP\ao-uniform-public-stack-release-20260823`.

- [ ] **Step 1: Verify synchronized clean main branches without changing generated state**

Run in each of `ao2`, `ao-mission`, `ao2-control-plane`, and `ao-architecture`:

```powershell
git fetch origin main --tags
git status --short
git rev-parse main
git rev-parse origin/main
git merge-base --is-ancestor main origin/main
git merge-base --is-ancestor origin/main main
```

Expected: the two SHAs match; only previously observed generated paths may be untracked. Any source edit or divergence stops S01.

- [ ] **Step 2: Create isolated implementation worktrees**

```powershell
$worktreeRoot = Join-Path $env:USERPROFILE '.config\superpowers\worktrees'
$factoryRoot = (Resolve-Path '..').Path
git -C (Join-Path $factoryRoot 'ao2') worktree add (Join-Path $worktreeRoot 'ao2\uniform-public-stack-release') -b codex/uniform-public-stack-release origin/main
git -C (Join-Path $factoryRoot 'ao-mission') worktree add (Join-Path $worktreeRoot 'ao-mission\uniform-public-stack-release') -b codex/uniform-public-stack-release origin/main
```

Expected: both worktrees are created on isolated branches. Reuse the existing Architecture `uniform-public-stack-release` worktree. Do not create a Control Plane worktree unless S05 proves it is required.

- [ ] **Step 3: Record exact immutable starting facts**

```powershell
$campaignRoot = Join-Path $env:TEMP 'ao-uniform-public-stack-release-20260823'
New-Item -ItemType Directory -Force -Path $campaignRoot | Out-Null
gh api repos/uesugitorachiyo/ao2/commits/main | Set-Content -Encoding utf8 (Join-Path $campaignRoot 'ao2-main.json')
gh api repos/uesugitorachiyo/ao-mission/commits/main | Set-Content -Encoding utf8 (Join-Path $campaignRoot 'ao-mission-main.json')
gh api repos/uesugitorachiyo/ao2-control-plane/releases/tags/v0.1.19 | Set-Content -Encoding utf8 (Join-Path $campaignRoot 'control-plane-v0.1.19.json')
gh release view v0.5.11 --repo uesugitorachiyo/ao2 --json tagName,targetCommitish,isDraft,isPrerelease,assets,url | Set-Content -Encoding utf8 (Join-Path $campaignRoot 'ao2-v0.5.11.json')
gh release view v0.1.5 --repo uesugitorachiyo/ao-mission --json tagName,targetCommitish,isDraft,isPrerelease,assets,url | Set-Content -Encoding utf8 (Join-Path $campaignRoot 'mission-v0.1.5.json')
```

Expected: every command exits zero and the ledger contains only public metadata. Record S01 complete before editing source.

## S02: Package the AO2 Windows Outbound Worker

**Files:**
- Modify: `crates/ao2-cli/tests/release_packaging.rs`
- Modify: `tests/test_windows_outbound_worker.py`
- Modify: `crates/ao2-cli/src/release_package.rs`
- Modify: `scripts/release-archive-hosted-smoke.ps1`

- [ ] **Step 1: Write failing Rust archive-contract assertions**

Add to `cli_packages_explicit_binary_for_cross_target_distribution`:

```rust
assert!(entries.iter().any(|entry| entry == "ao2-windows-outbound-worker.py"));
assert!(entries.iter().any(|entry| entry == "ao2-windows-worker.cmd"));
assert!(manifest_json["files"].as_array().unwrap().iter().any(|value| value == "ao2-windows-outbound-worker.py"));
assert!(manifest_json["files"].as_array().unwrap().iter().any(|value| value == "ao2-windows-worker.cmd"));
let checksums = archive_text_entry(Path::new(json["archive"].as_str().unwrap()), "SHA256SUMS");
assert!(checksums.contains("ao2-windows-outbound-worker.py"));
assert!(checksums.contains("ao2-windows-worker.cmd"));
```

Add a Unix-target regression asserting both names are absent.

- [ ] **Step 2: Run the focused Rust test and verify RED**

Run:

```powershell
cargo test -p ao2-cli --test release_packaging cli_packages_explicit_binary_for_cross_target_distribution -- --exact
```

Expected: FAIL because the worker and launcher are not in the archive.

- [ ] **Step 3: Add the minimal Windows-only package implementation**

In `release_package.rs`, copy `scripts/ao2_windows_outbound_worker.py` to the archive root as `ao2-windows-outbound-worker.py`, write `ao2-windows-worker.cmd`, and append both paths before sorting `checksum_paths`. The launcher content is:

```bat
@echo off
setlocal
where py >nul 2>nul
if not errorlevel 1 (
  py -3.11 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
  if not errorlevel 1 (
    py -3.11 "%~dp0ao2-windows-outbound-worker.py" %*
    exit /b %errorlevel%
  )
)
where python >nul 2>nul
if not errorlevel 1 (
  python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
  if not errorlevel 1 (
    python "%~dp0ao2-windows-outbound-worker.py" %*
    exit /b %errorlevel%
  )
)
>&2 echo AO2 Windows outbound worker requires Python 3.11 or newer.
exit /b 1
```

Use a repository-file resolver with the same containment behavior as `release_legal_file`; do not read a worker path from an environment variable.

- [ ] **Step 4: Run the Rust contract and reproducibility tests**

```powershell
cargo test -p ao2-cli --test release_packaging cli_packages_explicit_binary_for_cross_target_distribution -- --exact
cargo test -p ao2-cli --test release_packaging cli_release_archives_are_byte_reproducible -- --exact
```

Expected: PASS; the archive remains byte-reproducible.

- [ ] **Step 5: Add failing Windows launcher tests**

Extend `tests/test_windows_outbound_worker.py` with Windows-only subprocess tests that copy the two packaged files into `tmp_path / "AO2 Worker Package"` and assert:

```python
result = subprocess.run([str(package / "ao2-windows-worker.cmd"), "--help"], capture_output=True, text=True, check=False)
assert result.returncode == 0
assert "usage:" in result.stdout.lower()
```

Add cases for the existing `--validate-physical-host-lease` offline path, a PATH containing no Python (exit 1 with the exact prerequisite message), and arguments containing spaces preserved as one value.

- [ ] **Step 6: Run the launcher tests and verify RED before hosted-smoke wiring**

```powershell
python -m pytest tests/test_windows_outbound_worker.py -q
```

Expected: the new launcher cases fail until the test fixture packages the new files; all pre-existing worker tests remain green.

- [ ] **Step 7: Exercise the real packaged entry point in hosted Windows smoke**

After extracting the archive, update `scripts/release-archive-hosted-smoke.ps1` to copy the extracted tree beneath `Join-Path $Root 'worker package with spaces'`, run `ao2-windows-worker.cmd --help`, run one synthetic offline lease validation, and record:

```powershell
windows_worker_launcher = 'passed'
windows_worker_python_requirement = '>=3.11'
provider_calls = 0
credential_use = 0
```

Expected: the smoke never starts a listener or contacts Control Plane.

- [ ] **Step 8: Run focused AO2 gates and commit S02**

```powershell
cargo fmt --all -- --check
cargo test -p ao2-cli --test release_packaging
python -m pytest tests/test_windows_outbound_worker.py tests/test_physical_windows_qualification.py -q
git diff --check
git add crates/ao2-cli/src/release_package.rs crates/ao2-cli/tests/release_packaging.rs scripts/release-archive-hosted-smoke.ps1 tests/test_windows_outbound_worker.py
git commit -m "feat: package Windows outbound worker"
```

Expected: all commands pass and the commit contains no generated files. Checkpoint S02.

## S03: Prepare, Merge, and Publish AO2 v0.5.12

**Files:**
- Modify: `Cargo.toml`, `Cargo.lock`, `package.json`
- Modify: `docs/release/release-train.json`, `tests/test_public_stabilization.py`
- Create: `docs/release/v0.5.12-stable.md`
- Modify: `README.md`, `docs/INSTALL.md`, `docs/VERIFICATION.md`, `docs/windows-outbound-worker.md`, `AGENTS.md`

- [ ] **Step 1: Write failing release-version and documentation assertions**

Add assertions that package metadata equals `0.5.12`, `next_patch.ao2` equals `{"tag": "v0.5.12", "version": "0.5.12"}`, Control Plane remains `v0.1.19`, the new release notes exist, and the docs name `ao2-windows-worker.cmd` plus Python 3.11.

- [ ] **Step 2: Run the focused release tests and verify RED**

```powershell
python -m pytest tests/test_public_stabilization.py -q
```

Expected: failures identify the old `0.5.11` package/train values and missing notes.

- [ ] **Step 3: Apply the exact patch version and release metadata**

Set workspace/package versions to `0.5.12`, run `cargo check -p ao2-cli` to refresh `Cargo.lock`, set `package.json` to `0.5.12`, set release-train `stable` to AO2 `v0.5.11` / CP `v0.1.19`, and `next_patch` to AO2 `v0.5.12` / CP `v0.1.19` with confirmations:

```text
promote-stable-v0.5.12-v0.1.19
public-release-reviewed-v0.5.12-v0.1.19
```

Document that only the Windows archive adds the worker files and that Python 3.11 is an explicit operator prerequisite.

- [ ] **Step 4: Run full AO2 local gates**

```powershell
cargo fmt --all -- --check
cargo test --workspace --all-targets
cargo clippy --workspace --all-targets -- -D warnings
python -m pytest tests/test_windows_outbound_worker.py tests/test_physical_windows_qualification.py tests/test_public_stabilization.py -q
npm run test:archive-resources
git diff --check
```

Expected: all pass. If repository-owned `scripts/local-ci.sh` covers additional required gates, run it before commit.

- [ ] **Step 5: Commit, push, review, and merge the AO2 release PR**

```powershell
git add Cargo.toml Cargo.lock package.json docs/release/release-train.json docs/release/v0.5.12-stable.md README.md docs/INSTALL.md docs/VERIFICATION.md docs/windows-outbound-worker.md AGENTS.md tests/test_public_stabilization.py
git commit -m "release: prepare AO2 v0.5.12"
git push -u origin codex/uniform-public-stack-release
gh pr create --repo uesugitorachiyo/ao2 --base main --head codex/uniform-public-stack-release --title "Release AO2 v0.5.12 Windows worker package" --body "Packages the existing qualified outbound worker in the Windows archive, preserves AO2 authority boundaries, and prepares v0.5.12."
```

Expected: required CI and review pass before merge. Record the merge SHA as `$ao2SourceSha`.

- [ ] **Step 6: Run the AO2 release rehearsal and dry-run publication**

Build the approved asset manifest using the repository's existing rehearsal command, hash the exact bytes, and dispatch `public-release-build.yml` with `release_version=0.5.12`, `release_tag=v0.5.12`, the approved manifest SHA-256, the successful physical-Windows qualification run ID, and `dry_run=true`.

Expected: the workflow publishes no tag/release, produces three archives plus plan/checksums, and the Windows archive inventory/checksums contain both worker files.

- [ ] **Step 7: Publish only from the exact dry-run producer**

Dispatch the same workflow with the dry-run `promotion_plan_run_id`, exact plan SHA-256, `dry_run=false`, and:

```text
publish-v0.5.12-$ao2SourceSha-with-plan-$ao2PromotionPlanSha256
```

Expected: one immutable `v0.5.12` release is created from `$ao2SourceSha`; no pre-existing release is modified.

- [ ] **Step 8: Independently download, rehash, and smoke the public release**

```powershell
$ao2Public = Join-Path $campaignRoot 'ao2-v0.5.12-public'
New-Item -ItemType Directory -Force -Path $ao2Public | Out-Null
gh release download v0.5.12 --repo uesugitorachiyo/ao2 --dir $ao2Public
Get-ChildItem -File $ao2Public | Get-FileHash -Algorithm SHA256 | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $campaignRoot 'ao2-v0.5.12-rehash.json')
gh workflow run post-stable-release-verification.yml --repo uesugitorachiyo/ao2 -f ao2_release_tag=v0.5.12 -f ao2_release_version=0.5.12 -f ao2_cp_release_tag=v0.1.19
```

Expected: public checksums match fresh downloads and all three hosted smoke lanes pass. Checkpoint S03.

## S04: Prepare, Merge, and Publish AO Mission v0.1.6

**Files:**
- Create: `docs/release/V0.1.6-RELEASE-NOTES.md`
- Modify: `internal/mission/release_rehearsal_workflow_test.go`
- Modify: `README.md` only if current command documentation is incomplete.

- [ ] **Step 1: Add failing v0.1.6 release assertions**

Add a release-workflow test fixture for `0.1.6` asserting that notes mention `ao.next.live-run-record.v1`, ordered S01-S07 checkpoints, idempotence, and all-false execution/approval/repository-mutation/provider/publication/promotion flags.

- [ ] **Step 2: Run focused tests and verify RED**

```powershell
go test ./internal/mission -run 'Release|Checkpoint|AONext' -count=1
```

Expected: the new release-note fixture fails because `V0.1.6-RELEASE-NOTES.md` is absent.

- [ ] **Step 3: Write bounded release notes and complete command documentation**

The notes must list exact new commands already implemented on `main`, state read-only candidate projection and durable checkpoint semantics, and explicitly deny execution, approval, mutation, provider, publication, promotion, compatibility activation, beta, RSI, and AO Office Pool authority.

- [ ] **Step 4: Run Mission release and production gates**

```powershell
gofmt -d cmd internal
go test ./internal/mission -count=1
go test ./... -count=1
go vet ./...
go build ./cmd/ao-mission
python scripts/test_public_safety_scan.py
bash scripts/production-readiness.sh
python ..\ao-architecture\scripts\verify_agent_instruction_layout.py --workspace-root .. --repository ao-mission
git diff --check
```

Expected: formatting diff is empty and every gate passes.

- [ ] **Step 5: Commit, push, review, and merge the Mission release PR**

```powershell
git add docs/release/V0.1.6-RELEASE-NOTES.md internal/mission/release_rehearsal_workflow_test.go README.md
git commit -m "release: prepare AO Mission v0.1.6"
git push -u origin codex/uniform-public-stack-release
gh pr create --repo uesugitorachiyo/ao-mission --base main --head codex/uniform-public-stack-release --title "Release AO Mission v0.1.6" --body "Publishes the additive AO Next candidate import and evidence-bound S01-S07 checkpoint surfaces without widening Mission authority."
```

Expected: required CI and review pass before merge. Record the exact merge SHA as `$missionSourceSha`.

- [ ] **Step 6: Produce the approved manifest and rehearsal candidates**

Construct the exact three-target manifest required by `release-rehearsal.yml`, using `$missionSourceSha`, version `0.1.6`, tag `v0.1.6`, and the SHA-256 of `docs/sdd/AO-MISSION-V0.1.md`; encode and hash the exact JSON bytes. Dispatch rehearsal with `dry_run=true` and verify its candidate inventory, version output, help, functional smoke, SBOM, provenance, checksums, and sealed plan.

- [ ] **Step 7: Run the finalizer dry-run and live publication**

Dispatch `release-finalize.yml` first with `dry_run=true`. After it passes, dispatch again with `dry_run=false`, `repair_empty_release_notes=false`, and:

```text
publish-imported-ao-mission-$missionProducerRunId-0.1.6-v0.1.6-$missionSourceSha-$missionManifestDigest
```

Expected: one immutable `v0.1.6` release with exactly three platform archives.

- [ ] **Step 8: Independently download and verify Mission public assets**

```powershell
$missionPublic = Join-Path $campaignRoot 'ao-mission-v0.1.6-public'
New-Item -ItemType Directory -Force -Path $missionPublic | Out-Null
gh release download v0.1.6 --repo uesugitorachiyo/ao-mission --dir $missionPublic
Get-ChildItem -File $missionPublic | Get-FileHash -Algorithm SHA256 | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $campaignRoot 'ao-mission-v0.1.6-rehash.json')
```

Expected: archive names, sizes, SHA-256 values, version output, and source SHA match rehearsal evidence. Checkpoint S04.

## S05: Decide AO2 v0.5.12 / Control Plane v0.1.19 Compatibility

**Files:**
- Read first: `scripts/public_release_pair_verify.py`, `tests/test_public_release_pair_verify.py`, `docs/release/release-train.json` in Control Plane.
- Conditional modify only for metadata mismatch: release-train manifest, compatibility fixture/test, package version files, release notes, and release workflows owned by Control Plane.

- [ ] **Step 1: Run the public pair verifier with explicit tags**

```powershell
python scripts/public_release_pair_verify.py --ao2-tag v0.5.12 --control-plane-tag v0.1.19 --strict --output-root (Join-Path $campaignRoot 'pair-v0.5.12-v0.1.19')
```

Expected: PASS means retain Control Plane `v0.1.19`. The verifier is read-only and downloads public checksums only.

- [ ] **Step 2: Run the native compatibility consumer tests**

```powershell
cargo test -p ao2-cp-server --test compatibility_vectors
python -m pytest tests/test_public_release_pair_verify.py tests/test_release_qualification.py -q
git diff --check
```

Expected: PASS with no Control Plane source mutation. Record `control_plane_update_required=false` and skip Steps 3-5.

- [ ] **Step 3: Apply the conditional metadata-only path if and only if exact pair metadata fails**

Create `codex/uniform-public-stack-release` from `origin/main`, change only version-pair declarations/fixtures and release metadata to AO2 `v0.5.12` / Control Plane `v0.1.20`, and add a regression proving no protocol/schema/storage/authentication/runtime change. Any other failure exits S05 blocked for a new design.

- [ ] **Step 4: Run full Control Plane gates and merge the conditional PR**

```powershell
cargo fmt --all -- --check
cargo test --workspace --all-targets
cargo clippy --workspace --all-targets -- -D warnings
python -m pytest tests/test_public_release_pair_verify.py tests/test_release_qualification.py tests/test_release_promotion_workflow.py -q
git diff --check
```

Expected: all pass and the diff contains metadata/fixtures/tests only.

- [ ] **Step 5: Publish and verify conditional v0.1.20 through source-owned workflows**

Use `release-promotion.yml` dry-run, bind the exact plan digest, then live-publish with the workflow-emitted confirmation. Run `post-release-verification.yml -f release_tag=v0.1.20` and repeat Steps 1-2 against `v0.1.20`.

Expected: one immutable public release and a passing exact pair decision. Checkpoint S05 records either retained `v0.1.19` or published `v0.1.20`, never an assumption.

## S06: Refresh and Qualify the Public Stack in AO Architecture

**Files:**
- Modify: `scripts/test_verify_current_release_manifest.py`, `scripts/verify_current_release_manifest.py`
- Modify: `scripts/test_run_public_stack_canary.py`, `scripts/run_public_stack_canary.py`
- Modify: `stack/current-release-manifest.json`, `docs/current-release.md`, `docs/stack-assembly.md`, `docs/operator-workflow.md`

- [ ] **Step 1: Write failing manifest and canary pin tests**

Update expected pins to AO2 `v0.5.12`, Mission `v0.1.6`, and the exact retained/published Control Plane version. Add an assertion that only the Windows AO2 asset exposes `ao2-windows-worker.cmd`, that the canary runs it from a path containing spaces, and that the report records Python `>=3.11` with zero provider/credential counts.

- [ ] **Step 2: Run focused Architecture tests and verify RED**

```powershell
python -m unittest scripts.test_verify_current_release_manifest scripts.test_run_public_stack_canary -v
```

Expected: failures identify old AO2/Mission pins and missing launcher smoke.

- [ ] **Step 3: Update the frozen public manifest from fresh readbacks**

Enter exact tag targets, workflow run URLs, asset counts, names, sizes, and independently computed SHA-256 values from S03-S05. Preserve all unchanged component records byte-for-byte except fields whose schema requires a regenerated manifest timestamp/source description. Set every authority boundary false.

- [ ] **Step 4: Update canary assets and Windows worker smoke**

Replace AO2 and Mission `_COMPONENTS` entries with exact public downloads. Extend Windows installation to locate `ao2-windows-worker.cmd` in the verified AO2 archive, run `--help` and one synthetic offline lease validation, and include the results in report validation. Do not expose or execute the worker on Linux/macOS.

- [ ] **Step 5: Update the canonical user documentation**

Document one seven-row matrix with the selected component versions, direct release links, the Windows worker command, Python 3.11 prerequisite, and Covenant Rosetta boundary. Remove statements that call AO2 `v0.5.11` or Mission `v0.1.5` current; do not edit historical evidence.

- [ ] **Step 6: Run focused and full Architecture gates**

```powershell
python -m unittest scripts.test_verify_current_release_manifest scripts.test_run_public_stack_canary -v
python scripts/verify_current_release_manifest.py
python scripts/verify_architecture.py
python scripts/verify_agent_instruction_layout.py --workspace-root .. --repository ao-architecture
git diff --check
```

Expected: all pass.

- [ ] **Step 7: Commit, push, review, and merge the public-stack refresh**

```powershell
git add scripts/test_verify_current_release_manifest.py scripts/verify_current_release_manifest.py scripts/test_run_public_stack_canary.py scripts/run_public_stack_canary.py stack/current-release-manifest.json docs/current-release.md docs/stack-assembly.md docs/operator-workflow.md
git commit -m "docs: refresh uniform public AO stack"
git push -u origin codex/uniform-public-stack-release
gh pr create --repo uesugitorachiyo/ao-architecture --base main --head codex/uniform-public-stack-release --title "Refresh uniform public AO stack" --body "Pins AO2 v0.5.12 and Mission v0.1.6, retains qualified unchanged releases, and adds the packaged Windows worker to the public canary."
```

Expected: required CI and review pass before merge.

- [ ] **Step 8: Dispatch and independently verify the three-platform public canary**

```powershell
gh workflow run public-stack-canary.yml --repo uesugitorachiyo/ao-architecture --ref main
```

Wait for completion, download all three artifacts into a new empty campaign directory, recompute SHA-256, parse JSON, and verify seven exact component identities, Windows launcher evidence, identical terminal-index digest, cleanup, and all-zero authority counters.

Expected: Linux x86_64, macOS arm64, and Windows x86_64 all pass from public assets only. Checkpoint S06.

## S07: Regenerate and Qualify the 14-Repository Development Baseline

**Files:**
- Modify: `stack/development-baseline-manifest.json`
- Modify: `.github/workflows/development-baseline-qualification.yml`
- Modify: `docs/development-baseline.md`, `docs/development-baseline-qualification.md`
- Modify exact-current regression files discovered by tests; do not modify historical evidence.

- [ ] **Step 1: Freeze all 14 reviewed current source heads**

Read each repository's `origin/main` SHA after all campaign PRs are merged. Require clean synchronized main, green CI, exact upstream URL, and existing repository-owned gate declarations. Populate a new canonical manifest using the current release manifest as `release_input`.

- [ ] **Step 2: Verify the regenerated manifest and capture its identity**

```powershell
$architectureSourceSha = git rev-parse HEAD
python scripts/verify_development_baseline.py --manifest stack/development-baseline-manifest.json --schema docs/contracts/development-baseline-manifest-v1.schema.json --release-manifest stack/current-release-manifest.json --controller-commit $architectureSourceSha
```

Expected: exit 0 and `baseline_identity=sha256:` followed by 64 lowercase hex characters.

- [ ] **Step 3: Bind the exact new identity in qualification surfaces**

Replace the previous current identity only in `.github/workflows/development-baseline-qualification.yml`, `docs/development-baseline.md`, and `docs/development-baseline-qualification.md`. Preserve the old baseline declaration as historical text where explicitly labeled historical.

- [ ] **Step 4: Run baseline and Architecture regression gates**

```powershell
python -m unittest scripts.test_verify_development_baseline scripts.test_bootstrap_development_baseline scripts.test_run_development_baseline_workflow scripts.test_run_development_baseline_gates scripts.test_compare_development_baseline_results scripts.test_verify_development_baseline_evidence -v
python scripts/verify_architecture.py
python scripts/verify_agent_instruction_layout.py --workspace-root .. --repository ao-architecture
git diff --check
```

Expected: all pass.

- [ ] **Step 5: Commit and merge the baseline refresh**

```powershell
git add stack/development-baseline-manifest.json .github/workflows/development-baseline-qualification.yml docs/development-baseline.md docs/development-baseline-qualification.md
git commit -m "docs: freeze refreshed development baseline"
git push
```

Update the existing Architecture PR if still open; otherwise open one bounded follow-up PR. Merge only with green required CI and review.

- [ ] **Step 6: Dispatch full native qualification**

```powershell
gh workflow run development-baseline-qualification.yml --repo uesugitorachiyo/ao-architecture --ref main
```

Expected: `macos-26` and `windows-2025` materialize the exact manifest in new empty roots, run every declared gate and workflow stage, remove run-owned roots, produce semantic parity with zero differences, and close the complete artifact inventory.

- [ ] **Step 7: Independently download, rehash, and close evidence**

Download host, gate, workflow, cleanup, rehash, parity, and evidence-closure artifacts into a new empty directory. Run `scripts/verify_development_baseline_evidence.py` with the merged Architecture SHA and exact new baseline identity. Verify no missing/extra artifact, digest mismatch, undeclared skip, residue, provider call, credential use, or authority widening.

- [ ] **Step 8: Reconcile repositories and checkpoint terminal completion**

Confirm all changed repositories have green merged-main CI, public tags point to exact reviewed sources, Architecture current truth matches fresh public downloads, task worktrees contain no uncommitted source changes, and temporary campaign roots are either retained intentionally as private evidence or safely removed. Delete no historical evidence and do not claim deployment, promotion, beta, RSI, or AO Office Pool completion.

Expected: S07 and the campaign are complete only when every required check above is evidenced.
