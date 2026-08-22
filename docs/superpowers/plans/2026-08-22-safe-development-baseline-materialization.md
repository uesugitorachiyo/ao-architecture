# Safe Development Baseline Materialization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Materialize or read-only verify the exact S01 AO development baseline on native macOS and Windows, including detached source identities, native runtime assets, preflight capabilities, deterministic evidence, cleanup, and independent rehashing.

**Architecture:** One Python standard-library controller owns all behavior. Thin PowerShell and POSIX wrappers forward argv, and one workflow runs the same controller on `macos-26` and `windows-2025`; local fixture tests exercise each unsafe boundary without network access.

**Tech Stack:** Python 3 standard library, Git argv, tar/ZIP libraries, urllib, PowerShell 5.1-compatible script, POSIX shell, GitHub Actions.

---

### Task 1: Input Loading And Root Containment

**Files:**
- Create: `scripts/test_bootstrap_development_baseline.py`
- Create: `scripts/bootstrap_development_baseline.py`

- [ ] **Step 1: Write failing loader and root tests**

Import the planned module with `importlib.util`. Add tests for:

```python
load_json_file(path, maximum_bytes)
validate_materialization_root(root, mode)
contained_child(root, name)
is_link_or_reparse(path)
```

Prove duplicate JSON keys, non-UTF-8, symlink inputs, oversized inputs, absolute
or multi-component repository names, an existing non-empty materialize root,
a missing verify-existing root, symlink/reparse ancestors, case-fold sibling
collisions, and escaped child paths fail. Prove absent and existing-empty roots
pass materialize mode and a regular existing root passes verify-existing mode.

- [ ] **Step 2: Run focused tests and observe RED**

```powershell
python3 scripts/test_bootstrap_development_baseline.py
```

Expected: import fails because the bootstrap module does not exist.

- [ ] **Step 3: Implement bounded input and root primitives**

Use `Path.lstat`, `stat.FILE_ATTRIBUTE_REPARSE_POINT` when available,
`resolve(strict=False)`, and `os.path.commonpath`. Never follow a symlink or
reparse point to decide containment. Use duplicate-key JSON decoding and fixed
1 MiB manifest/schema/release limits.

- [ ] **Step 4: Run focused tests and observe GREEN**

Run the Task 1 command. Expected: all loader/root tests pass.

- [ ] **Step 5: Commit Task 1**

```powershell
git add scripts/bootstrap_development_baseline.py scripts/test_bootstrap_development_baseline.py
git commit -m "feat: validate baseline materialization roots"
```

### Task 2: Repository Materialization And Read-Only Verification

**Files:**
- Modify: `scripts/test_bootstrap_development_baseline.py`
- Modify: `scripts/bootstrap_development_baseline.py`

- [ ] **Step 1: Write failing local-Git fixture tests**

Create temporary working and bare repositories with fixed author/committer
metadata and one commit. Test real argv behavior for:

- canonical sibling order;
- `GIT_TERMINAL_PROMPT=0` and `GCM_INTERACTIVE=Never`;
- detached exact checkout;
- exact origin and commit;
- tracked and untracked dirt;
- attached branch;
- missing and extra siblings;
- unsafe repository symlink/reparse entry;
- submodule status beginning with `-`, `+`, or `U`; and
- paths containing spaces.

Call `materialize_repositories(root, specs, runner)` and
`verify_repositories(root, specs, runner)` directly with local fixture
upstreams. Snapshot file hashes before verify-existing and require no changes.

- [ ] **Step 2: Run focused tests and observe RED**

Run the Task 1 command. Expected: repository functions are absent.

- [ ] **Step 3: Implement explicit Git argv and verification**

Add a `CommandRunner` that accepts argv arrays only, fixed environment
overrides, bounded stdout/stderr, timeout, and deterministic failure text.
Materialize with `git clone --no-checkout --no-tags` then detached checkout.
Verify `HEAD`, symbolic-ref failure, origin, porcelain status, submodules,
containment, and top-level sibling set. Preserve partial roots on failure.

- [ ] **Step 4: Run focused tests and observe GREEN**

Run the Task 1 command. Expected: all real local-Git tests pass.

- [ ] **Step 5: Commit Task 2**

```powershell
git add scripts/bootstrap_development_baseline.py scripts/test_bootstrap_development_baseline.py
git commit -m "feat: materialize exact detached repositories"
```

### Task 3: Bounded Native Runtime Assets

**Files:**
- Modify: `scripts/test_bootstrap_development_baseline.py`
- Modify: `scripts/bootstrap_development_baseline.py`

- [ ] **Step 1: Write failing asset tests**

Use in-memory response objects and synthetic tar/ZIP/plain files. Cover:

