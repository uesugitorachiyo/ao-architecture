# Public Binary AO Stack Canary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a fail-closed, public-only canary for the supported seven-component AO Stack on Linux x86_64, macOS aarch64, and Windows x86_64.

**Architecture:** One standard-library Python program owns the frozen public artifact manifest, validates and installs one asset per component, runs credential-free identity and reconciliation checks, and writes a deterministic JSON report. One offline `unittest` module drives the implementation. One GitHub Actions workflow runs the same program on all three native hosted runners and uploads the reports.

**Tech Stack:** Python 3 standard library, `unittest`, GitHub Actions.

## Global Constraints

- Pin AO2 `v0.5.11`, AO2 Control Plane `v0.1.19`, AO Mission `v0.1.4`, AO Atlas `v0.2.0`, AO Command `v0.1.2`, AO Forge `v0.1.4`, and AO Covenant `v0.1.1`.
- Use public GitHub release assets and public source documentation only.
- Add no dependency, credential, provider call, repository mutation, publication, deployment, or authority advance.
- Verify SHA-256 before extraction and reject unsafe paths, links, duplicate identities, missing files, and wrong versions.
- Keep generated reports and temporary installations out of source control.
- Preserve AO2 native verification run `31622142672` as the full AO2 install/doctor/fixture/uninstall proof.

---

### Task 1: Frozen manifest and safe installation

**Files:**
- Create: `scripts/run_public_stack_canary.py`
- Create: `scripts/test_run_public_stack_canary.py`

**Interfaces:**
- Produces: `ASSETS: dict[str, dict[str, Asset]]`, `select_assets(target: str) -> tuple[Asset, ...]`, `verify_digest(path: Path, expected: str) -> None`, and `install_asset(asset: Asset, archive: Path, destination: Path) -> tuple[Path, ...]`.

- [ ] **Step 1: Write failing tests for manifest coverage and target selection**

```python
def test_each_target_selects_all_seven_components(self):
    for target in ("linux-x86_64", "macos-aarch64", "windows-x86_64"):
        assets = canary.select_assets(target)
        self.assertEqual(7, len(assets))
        self.assertEqual(7, len({asset.component for asset in assets}))

def test_manifest_uses_sha256_and_https_release_urls(self):
    for target in canary.TARGETS:
        for asset in canary.select_assets(target):
            self.assertRegex(asset.sha256, r"^[0-9a-f]{64}$")
            self.assertTrue(asset.url.startswith("https://github.com/uesugitorachiyo/"))
            self.assertIn("/releases/download/", asset.url)
```

- [ ] **Step 2: Run the tests and verify RED**

Run: `python3 -m unittest scripts.test_run_public_stack_canary -v`

Expected: import or attribute failure because the canary module and manifest do not exist.

- [ ] **Step 3: Add the seven live asset URLs and GitHub-reported SHA-256 values per target**

Use a frozen `Asset` dataclass. Include only the native binary asset for each component and target. Covenant is a raw executable; the other assets are tar.gz or ZIP according to their release inventory.

- [ ] **Step 4: Write failing tests for digest rejection and tar/ZIP/raw extraction**

```python
def test_verify_digest_rejects_drift(self):
    path = self.write_bytes("asset", b"changed")
    with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
        canary.verify_digest(path, "0" * 64)

def test_install_rejects_parent_traversal(self):
    archive = self.make_tar({"../escape": b"bad"})
    with self.assertRaisesRegex(ValueError, "unsafe archive path"):
        canary.install_asset(self.tar_asset, archive, self.install_root)

def test_install_rejects_links(self):
    archive = self.make_symlink_tar("binary", "outside")
    with self.assertRaisesRegex(ValueError, "link"):
        canary.install_asset(self.tar_asset, archive, self.install_root)
```

- [ ] **Step 5: Run the focused tests and verify RED**

Run: `python3 -m unittest scripts.test_run_public_stack_canary.SafeInstallTests -v`

Expected: failures because digest and extraction functions are absent.

- [ ] **Step 6: Implement minimal safe installation**

Use `hashlib.file_digest`, `tarfile`, `zipfile`, `pathlib.PurePosixPath`, and `shutil.copyfileobj`. Reject absolute paths, `..`, empty names, links, non-regular tar members, duplicate paths, and output escaping the destination. Copy raw Covenant binaries directly and add executable bits on POSIX.

- [ ] **Step 7: Run all offline tests**

Run: `python3 -m unittest scripts.test_run_public_stack_canary -v`

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add scripts/run_public_stack_canary.py scripts/test_run_public_stack_canary.py
git commit -m "Add safe public stack asset installer"
```

### Task 2: Identity, smoke, and terminal reconciliation

**Files:**
- Modify: `scripts/run_public_stack_canary.py`
- Modify: `scripts/test_run_public_stack_canary.py`

**Interfaces:**
- Produces: `run_command(argv: list[str], *, env: dict[str, str], expected_exit: set[int]) -> CommandResult`, `verify_identity(component: str, result: CommandResult) -> None`, and `run_canary(target: str, output: Path) -> dict[str, object]`.

- [ ] **Step 1: Write failing tests for identity parsing and command recording**

```python
def test_identity_rejects_wrong_version(self):
    result = canary.CommandResult(["ao2", "--version"], 0, "ao2 0.5.10\n", "", 1)
    with self.assertRaisesRegex(ValueError, "AO2 identity mismatch"):
        canary.verify_identity("ao2", result)

