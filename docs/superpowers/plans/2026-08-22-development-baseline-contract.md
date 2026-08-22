# AO Development Baseline Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The operator has disabled subagents for this campaign.

**Goal:** Create and qualify a strict manifest identity for the fourteen-repository stable AO development baseline.

**Architecture:** AO Architecture owns a closed JSON manifest, its JSON Schema, and a standard-library Python verifier. The manifest pins fourteen target repository commits and seven runtime releases; verification evidence separately records the controller commit so the manifest never self-references. Validation is offline, deterministic, bounded, duplicate-key-safe, and authority-denying.

**Tech Stack:** Python 3 standard library, JSON Schema 2020-12, Git, SHA-256, AO Architecture verification, AO Mission artifact retention.

---

## Fixed Inputs

- Approved design: `docs/superpowers/specs/2026-08-22-development-baseline-contract-design.md`
- Protected release input: `stack/current-release-manifest.json`
- Protected release input SHA-256: `903061a5983068040d19c05adb5e6d0d29f0bf15a59f1bfbf533ac448f0f4e8d`
- S01 Mission: `mission-0d10a1a990af0fdc`
- Correlation: `ao-cross-platform-development-baseline-20260822-r2`
- Mission controller source at intake: `500a7b6e353f1d27fcdfd2115f6b0966f172a73b`
- S01 design commit: `bf26e18`

## Task 1: Strict Loader And Canonical Identity

**Files:**
- Create: `scripts/test_verify_development_baseline.py`
- Create: `scripts/verify_development_baseline.py`

- [ ] **Step 1: Write failing loader and identity tests**

Create a `unittest.TestCase` that imports the wished-for verifier API and proves
bounded reads, duplicate-key rejection, non-UTF-8 rejection, deterministic
canonical JSON, and SHA-256 identity formatting:

```python
from verify_development_baseline import (
    InputError,
    canonical_bytes,
    identity_digest,
    load_json_file,
)

class StrictLoaderTests(unittest.TestCase):
    def test_duplicate_key_is_rejected(self):
        path = self.write_bytes(b'{"schema":"one","schema":"two"}')
        with self.assertRaisesRegex(InputError, "duplicate key: schema"):
            load_json_file(path, 1024)

    def test_oversized_input_is_rejected_before_decode(self):
        path = self.write_bytes(b"{} " * 1024)
        with self.assertRaisesRegex(InputError, "exceeds 32 bytes"):
            load_json_file(path, 32)

    def test_non_utf8_input_is_rejected(self):
        path = self.write_bytes(b'{"schema":"\xff"}')
        with self.assertRaisesRegex(InputError, "UTF-8"):
            load_json_file(path, 1024)

    def test_identity_uses_sorted_compact_utf8_json(self):
        left = {"z": 1, "a": ["é", True]}
        right = {"a": ["é", True], "z": 1}
        self.assertEqual(canonical_bytes(left), canonical_bytes(right))
        self.assertRegex(identity_digest(left), r"^sha256:[0-9a-f]{64}$")
```

- [ ] **Step 2: Run the loader tests and observe RED**

Run:

```powershell
python3 scripts/test_verify_development_baseline.py
```

Expected: import failure because `scripts/verify_development_baseline.py` does
not exist.

- [ ] **Step 3: Implement the smallest strict loader and identity API**

Implement these exact public functions and error type:

```python
class InputError(ValueError):
    pass

def reject_duplicate_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError(f"duplicate key: {key}")
        result[key] = value
    return result

def load_json_file(path, maximum_bytes):
    target = Path(path)
    if not target.is_file() or target.is_symlink():
        raise InputError(f"input is not a regular file: {target}")
    size = target.stat().st_size
    if size > maximum_bytes:
        raise InputError(f"input exceeds {maximum_bytes} bytes: {target}")
    try:
        text = target.read_bytes().decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InputError(f"input is not UTF-8: {target}") from exc
    try:
        return json.loads(text, object_pairs_hook=reject_duplicate_pairs)
    except json.JSONDecodeError as exc:
        raise InputError(f"invalid JSON: {target}: {exc.msg}") from exc

def canonical_bytes(document):
    return json.dumps(
        document, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")

def identity_digest(document):
    return "sha256:" + hashlib.sha256(canonical_bytes(document)).hexdigest()
```

- [ ] **Step 4: Run the loader tests and observe GREEN**

Run `python3 scripts/test_verify_development_baseline.py`.

Expected: all `StrictLoaderTests` pass.

## Task 2: Closed Schema And Stable Repository Profile

**Files:**
- Create: `docs/contracts/development-baseline-manifest-v1.schema.json`
- Create: `stack/development-baseline-manifest.json`
- Modify: `scripts/test_verify_development_baseline.py`
- Modify: `scripts/verify_development_baseline.py`

- [ ] **Step 1: Add failing stable-profile tests**

Add table-driven cases that clone the valid fixture and assert these stable
errors:

```python
cases = {
    "duplicate repository": duplicate_repository,
    "missing stable member": remove_mission,
    "unexpected stable member": add_ao_next,
    "repository commit must be lowercase 40-character hex": malformed_commit,
    "repository identity cannot use only a moving branch": remove_commit,
    "unsafe repository path": use_parent_path,
    "repository upstream must be canonical HTTPS": use_ssh_upstream,
    "unknown property": add_unknown_repository_property,
}
for expected, mutate in cases.items():
    with self.subTest(expected=expected):
        document = copy.deepcopy(self.valid_manifest)
        mutate(document)
        self.assertIn(expected, validate_manifest(document, self.release_input))
```

Also load the real schema and assert `additionalProperties` is false at the
top level and for repository, gate-source, runtime-release, toolchain,
platform-override, and authority definitions.

- [ ] **Step 2: Run focused tests and observe RED**

Run `python3 scripts/test_verify_development_baseline.py`.

Expected: failures because the schema, manifest, and `validate_manifest` do not
exist.

- [ ] **Step 3: Add the strict schema and explicit fourteen-entry manifest**

The schema must require exactly these top-level fields and no others:

```json
{
  "schema": "ao.architecture.development-baseline-manifest.v1",
  "profile": "stable",
  "source_freeze_utc": "2026-08-22T18:00:00Z",
  "repositories": [],
  "release_input": {},
  "runtime_releases": [],
  "toolchains": [],
  "platform_overrides": [],
  "excluded_repositories": ["ao-next"],
  "authority": {}
}
```

Populate `repositories` in the exact order and with the exact upstream commits
from the approved design. Each entry must include:

```json
{
  "name": "ao-architecture",
  "path": "ao-architecture",
  "upstream_url": "https://github.com/uesugitorachiyo/ao-architecture.git",
  "commit": "c0b6f745049bb10034d98946bad4c45174950c0b",
  "branch_metadata": "main",
  "source_role": "architecture_truth",
  "gate_source": {
    "path": "ao-quality-gates.json",
    "sha256": "2f3c727b1e8343cc373c9d561eb5b9ea953f851ac9f767df2e95b9386d83c655",
    "gate_refs": [
      "ao-quality-gates.json#levels.full.steps.architecture-verifier",
      "ao-quality-gates.json#levels.full.steps.python-regressions"
    ]
  }
}
```

For repositories without `ao-quality-gates.json`, bind the exact `AGENTS.md`
SHA-256 and use `AGENTS.md#Verification:<one-based ordinal>` locators for every
unconditional full-gate command. Do not include conditional release,
publication, live-provider, or instruction-only commands.

- [ ] **Step 4: Implement structural and cross-field validation**

Add constants for the exact stable names, safe name pattern, commit pattern,
canonical upstreams, allowed top-level keys, and allowed nested keys. Implement
`validate_manifest(document, release_input)` to return sorted unique errors and
to enforce exact ordering, uniqueness, safe paths, canonical upstreams, exact
commits, exact gate-source digests, `ao-next` exclusion, and closed objects.

- [ ] **Step 5: Run focused tests and observe GREEN**

Run `python3 scripts/test_verify_development_baseline.py`.

Expected: loader and stable-profile tests pass.

## Task 3: Seven Runtime Releases And Digest Provenance

**Files:**
- Modify: `stack/development-baseline-manifest.json`
- Modify: `scripts/test_verify_development_baseline.py`
- Modify: `scripts/verify_development_baseline.py`

- [ ] **Step 1: Add failing release-binding tests**

Cover:

```python
release_cases = {
    "release input digest drift": change_release_input_digest,
    "runtime release count must be 7": remove_runtime_release,
    "runtime release tag drift": change_mission_tag,
    "runtime release tag target drift": change_atlas_target,
    "runtime platform digest drift": change_windows_digest,
    "supplemental digest source is required": remove_control_plane_provenance,
    "Covenant macOS asset requires Rosetta 2": remove_covenant_rosetta_override,
}
```

Assert the real protected release file hashes to
`903061a5983068040d19c05adb5e6d0d29f0bf15a59f1bfbf533ac448f0f4e8d`.

- [ ] **Step 2: Run focused tests and observe RED**

Run `python3 scripts/test_verify_development_baseline.py`.

Expected: release-binding assertions fail.

- [ ] **Step 3: Populate the seven exact release bindings**

For AO2, AO Mission, AO Command, AO Atlas, and AO Forge, copy the exact release
identity and `asset_sha256` maps from the protected release input. For AO2
Control Plane and AO Covenant, preserve the protected tag/release identity and
add the supplemental GitHub release API URL plus the exact six platform digests
listed in the approved S01 design. Select Covenant Darwin amd64 for macOS arm64
with the declared Rosetta 2 override.

- [ ] **Step 4: Implement exact protected-input comparison**

Add `sha256_file(path)` and release-record extraction. Validation must compare
every manifest field represented in the protected release input, require all
selected platform assets to have lowercase SHA-256, and accept supplemental
digests only for the two named releases and exact producer API URLs.

- [ ] **Step 5: Run focused tests and observe GREEN**

Run `python3 scripts/test_verify_development_baseline.py`.

Expected: all release tests pass.

## Task 4: Toolchains, Overrides, And Denied Authority