- HTTPS-only immutable URL construction;
- platform selection of exactly seven assets;
- declared and streamed byte limits;
- exclusive destination creation;
- expected/actual SHA-256 mismatch;
- absolute, drive, UNC, `..`, empty, duplicate, and case-fold-colliding names;
- tar symlink, hard link, FIFO, device, and unknown types;
- ZIP symlink attributes;
- member count, individual size, and expanded-total limits;
- containment with paths containing spaces; and
- Covenant plain executable disposition.

Tests call `download_bounded`, `safe_extract_tar`, `safe_extract_zip`,
`install_plain_asset`, and `materialize_runtime_assets` without internet.

- [ ] **Step 2: Run focused tests and observe RED**

Run the Task 1 command. Expected: asset functions are absent.

- [ ] **Step 3: Implement bounded download, digest, and extraction**

Use 256 MiB compressed/member and 512 MiB expanded maxima, 1,024 entries,
exclusive `xb` writes, fixed timeouts, and no credential headers. Normalize
member names with POSIX rules before platform path conversion. Reject every
non-regular archive type and setuid/setgid bit before writing.

- [ ] **Step 4: Run focused tests and observe GREEN**

Run the Task 1 command. Expected: asset tests pass.

- [ ] **Step 5: Commit Task 3**

```powershell
git add scripts/bootstrap_development_baseline.py scripts/test_bootstrap_development_baseline.py
git commit -m "feat: verify bounded native runtime assets"
```

### Task 4: Toolchain Preflight And Deterministic Evidence

**Files:**
- Modify: `scripts/test_bootstrap_development_baseline.py`
- Modify: `scripts/bootstrap_development_baseline.py`

- [ ] **Step 1: Write failing preflight and evidence tests**

Cover version parsing for Git, Python, Go, Rust/Cargo, Node/npm, PowerShell, and
Bash; minimum and exact-major constraints; missing tools; nonzero probes;
Windows executable/Bash/PowerShell capability classification; macOS Covenant
Rosetta requirement; CRLF, case, symlink, locking, and spaces probes; canonical
repository/asset ordering; bounded command summaries; atomic result creation;
and all-false authority.

Run materialize probes only beneath a fixture `.ao-baseline`. Snapshot an
existing root and prove verify-existing reads retained probe evidence and
changes no byte.

- [ ] **Step 2: Run focused tests and observe RED**

Run the Task 1 command. Expected: preflight/result functions are absent.

- [ ] **Step 3: Implement preflight and result contracts**

Implement fixed version argv from the manifest, numeric version extraction and
constraint comparison, platform capability records, deterministic ordered
objects, atomic exclusive result writes, and this exact authority set:

```python
AUTHORITY = {
    "safe_to_execute": False,
    "executes_work": False,
    "approves_work": False,
    "mutates_repositories": False,
    "provider_calls": False,
    "credential_use": False,
    "release": False,
    "publication": False,
    "deployment": False,
    "promotion": False,
    "compatibility_activation": False,
    "external_beta": False,
    "rsi": False,
}
```

- [ ] **Step 4: Run focused tests and observe GREEN**

Run the Task 1 command. Expected: all preflight/evidence tests pass.

- [ ] **Step 5: Commit Task 4**

```powershell
git add scripts/bootstrap_development_baseline.py scripts/test_bootstrap_development_baseline.py
git commit -m "feat: record native baseline preflight evidence"
```

### Task 5: CLI And Native Wrappers

**Files:**
- Modify: `scripts/test_bootstrap_development_baseline.py`
- Modify: `scripts/bootstrap_development_baseline.py`
- Create: `scripts/bootstrap-development-baseline.ps1`
- Create: `scripts/bootstrap-development-baseline.sh`
- Modify: `docs/development-baseline.md`
- Modify: `AGENTS.md`

- [ ] **Step 1: Write failing CLI tests**

Run the controller as a subprocess. Prove:

- `--mode` accepts only materialize or verify-existing;
- exact manifest/schema/release/controller/root/result arguments are required;
- controller commit must be lowercase 40-hex;
- result must be outside the root for verify-existing;
- manifest validation occurs before root mutation;
- errors are sorted/stable, go to stderr, and return nonzero;
- success output contains result digest, baseline identity, repository count 14,
  runtime count 7, and errors 0; and
- no absolute root or private host detail is printed.

Add wrapper text tests that forbid command-string evaluation and require argv
forwarding.

- [ ] **Step 2: Run focused tests and observe RED**

Run the Task 1 command. Expected: CLI/wrapper assertions fail.

- [ ] **Step 3: Implement CLI orchestration and wrappers**

Import `verify_development_baseline.py` from the same scripts directory,
validate S01 inputs first, then route the exact mode. Write failure results only
when the explicit result parent is safe and writable. Keep the shell wrapper
POSIX and the PowerShell wrapper compatible with Windows PowerShell 5.1.