def test_command_record_keeps_exit_and_output(self):
    result = canary.run_command([sys.executable, "-c", "print('ok')"], env={}, expected_exit={0})
    self.assertEqual(0, result.exit_code)
    self.assertEqual("ok\n", result.stdout)
```

- [ ] **Step 2: Run focused tests and verify RED**

Run: `python3 -m unittest scripts.test_run_public_stack_canary.CommandTests -v`

Expected: failures because command and identity interfaces do not exist.

- [ ] **Step 3: Implement exact component identity checks**

Run these public binary commands:

```text
ao2 --version
ao2-cp-server --version
ao-mission version --json
ao-atlas --version
ao-command version --json
forge --version
covenant version --json
```

Check the exact pinned version and, where emitted, the release source SHA or schema. Record argv, exit, stdout, stderr, and elapsed milliseconds. Pass a minimal environment containing the temporary install root and platform-required system variables; remove AO/provider token variables.

- [ ] **Step 4: Write failing tests for report validation and reconciliation failures**

```python
def test_report_requires_seven_unique_components(self):
    report = self.valid_report()
    report["components"].pop()
    with self.assertRaisesRegex(ValueError, "seven components"):
        canary.validate_report(report)

def test_report_denies_external_mutations(self):
    report = self.valid_report()
    report["external_mutations"] = 1
    with self.assertRaisesRegex(ValueError, "external mutations"):
        canary.validate_report(report)
```

- [ ] **Step 5: Run report tests and verify RED**

Run: `python3 -m unittest scripts.test_run_public_stack_canary.ReportTests -v`

Expected: failures because report validation does not exist.

- [ ] **Step 6: Implement the public credential-free smoke and report**

Run component-owned help or validation commands without providers. Build an Atlas terminal index from a pinned public fixture, verify it with Atlas, import it into a temporary Mission home, and read it through Mission and Command. Assert that each readback binds the same canonical index digest while retaining its own state digest. Set provider calls, credentials, publications, deployments, and external mutations to zero in the report and reject any nonzero value.

- [ ] **Step 7: Run all offline tests**

Run: `python3 -m unittest scripts.test_run_public_stack_canary -v`

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add scripts/run_public_stack_canary.py scripts/test_run_public_stack_canary.py
git commit -m "Exercise public stack identities and reconciliation"
```

### Task 3: Native hosted canary workflow

**Files:**
- Create: `.github/workflows/public-stack-canary.yml`
- Modify: `scripts/test_run_public_stack_canary.py`

**Interfaces:**
- Consumes: `python3 scripts/run_public_stack_canary.py --target TARGET --output PATH`.
- Produces: artifacts named `public-stack-canary-TARGET` containing `public-stack-canary-TARGET.json`.

- [ ] **Step 1: Write a failing static workflow regression**

Assert that the workflow contains exactly the three targets and runners, invokes the canary with the matrix target, uploads the JSON result, grants `contents: read`, and has no secret or write permission references.

- [ ] **Step 2: Run the workflow test and verify RED**

Run: `python3 -m unittest scripts.test_run_public_stack_canary.WorkflowTests -v`

Expected: FAIL because `.github/workflows/public-stack-canary.yml` is missing.

- [ ] **Step 3: Add the minimal matrix workflow**

Use `workflow_dispatch` and `pull_request` triggers, `actions/checkout`, a three-entry matrix with explicit target/runner pairs, the runner command, and `actions/upload-artifact`. Do not add setup actions or dependencies; hosted Python 3 is sufficient.

- [ ] **Step 4: Run all offline tests and Architecture verification**

Run:

```bash
python3 -m unittest scripts.test_run_public_stack_canary -v
python3 scripts/verify_architecture.py
python3 scripts/verify_agent_instruction_layout.py --workspace-root .. --repository ao-architecture
git diff --check
```

Expected: all commands exit 0.

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/public-stack-canary.yml scripts/test_run_public_stack_canary.py
git commit -m "Run public stack canary on three platforms"
```

### Task 4: Live qualification and evidence handoff

**Files:**
- Modify only if qualification exposes a tested defect: the files from Tasks 1-3.
- Generated outside source: campaign Gate 6 evidence directory.

**Interfaces:**
- Produces: one verified JSON result for each native target and a PR/run ledger for the release campaign.

- [ ] **Step 1: Run the real macOS public canary**

Run: `python3 scripts/run_public_stack_canary.py --target macos-aarch64 --output "$CAMPAIGN_ROOT/gate-6/public-stack-canary-macos-aarch64.json"`

Expected: exit 0 and a valid seven-component result with all mutation counters zero.

- [ ] **Step 2: Run full local gates**

Run the offline tests, `python3 scripts/verify_architecture.py`, instruction-layout verification, and `git diff --check` again from the final source tree.

- [ ] **Step 3: Push and open one bounded Architecture pull request**

Request `harufumigithub` as the independent human reviewer. Do not merge until required review and every hosted check pass.

- [ ] **Step 4: Independently verify hosted artifacts**

Download all three workflow artifacts with `gh run download`. Recompute each artifact SHA-256, parse each JSON document independently, verify target/runner identity, seven pinned versions, public URLs and asset digests, command exits, reconciliation digests, cleanup success, and zero mutation counters.

- [ ] **Step 5: Record evidence and continue to Architecture truth updates**

Write the exact PR, review, merge, workflow, job, artifact, and digest bindings into the private campaign ledger. Do not claim Gate 6 complete until Linux, macOS, and Windows results all pass independent verification.