**Files:**
- Modify: `stack/development-baseline-manifest.json`
- Modify: `scripts/test_verify_development_baseline.py`
- Modify: `scripts/verify_development_baseline.py`

- [ ] **Step 1: Add failing policy tests**

Add one test per allowed override plus explicit rejection tests for unknown
toolchains, duplicate toolchains, undeclared overrides, authority widening,
AO Next stable inclusion, absolute paths, and environment-dependent identity
fields.

- [ ] **Step 2: Run focused tests and observe RED**

Run `python3 scripts/test_verify_development_baseline.py`.

Expected: toolchain, override, and authority assertions fail.

- [ ] **Step 3: Populate the closed toolchain and override sets**

Declare Git, Python, Go, Rust, Cargo, Node, npm, PowerShell, and POSIX shell with
version-probe argv arrays and bounded version constraints. Add only the four
override families approved by the design. Set every authority field to false,
including `rsi`.

- [ ] **Step 4: Implement policy validation**

Require exact tool names, unique order, non-empty argv arrays without shell
metacharacters, supported constraint forms, exact override IDs, exact platform
selectors, and all-false authority. Reject timestamps, roots, process IDs, or
controller commits outside their approved fields.

- [ ] **Step 5: Run focused tests and observe GREEN**

Run `python3 scripts/test_verify_development_baseline.py`.

Expected: all policy tests pass.

## Task 5: CLI, Documentation, And Architecture Integration

**Files:**
- Modify: `scripts/test_verify_development_baseline.py`
- Modify: `scripts/verify_development_baseline.py`
- Create: `docs/development-baseline.md`
- Modify: `AGENTS.md`

- [ ] **Step 1: Add failing CLI tests**

Use `subprocess.run` against the real CLI and assert a valid manifest prints
exactly five stable lines—controller source commit, baseline identity,
repository count, release count, and `errors=0`—while invalid input prints
sorted errors to stderr and returns 1.
Assert the output contains no absolute controller path.

- [ ] **Step 2: Run focused tests and observe RED**

Run `python3 scripts/test_verify_development_baseline.py`.

Expected: CLI tests fail because `main()` is incomplete.

- [ ] **Step 3: Implement the CLI**

Support only:

```text
--manifest <path>
--schema <path>
--release-manifest <path>
--controller-commit <40-character lowercase commit>
```

Default the three paths to their repository locations. Record the controller
commit in output evidence but exclude it from `identity_digest(document)`.
Never run Git or access the network from the verifier.

- [ ] **Step 4: Document use and update Architecture instructions**

`docs/development-baseline.md` must explain target versus controller identity,
the fourteen repositories, seven releases, supplemental provenance, toolchain
and override boundaries, exact verification command, and denied authorities.
Add the focused test/verifier pair to `AGENTS.md` under Verification because the
durable contract command is new.

- [ ] **Step 5: Run focused and Architecture gates**

Run:

```powershell
python3 scripts/test_verify_development_baseline.py
python3 scripts/verify_development_baseline.py --manifest stack/development-baseline-manifest.json --controller-commit (git rev-parse HEAD)
python3 scripts/verify_architecture.py
git diff --check
```

Expected: tests pass; verifier prints `repositories=14`,
`runtime_releases=7`, and `errors=0`; Architecture verification and diff check
exit zero.

## Task 6: Commit, Independent Review, And Mission Checkpoint

**Files:**
- Generated only: operator-owned S01 evidence beneath the private campaign root
- Generated only: AO Mission retained artifacts

- [ ] **Step 1: Commit the S01 implementation**

Stage only the schema, manifest, verifier, tests, current documentation,
approved design/plan, and `AGENTS.md`. Do not stage `scripts/__pycache__/` or any
generated evidence. Commit with:

```powershell
git commit -m "feat: freeze development baseline contract"
```

- [ ] **Step 2: Re-run fresh verification on the committed source**

Run the four Task 5 commands again using the committed `git rev-parse HEAD`.
Record command, exit status, source commit, manifest identity, release-input
digest, and test count in private S01 evidence.

- [ ] **Step 3: Obtain independent review**

Review must explicitly approve or reject:

```text
inventory_exact=true
release_binding_exact=true
gate_source_provenance_exact=true
controller_identity_separate=true
authority_boundary_preserved=true
```

The reviewer must be independent of the implementation author. A missing,
self-authored, ambiguous, or rejected review blocks S01.

- [ ] **Step 4: Import and checkpoint S01 in Mission**

Retain a public-safe S01 artifact containing the committed controller source,
manifest identity, release-input digest, focused/full test summary, review
identity, review decision, and all-false authority fields. Import it through a
correlation-bound neutral evidence chain, create a Mission checkpoint, and
verify Mission status/inspect/checkpoint/Command readbacks preserve mission
`mission-0d10a1a990af0fdc` and correlation
`ao-cross-platform-development-baseline-20260822-r2`.

- [ ] **Step 5: Enforce the S01 stop gate**

Continue to S02 only when the S01 review is independent and approved, every
verification command exits zero, the Architecture tracked worktree is clean,
the artifact rehashes, and Mission records one new S01 checkpoint without
execution or approval authority.