- [ ] **Step 4: Update Architecture documentation**

Document exact commands for both modes, empty-root and read-only semantics,
native asset download behavior, evidence fields, and denied authorities. Add
the focused bootstrap test and PowerShell parser to `AGENTS.md`.

- [ ] **Step 5: Run focused native gates**

```powershell
python3 scripts/test_bootstrap_development_baseline.py
powershell.exe -NoProfile -NonInteractive -Command "[void][scriptblock]::Create((Get-Content -Raw scripts/bootstrap-development-baseline.ps1))"
python3 scripts/verify_architecture.py
git diff --check
```

Expected: every command exits zero.

- [ ] **Step 6: Commit Task 5**

```powershell
git add AGENTS.md docs/development-baseline.md scripts/bootstrap_development_baseline.py scripts/test_bootstrap_development_baseline.py scripts/bootstrap-development-baseline.ps1 scripts/bootstrap-development-baseline.sh
git commit -m "feat: expose native baseline bootstrap"
```

### Task 6: Hosted Matrix, Cleanup, And Independent Rehash

**Files:**
- Create: `.github/workflows/development-baseline-bootstrap.yml`
- Modify: `scripts/test_bootstrap_development_baseline.py`

- [ ] **Step 1: Write failing workflow contract tests**

Parse workflow YAML as text/JSON-safe structure and require:

- `workflow_dispatch` only;
- matrix values exactly `macos-26` and `windows-2025`;
- unique runner-temp roots containing spaces;
- native wrapper selection;
- controller commit from `git rev-parse HEAD`;
- artifact names bound to platform and source commit;
- upload before cleanup;
- cleanup guarded with `always()` and exact-root containment;
- proof the root is absent after cleanup;
- two host results plus two cleanup results;
- a dependent rehash job that downloads both results and recomputes all hashes;
- no secrets, credentials, provider calls, releases, deployments, publication,
  promotion, or self-hosted runner labels.

- [ ] **Step 2: Run focused tests and observe RED**

Run the Task 1 command. Expected: workflow file is absent.

- [ ] **Step 3: Implement the hosted workflow**

Use `actions/checkout@v4`, `actions/upload-artifact@v4`, and
`actions/download-artifact@v4`. Matrix jobs invoke only native wrappers and
public GitHub assets. Cleanup removes only the unique runner-temp root after
validating its prefix. The Ubuntu rehash job uses the committed Python
controller's evidence helpers without materializing or modifying repositories.

- [ ] **Step 4: Run S02 local integration gates**

```powershell
python3 scripts/test_bootstrap_development_baseline.py
powershell.exe -NoProfile -NonInteractive -Command "[void][scriptblock]::Create((Get-Content -Raw scripts/bootstrap-development-baseline.ps1))"
python3 scripts/verify_development_baseline.py --manifest stack/development-baseline-manifest.json --controller-commit $(git rev-parse HEAD)
python3 scripts/verify_architecture.py
python3 -m unittest discover -s scripts -p 'test_*.py'
git diff --check
```

Record any pre-existing Windows fixture failures separately; all S02-focused
and required Architecture gates must pass.

- [ ] **Step 5: Commit Task 6**

```powershell
git add .github/workflows/development-baseline-bootstrap.yml scripts/test_bootstrap_development_baseline.py
git commit -m "ci: qualify baseline bootstrap on native hosts"
```

### Task 7: Hosted Proof And S02 Mission Checkpoint

**Files:**
- Generated only: GitHub Actions artifacts and private campaign evidence

- [ ] **Step 1: Push the reviewed branch and run the workflow**

Push the exact Architecture branch, make the workflow available through its
normal reviewed integration path, and dispatch it at the exact merged source
commit. Do not dispatch from unreviewed or dirty source.

- [ ] **Step 2: Verify both host and cleanup artifacts**

Require the same S01 baseline identity, fourteen exact detached clean commits,
seven native assets, required toolchains/capabilities, zero undeclared skips,
and cleanup root absent on macOS and Windows.

- [ ] **Step 3: Verify the independent rehash report**

Require zero missing, extra, size, or digest mismatches and exact source,
workflow-run, host-job, artifact-name, and correlation bindings.

- [ ] **Step 4: Import and checkpoint S02**

Create a public-safe S02 evidence artifact linked to the host artifacts and
rehash report. Import it through a correlation chain, then run:

```powershell
go run ./cmd/ao-mission --home $env:AO_MISSION_HOME checkpoint create --mission mission-0d10a1a990af0fdc --slice S02 --evidence-digest $s02EvidenceDigest --json
```

Require checkpoint count 3, exact S02 digest, idempotent replay, unchanged
Mission lifecycle, and false authority before starting S03.
