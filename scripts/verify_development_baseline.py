#!/usr/bin/env python3
"""Verify the frozen AO cross-platform development-baseline manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterable


STABLE_REPOSITORIES = (
    "ao-architecture",
    "ao-mission",
    "ao-blueprint",
    "ao-atlas",
    "ao-foundry",
    "ao-forge",
    "ao-covenant",
    "ao2",
    "ao2-control-plane",
    "ao-command",
    "ao-arena",
    "ao-crucible",
    "ao-sentinel",
    "ao-promoter",
)

FROZEN_REPOSITORIES = {
    "ao-architecture": ("ef421a4e22a1e5832d58acdca14b46862aa119a3", "architecture_truth"),
    "ao-mission": ("1aeb2cd78c8a7c5df100cdf1bd17d20c478ca47e", "mission_state"),
    "ao-blueprint": ("ec6a80b60b54c0c0ac1822f873c1abf337fe5eb5", "requirements_authorization"),
    "ao-atlas": ("acd162ad1b187a9fe179e36cb0d20be5db874d69", "workgraph_context"),
    "ao-foundry": ("028ec4d50847247ee48c1d8d4560a4eda3422550", "portfolio_scheduling"),
    "ao-forge": ("b17a6dc58d4938b3dbe10ec949b6b1008b192379", "goal_run"),
    "ao-covenant": ("7d2af0d3446757f096ebf3ce51e0918716daf7ff", "policy_contract_authority"),
    "ao2": ("880f32ce8d9af5ba6e50aa5885c214c04f23f20d", "execution"),
    "ao2-control-plane": ("4e41da173dc9f1ee37f4ae99b85791e5f05ea453", "evidence_observation"),
    "ao-command": ("ffef6d76306e892c3e7a7f39734433d5a832006a", "operator_presentation"),
    "ao-arena": ("88a52d9a42c5bffe998b45c5046f36be0cf5ea43", "benchmark"),
    "ao-crucible": ("64227e3ee305cc3399063b567e02a548b5bc1855", "adversarial_assurance"),
    "ao-sentinel": ("c301b1192c77a6b1833c49a5c9230491be50a258", "monitoring"),
    "ao-promoter": ("5b103a66476e45bcf0c7fdcf4fffdb82b415ff72", "promotion_decision"),
}

EXPECTED_GATE_SOURCES = {
    "ao-architecture": ("ao-quality-gates.json", "2f3c727b1e8343cc373c9d561eb5b9ea953f851ac9f767df2e95b9386d83c655", ("architecture-verifier", "python-regressions")),
    "ao-mission": ("AGENTS.md", "e85e21a7288e92e98bacb9957ba54c87f6c9678c6e5c3167d65e4992cb4afc45", ("1", "2", "3", "4")),
    "ao-blueprint": ("ao-quality-gates.json", "b56d6eb7c0e4636a451b5d3a9139dc992a454967a5adf202273581c236b7eeb8", ("production-readiness",)),
    "ao-atlas": ("ao-quality-gates.json", "5d71e2021944992173e83a1e1c92c1d1eec40a1de85ef0aa3fd072a7feb9a383", ("go-tests", "go-vet", "go-build")),
    "ao-foundry": ("AGENTS.md", "2ada1272eef474cd1d8fe162ea28a0d060211b22ed334b5a1846e57bcc3976c2", ("1", "2")),
    "ao-forge": ("AGENTS.md", "2b4abb5c872797b89f3ec410a3ab654cd9898f21a289d8cc19f9da5f0ab24fb2", ("1", "2", "3", "4")),
    "ao-covenant": ("AGENTS.md", "4be243338aadbdd1f04a124ac95ee51e486a44e8ec8becaed3cb0d8fe8926b7b", ("1", "2", "3", "4")),
    "ao2": ("ao-quality-gates.json", "f6d8d255c77d4876d514dfb84d68956fc2fed1981b41a756da4c11657f740162", ("workspace-verification", "rust-architecture")),
    "ao2-control-plane": ("AGENTS.md", "8b1739dc1e3e74d4df6332e8b1795387da5c24ee8530ea879e59804cdaa317f0", ("1", "2", "3", "4")),
    "ao-command": ("AGENTS.md", "a50c855a8dcb47b23ac4656633ea8be0a80e0228df9c636135c7c020f0def6ca", ("1", "2")),
    "ao-arena": ("ao-quality-gates.json", "c2e2207b5a67e832615534fbffa9792127c01eac468156600bfe3253815d4980", ("go-tests", "go-vet", "go-build")),
    "ao-crucible": ("AGENTS.md", "28839fb5647f15e477026de1de236b2f7ec58538241ad6d9fe348245f3a64e93", ("1", "2", "3")),
    "ao-sentinel": ("AGENTS.md", "63ce5e1685e7cf27acd5114f2ee4f3f5d7ea0b5eb1faf9783cc1ae26a92bd35f", ("1", "2", "3")),
    "ao-promoter": ("AGENTS.md", "2136efca3d324b5ff748b530c59b4c4bccedbf0c063763544d4d2adcdb4d7c9d", ("1", "2", "3")),
}


def _gate(
    identifier: str,
    argv: list[str],
    timeout: int,
    *,
    shell: str = "direct",
    environment: dict[str, str] | None = None,
    success_stdout: str = "any",
) -> dict[str, Any]:
    return {
        "id": identifier,
        "argv": argv,
        "timeout_seconds": timeout,
        "shell": shell,
        "required": True,
        "environment": environment or {},
        "success_stdout": success_stdout,
    }


EXPECTED_DEVELOPMENT_GATES = {
    "ao-architecture": [
        _gate("architecture-verifier", ["python3", "scripts/verify_architecture.py"], 300),
        _gate("python-regressions", ["python3", "-m", "unittest", "discover", "-s", "scripts", "-p", "test_*.py"], 1500),
    ],
    "ao-mission": [
        _gate("gofmt", ["gofmt", "-d", "cmd", "internal"], 300, success_stdout="empty"),
        _gate("go-tests", ["go", "test", "./...", "-count=1"], 1800),
        _gate("go-vet", ["go", "vet", "./..."], 600),
        _gate("go-build", ["go", "build", "./cmd/ao-mission"], 600),
        _gate("production-readiness", ["scripts/production-readiness.sh"], 2400, shell="posix-script"),
        _gate("diff-check", ["git", "diff", "--check"], 120),
    ],
    "ao-blueprint": [
        _gate("production-readiness", ["scripts/production-readiness.sh"], 1800, shell="posix-script"),
    ],
    "ao-atlas": [
        _gate("go-tests", ["go", "test", "./...", "-count=1"], 1200),
        _gate("go-vet", ["go", "vet", "./..."], 300),
        _gate("go-build", ["go", "build", "-o", "target/quality-gates/atlas", "./cmd/atlas"], 300),
    ],
    "ao-foundry": [
        _gate("gofmt", ["gofmt", "-d", "cmd", "internal"], 300, success_stdout="empty"),
        _gate("go-tests", ["go", "test", "./...", "-count=1"], 1200),
        _gate("go-vet", ["go", "vet", "./..."], 300),
        _gate("build-foundry", ["go", "build", "-o", "bin/foundry", "./cmd/foundry"], 300),
        _gate("build-ao", ["go", "build", "-o", "bin/ao", "./cmd/ao"], 300),
        _gate("diff-check", ["git", "diff", "--check"], 120),
    ],
    "ao-forge": [
        _gate("gofmt", ["gofmt", "-d", "cmd", "internal"], 300, success_stdout="empty"),
        _gate("go-tests", ["go", "test", "./...", "-count=1"], 1200),
        _gate("go-vet", ["go", "vet", "./..."], 300),
        _gate("go-build", ["go", "build", "-o", "bin/forge", "./cmd/forge"], 300),
        _gate("diff-check", ["git", "diff", "--check"], 120),
    ],
    "ao-covenant": [
        _gate("gofmt", ["gofmt", "-d", "cmd", "internal", "schemas"], 300, success_stdout="empty"),
        _gate("go-tests", ["go", "test", "./...", "-count=1"], 1200),
        _gate("go-vet", ["go", "vet", "./..."], 300),
        _gate("go-build", ["go", "build", "-o", "bin/covenant", "./cmd/covenant"], 300, environment={"CGO_ENABLED": "0"}),
        _gate("license-policy", ["scripts/check-license-policy.sh"], 300, shell="posix-script"),
        _gate("public-policy", ["scripts/check-public-repo-policy.sh"], 300, shell="posix-script"),
        _gate("diff-check", ["git", "diff", "--check"], 120),
    ],
    "ao2": [
        _gate("workspace-verification", ["npm", "run", "verify"], 2340),
        _gate("rust-architecture", ["python3", "scripts/check-rust-architecture.py"], 60),
    ],
    "ao2-control-plane": [
        _gate("cargo-fmt", ["cargo", "fmt", "--all", "--", "--check"], 300),
        _gate("workspace-tests", ["python3", "scripts/run-workspace-tests.py"], 2400),
        _gate("cargo-clippy", ["cargo", "clippy", "--workspace", "--all-targets", "--", "-D", "warnings"], 1800),
        _gate("diff-check", ["git", "diff", "--check"], 120),
    ],
    "ao-command": [
        _gate("gofmt", ["gofmt", "-d", "cmd", "internal"], 300, success_stdout="empty"),
        _gate("go-tests", ["go", "test", "./...", "-count=1"], 1200),
        _gate("go-vet", ["go", "vet", "./..."], 300),
        _gate("go-build", ["go", "build", "-o", "bin/ao-command", "./cmd/ao-command"], 300),
        _gate("diff-check", ["git", "diff", "--check"], 120),
    ],
    "ao-arena": [
        _gate("go-tests", ["go", "test", "./...", "-count=1"], 600),
        _gate("go-vet", ["go", "vet", "./..."], 180),
        _gate("go-build", ["go", "build", "-o", "tmp/quality-gates/arena", "./cmd/arena"], 120),
    ],
    "ao-crucible": [
        _gate("gofmt", ["gofmt", "-d", "cmd", "internal"], 300, success_stdout="empty"),
        _gate("go-tests", ["go", "test", "./...", "-count=1"], 1200),
        _gate("go-vet", ["go", "vet", "./..."], 300),
        _gate("go-build", ["go", "build", "-o", "tmp/bin/crucible", "./cmd/crucible"], 300),
        _gate("diff-check", ["git", "diff", "--check"], 120),
    ],
    "ao-sentinel": [
        _gate("gofmt", ["gofmt", "-d", "cmd", "internal"], 300, success_stdout="empty"),
        _gate("go-tests", ["go", "test", "./...", "-count=1"], 1200),
        _gate("go-vet", ["go", "vet", "./..."], 300),
        _gate("go-build", ["go", "build", "-o", "tmp/bin/sentinel", "./cmd/sentinel"], 300),
        _gate("diff-check", ["git", "diff", "--check"], 120),
    ],
    "ao-promoter": [
        _gate("gofmt", ["gofmt", "-d", "cmd", "internal"], 300, success_stdout="empty"),
        _gate("go-tests", ["go", "test", "./...", "-count=1"], 1200),
        _gate("go-vet", ["go", "vet", "./..."], 300),
        _gate("go-build", ["go", "build", "-o", "tmp/bin/promoter", "./cmd/promoter"], 300),
        _gate("diff-check", ["git", "diff", "--check"], 120),
    ],
}

REPOSITORY_KEYS = {
    "name",
    "path",
    "upstream_url",
    "commit",
    "branch_metadata",
    "source_role",
    "gate_source",
    "development_gates",
}
GATE_SOURCE_KEYS = {"path", "sha256", "gate_refs"}
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
RELEASE_INPUT_KEYS = {"path", "schema", "sha256"}
RUNTIME_RELEASE_KEYS = {
    "repository",
    "version",
    "tag",
    "tag_target",
    "release_url",
    "is_draft",
    "is_prerelease",
    "asset_count",
    "supplemental_digest_source",
    "assets",
}
RUNTIME_ASSET_KEYS = {"platform", "architecture", "name", "sha256", "source"}

RUNTIME_RELEASES = (
    "ao2",
    "ao2-control-plane",
    "ao-mission",
    "ao-command",
    "ao-atlas",
    "ao-forge",
    "ao-covenant",
)

SUPPLEMENTAL_RELEASES = {
    "ao2-control-plane": {
        "source": "https://api.github.com/repos/uesugitorachiyo/ao2-control-plane/releases/tags/v0.1.19",
        "assets": {
            "linux": ("ao2-control-plane-0.1.19-linux-x86_64.tar.gz", "588903471152cbc2cae1fc9d514d69b72c153b913a368cb6bf01da09c2789cbf"),
            "macos": ("ao2-control-plane-0.1.19-macos-aarch64.tar.gz", "06addc587bd282763c47d9ee4e36cb8ebea0c114881296569ef4d0b4dff86972"),
            "windows": ("ao2-control-plane-0.1.19-windows-x86_64.tar.gz", "c3528322730afd4a0c3988f9b2a23767f67febbf96b62340988546346ad00e05"),
        },
    },
    "ao-covenant": {
        "source": "https://api.github.com/repos/uesugitorachiyo/ao-covenant/releases/tags/v0.1.1",
        "assets": {
            "linux": ("ao-covenant_v0.1.1_linux_amd64", "f6820fdc7b99873071e7f68fc50d9bfd922750a2e788d9fca5aa8fb37cc8180b"),
            "macos": ("ao-covenant_v0.1.1_darwin_amd64", "9a5ca7c6920c44b6e120d6c5bd8baf190b66e188d43485639c6fc5355190868e"),
            "windows": ("ao-covenant_v0.1.1_windows_amd64.exe", "fd6e3a0033608d3f47dccb60f48191e4c4b2dc4fdce893c87d8ea96199610c5d"),
        },
    },
}

MANIFEST_KEYS = {
    "schema",
    "profile",
    "source_freeze_utc",
    "repositories",
    "release_input",
    "runtime_releases",
    "toolchains",
    "platform_overrides",
    "excluded_repositories",
    "authority",
}

EXPECTED_TOOLCHAINS = {
    "git": (["git", "--version"], {"kind": "minimum", "value": "2.39"}),
    "python": (["python3", "--version"], {"kind": "minimum", "value": "3.11"}),
    "go": (["go", "version"], {"kind": "minimum", "value": "1.26"}),
    "rust": (["rustc", "--version"], {"kind": "minimum", "value": "1.85"}),
    "cargo": (["cargo", "--version"], {"kind": "minimum", "value": "1.85"}),
    "node": (["node", "--version"], {"kind": "minimum", "value": "20"}),
    "npm": (["npm", "--version"], {"kind": "minimum", "value": "10"}),
    "powershell": (["pwsh", "--version"], {"kind": "minimum", "value": "7"}),
    "posix-shell": (["bash", "--version"], {"kind": "minimum", "value": "3.2"}),
}

EXPECTED_OVERRIDES = {
    "windows-git-bash": ("windows", "all", "Run repository-owned .sh gates with Git for Windows Bash only."),
    "windows-powershell-51-parse": ("windows", "all", "Parse declared Windows PowerShell entry points with Windows PowerShell 5.1."),
    "covenant-rosetta2": ("macos-arm64", "ao-covenant", "Run the frozen Darwin amd64 Covenant asset through Rosetta 2."),
    "windows-native-artifact-selection": ("windows", "all", "Select declared Windows executable suffixes and release archive formats."),
    "macos-native-artifact-selection": ("macos-arm64", "all", "Select declared macOS executable suffixes and release archive formats."),
}

AUTHORITY_KEYS = {
    "safe_to_execute",
    "executes_work",
    "approves_work",
    "mutates_repositories",
    "provider_calls",
    "credential_use",
    "release",
    "publication",
    "deployment",
    "promotion",
    "compatibility_activation",
    "external_beta",
    "rsi",
}

DEVELOPMENT_GATE_KEYS = {
    "id",
    "argv",
    "timeout_seconds",
    "shell",
    "required",
    "environment",
    "success_stdout",
}
GATE_AUTHORITY_TERMS = re.compile(
    r"(^|[-_/])(release|publish|deploy|promote|provider|credential|token|rsi|live)([-_/]|$)",
    re.IGNORECASE,
)


class InputError(ValueError):
    """Raised when a verifier input cannot be consumed safely."""


def reject_duplicate_pairs(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    """Build a JSON object while rejecting duplicate member names."""

    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise InputError(f"duplicate key: {key}")
        result[key] = value
    return result


def load_json_file(path: str | Path, maximum_bytes: int) -> Any:
    """Read one bounded, regular, non-symlink UTF-8 JSON file."""

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


def canonical_bytes(document: Any) -> bytes:
    """Return deterministic UTF-8 JSON bytes for identity hashing."""

    return json.dumps(
        document,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def identity_digest(document: Any) -> str:
    """Return the manifest's canonical SHA-256 identity."""

    return "sha256:" + hashlib.sha256(canonical_bytes(document)).hexdigest()


def validate_schema_contract(schema: Any) -> list[str]:
    """Validate the checked-in schema's identity and fail-closed object shape."""

    if not isinstance(schema, dict):
        return ["schema contract drift"]
    properties = schema.get("properties")
    definitions = schema.get("$defs")
    expected_definitions = {
        "sha256",
        "commit",
        "repository",
        "gateSource",
        "developmentGate",
        "releaseInput",
        "asset",
        "runtimeRelease",
        "toolchain",
        "platformOverride",
        "authority",
    }
    valid = (
        schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema"
        and schema.get("$id")
        == "https://github.com/uesugitorachiyo/ao-architecture/docs/contracts/development-baseline-manifest-v1.schema.json"
        and schema.get("type") == "object"
        and schema.get("additionalProperties") is False
        and isinstance(properties, dict)
        and set(properties) == MANIFEST_KEYS
        and isinstance(schema.get("required"), list)
        and set(schema["required"]) == MANIFEST_KEYS
        and len(schema["required"]) == len(MANIFEST_KEYS)
        and isinstance(definitions, dict)
        and set(definitions) == expected_definitions
    )

    def objects_are_closed(value: Any) -> bool:
        if isinstance(value, list):
            return all(objects_are_closed(item) for item in value)
        if not isinstance(value, dict):
            return True
        if value.get("type") == "object" and value.get("additionalProperties") is not False:
            return False
        return all(objects_are_closed(item) for item in value.values())

    if not valid or not objects_are_closed(schema):
        return ["schema contract drift"]
    return []


def sha256_file(path: str | Path) -> str:
    """Hash one regular non-symlink file without changing it."""

    target = Path(path)
    if not target.is_file() or target.is_symlink():
        raise InputError(f"input is not a regular file: {target}")
    return hashlib.sha256(target.read_bytes()).hexdigest()


def _gate_refs(path: str, identifiers: tuple[str, ...]) -> list[str]:
    if path == "ao-quality-gates.json":
        return [f"{path}#levels.full.steps.{identifier}" for identifier in identifiers]
    return [f"AGENTS.md#Verification:{identifier}" for identifier in identifiers]


def validate_development_gates(repository: str, gates: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(gates, list) or not gates:
        return [f"{repository} development gates must be a non-empty array"]
    seen: set[str] = set()
    for index, gate in enumerate(gates):
        label = f"{repository} development_gates[{index}]"
        if not isinstance(gate, dict):
            errors.append(f"{label} must be an object")
            continue
        identifier = gate.get("id")
        gate_label = (
            f"{repository} development gate {identifier}"
            if isinstance(identifier, str) and identifier
            else label
        )
        for unknown in sorted(set(gate) - DEVELOPMENT_GATE_KEYS):
            errors.append(f"{gate_label} unknown property: {unknown}")
        if not isinstance(identifier, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", identifier):
            errors.append(f"{label} id is invalid")
        elif identifier in seen:
            errors.append(f"{repository} duplicate development gate: {identifier}")
        else:
            seen.add(identifier)
        argv = gate.get("argv")
        if not isinstance(argv, list) or not argv or not all(
            isinstance(argument, str) and argument and len(argument) <= 256
            for argument in argv
        ):
            errors.append(f"{gate_label} argv is invalid")
        else:
            if any(re.search(r"[;&|><`$()\r\n]", argument) for argument in argv):
                errors.append(f"{gate_label} argv contains shell metacharacters")
            if any(GATE_AUTHORITY_TERMS.search(argument) for argument in argv):
                errors.append(f"{gate_label} contains authority-bearing argv")
        timeout = gate.get("timeout_seconds")
        if not isinstance(timeout, int) or isinstance(timeout, bool) or not 1 <= timeout <= 3600:
            errors.append(f"{gate_label} timeout is invalid")
        if gate.get("shell") not in {"direct", "posix-script"}:
            errors.append(f"{gate_label} shell is invalid")
        if gate.get("required") is not True:
            errors.append(f"{gate_label} must be required")
        environment = gate.get("environment")
        if not isinstance(environment, dict) or any(
            key != "CGO_ENABLED" or value != "0"
            for key, value in environment.items()
        ):
            errors.append(f"{gate_label} environment is unsafe")
        if gate.get("success_stdout", "any") not in {"any", "empty"}:
            errors.append(f"{gate_label} success stdout policy is invalid")
    return sorted(set(errors))


def validate_repository_profile(repositories: Any) -> list[str]:
    """Validate the exact stable repository inventory and gate provenance."""

    errors: list[str] = []
    if not isinstance(repositories, list):
        return ["repositories must be an array"]

    names = [item.get("name") for item in repositories if isinstance(item, dict)]
    seen: set[Any] = set()
    for name in names:
        if name in seen:
            errors.append(f"duplicate repository: {name}")
        seen.add(name)
    for expected in STABLE_REPOSITORIES:
        if expected not in names:
            errors.append(f"missing stable member: {expected}")
    for name in names:
        if name not in STABLE_REPOSITORIES:
            errors.append(f"unexpected stable member: {name}")
    if len(repositories) == len(STABLE_REPOSITORIES) and tuple(names) != STABLE_REPOSITORIES:
        errors.append("stable repositories are not in canonical order")

    for index, repository in enumerate(repositories):
        if not isinstance(repository, dict):
            errors.append(f"repositories[{index}] must be an object")
            continue
        name = repository.get("name")
        label = name if isinstance(name, str) and name else f"repositories[{index}]"
        for unknown in sorted(set(repository) - REPOSITORY_KEYS):
            errors.append(f"{label} repository unknown property: {unknown}")
        if name not in FROZEN_REPOSITORIES:
            continue
        expected_commit, expected_role = FROZEN_REPOSITORIES[name]
        if repository.get("path") != name or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", str(repository.get("path", ""))):
            errors.append(f"{name} unsafe repository path")
        expected_upstream = f"https://github.com/uesugitorachiyo/{name}.git"
        if repository.get("upstream_url") != expected_upstream:
            errors.append(f"{name} repository upstream must be canonical HTTPS")
        commit = repository.get("commit")
        if commit is None:
            errors.append(f"{name} repository identity cannot use only a moving branch")
        elif not isinstance(commit, str) or not COMMIT_PATTERN.fullmatch(commit):
            errors.append(f"{name} repository commit must be lowercase 40-character hex")
        elif commit != expected_commit:
            errors.append(f"{name} repository commit drift")
        if repository.get("branch_metadata") != "main":
            errors.append(f"{name} branch metadata must be main")
        if repository.get("source_role") != expected_role:
            errors.append(f"{name} source role drift")
        gate_source = repository.get("gate_source")
        if not isinstance(gate_source, dict):
            errors.append(f"{name} gate source must be an object")
            continue
        for unknown in sorted(set(gate_source) - GATE_SOURCE_KEYS):
            errors.append(f"{name} gate source unknown property: {unknown}")
        expected_path, expected_digest, identifiers = EXPECTED_GATE_SOURCES[name]
        if gate_source.get("path") != expected_path:
            errors.append(f"{name} gate source path drift")
        if gate_source.get("sha256") != expected_digest:
            errors.append(f"{name} gate source digest drift")
        refs = gate_source.get("gate_refs")
        expected_refs = _gate_refs(expected_path, identifiers)
        if not isinstance(refs, list):
            errors.append(f"{name} gate refs must be an array")
        else:
            for ref in refs:
                if not isinstance(ref, str) or not (
                    ref.startswith("ao-quality-gates.json#levels.full.steps.")
                    or re.fullmatch(r"AGENTS\.md#Verification:[1-9][0-9]*", ref)
                ):
                    errors.append(f"{name} invalid gate ref: {ref}")
            if refs != expected_refs and all(
                isinstance(ref, str)
                and (
                    ref.startswith("ao-quality-gates.json#levels.full.steps.")
                    or re.fullmatch(r"AGENTS\.md#Verification:[1-9][0-9]*", ref)
                )
                for ref in refs
            ):
                errors.append(f"{name} gate refs drift")
        development_gates = repository.get("development_gates")
        errors.extend(validate_development_gates(name, development_gates))
        if development_gates != EXPECTED_DEVELOPMENT_GATES[name]:
            errors.append(f"{name} development gate inventory drift")
    return sorted(set(errors))


def _release_records(release_input: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(release_input, dict):
        return {}
    records: list[Any] = [release_input.get("ao2"), release_input.get("control_plane")]
    for key in ("tier1_tools", "tier2_tools"):
        value = release_input.get(key)
        if isinstance(value, list):
            records.extend(value)
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        if isinstance(record, dict) and isinstance(record.get("repository"), str):
            result[record["repository"]] = record
    return result


def _validate_release_bindings(
    document: dict[str, Any], release_input: Any, release_path: str | Path
) -> list[str]:
    errors: list[str] = []
    release_binding = document.get("release_input")
    if not isinstance(release_binding, dict):
        errors.append("release input must be an object")
    else:
        for unknown in sorted(set(release_binding) - RELEASE_INPUT_KEYS):
            errors.append(f"release input unknown property: {unknown}")
        if release_binding.get("path") != "stack/current-release-manifest.json":
            errors.append("release input path drift")
        if release_binding.get("schema") != "ao.architecture.current-release-manifest.v0.1":
            errors.append("release input schema drift")
        try:
            actual_digest = sha256_file(release_path)
        except InputError as exc:
            errors.append(str(exc))
        else:
            if release_binding.get("sha256") != actual_digest:
                errors.append("release input digest drift")
    if not isinstance(release_input, dict) or release_input.get("schema") != "ao.architecture.current-release-manifest.v0.1":
        errors.append("protected release input schema drift")

    runtime_releases = document.get("runtime_releases")
    if not isinstance(runtime_releases, list):
        return errors + ["runtime releases must be an array"]
    if len(runtime_releases) != len(RUNTIME_RELEASES):
        errors.append("runtime release count must be 7")
    names = [item.get("repository") for item in runtime_releases if isinstance(item, dict)]
    if tuple(names) != RUNTIME_RELEASES:
        errors.append("runtime releases are not in canonical order")
    if len(names) != len(set(names)):
        errors.append("duplicate runtime release")

    protected = _release_records(release_input)
    for index, runtime in enumerate(runtime_releases):
        if not isinstance(runtime, dict):
            errors.append(f"runtime_releases[{index}] must be an object")
            continue
        name = runtime.get("repository")
        if name not in RUNTIME_RELEASES:
            errors.append(f"unexpected runtime release: {name}")
            continue
        for unknown in sorted(set(runtime) - RUNTIME_RELEASE_KEYS):
            errors.append(f"{name} runtime release unknown property: {unknown}")
        expected = protected.get(name)
        if expected is None:
            errors.append(f"{name} missing from protected release input")
            continue
        for field, label in (
            ("version", "version"),
            ("tag", "tag"),
            ("tag_target", "tag target"),
            ("release_url", "release URL"),
            ("is_draft", "draft disposition"),
            ("is_prerelease", "prerelease disposition"),
            ("asset_count", "asset count"),
        ):
            if runtime.get(field) != expected.get(field):
                errors.append(f"{name} runtime release {label} drift")

        assets = runtime.get("assets")
        if not isinstance(assets, list) or len(assets) != 3:
            errors.append(f"{name} runtime release requires three platform assets")
            continue
        platforms = [asset.get("platform") for asset in assets if isinstance(asset, dict)]
        if platforms != ["linux", "macos", "windows"]:
            errors.append(f"{name} runtime platform order drift")
        supplemental = SUPPLEMENTAL_RELEASES.get(name)
        if supplemental:
            if runtime.get("supplemental_digest_source") != supplemental["source"]:
                errors.append(f"{name} supplemental digest source is required")
        elif "supplemental_digest_source" in runtime:
            errors.append(f"{name} supplemental digest source is not allowed")

        protected_assets = expected.get("asset_sha256", {})
        for asset in assets:
            if not isinstance(asset, dict):
                errors.append(f"{name} runtime asset must be an object")
                continue
            platform = asset.get("platform")
            for unknown in sorted(set(asset) - RUNTIME_ASSET_KEYS):
                errors.append(
                    f"{name} {platform} runtime asset unknown property: {unknown}"
                )
            asset_name = asset.get("name")
            digest = asset.get("sha256")
            if not isinstance(digest, str) or not SHA256_PATTERN.fullmatch(digest):
                errors.append(f"{name} invalid runtime platform digest: {platform}")
                continue
            if supplemental:
                expected_name, expected_digest = supplemental["assets"].get(platform, (None, None))
                expected_source = "github-release-api"
            else:
                expected_name = asset_name
                expected_digest = protected_assets.get(asset_name)
                expected_source = "current-release-manifest"
            if asset_name != expected_name or digest != expected_digest:
                errors.append(f"{name} runtime platform digest drift: {platform}")
            if asset.get("source") != expected_source:
                errors.append(f"{name} runtime platform digest source drift: {platform}")

    overrides = document.get("platform_overrides")
    override_ids = {
        item.get("id") for item in overrides if isinstance(item, dict)
    } if isinstance(overrides, list) else set()
    covenant = next(
        (item for item in runtime_releases if isinstance(item, dict) and item.get("repository") == "ao-covenant"),
        None,
    )
    covenant_macos = next(
        (asset for asset in covenant.get("assets", []) if isinstance(asset, dict) and asset.get("platform") == "macos"),
        None,
    ) if covenant else None
    if covenant_macos and covenant_macos.get("architecture") == "amd64" and "covenant-rosetta2" not in override_ids:
        errors.append("Covenant macOS asset requires Rosetta 2")
    return errors


def _validate_policy(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for unknown in sorted(set(document) - MANIFEST_KEYS):
        errors.append(f"manifest unknown property: {unknown}")
    for missing in sorted(MANIFEST_KEYS - set(document)):
        errors.append(f"manifest missing property: {missing}")
    if document.get("schema") != "ao.architecture.development-baseline-manifest.v1":
        errors.append("manifest schema drift")
    if document.get("profile") != "stable":
        errors.append("manifest profile must be stable")
    if document.get("source_freeze_utc") != "2026-08-22T18:00:00Z":
        errors.append("manifest source freeze drift")
    if document.get("excluded_repositories") != ["ao-next"]:
        errors.append("excluded repositories must contain only ao-next")

    toolchains = document.get("toolchains")
    if not isinstance(toolchains, list):
        errors.append("toolchains must be an array")
    else:
        names = [item.get("name") for item in toolchains if isinstance(item, dict)]
        seen: set[Any] = set()
        for name in names:
            if name in seen:
                errors.append(f"duplicate toolchain: {name}")
            seen.add(name)
            if name not in EXPECTED_TOOLCHAINS:
                errors.append(f"unexpected toolchain: {name}")
        if tuple(names) != tuple(EXPECTED_TOOLCHAINS):
            errors.append("toolchains are not in canonical order")
        for index, toolchain in enumerate(toolchains):
            if not isinstance(toolchain, dict):
                errors.append(f"toolchains[{index}] must be an object")
                continue
            name = toolchain.get("name")
            label = name if isinstance(name, str) else f"toolchains[{index}]"
            for unknown in sorted(set(toolchain) - {"name", "version_argv", "constraint"}):
                errors.append(f"{label} toolchain unknown property: {unknown}")
            argv = toolchain.get("version_argv")
            if not isinstance(argv, list) or not argv or not all(
                isinstance(arg, str) and arg and len(arg) <= 64 for arg in argv
            ):
                errors.append(f"{label} toolchain version argv is invalid")
            elif any(re.search(r"[;&|><`$()]", arg) for arg in argv):
                errors.append(f"{label} toolchain version argv contains shell metacharacters")
            constraint = toolchain.get("constraint")
            if not isinstance(constraint, dict):
                errors.append(f"{label} toolchain constraint must be an object")
            else:
                for unknown in sorted(set(constraint) - {"kind", "value"}):
                    errors.append(f"{label} toolchain constraint unknown property: {unknown}")
            if name in EXPECTED_TOOLCHAINS:
                expected_argv, expected_constraint = EXPECTED_TOOLCHAINS[name]
                if argv != expected_argv:
                    errors.append(f"{name} toolchain version argv drift")
                if constraint != expected_constraint:
                    errors.append(f"{name} toolchain constraint drift")

    overrides = document.get("platform_overrides")
    if not isinstance(overrides, list):
        errors.append("platform overrides must be an array")
    else:
        ids = [item.get("id") for item in overrides if isinstance(item, dict)]
        seen_ids: set[Any] = set()
        for override_id in ids:
            if override_id in seen_ids:
                errors.append(f"duplicate platform override: {override_id}")
            seen_ids.add(override_id)
            if override_id not in EXPECTED_OVERRIDES:
                errors.append(f"undeclared platform override: {override_id}")
        if tuple(ids) != tuple(EXPECTED_OVERRIDES):
            errors.append("platform overrides are not in canonical order")
        for index, override in enumerate(overrides):
            if not isinstance(override, dict):
                errors.append(f"platform_overrides[{index}] must be an object")
                continue
            override_id = override.get("id")
            label = override_id if isinstance(override_id, str) else f"platform_overrides[{index}]"
            for unknown in sorted(set(override) - {"id", "platform", "repository", "behavior"}):
                errors.append(f"{label} platform override unknown property: {unknown}")
            if override_id in EXPECTED_OVERRIDES:
                platform, repository, behavior = EXPECTED_OVERRIDES[override_id]
                if (
                    override.get("platform"),
                    override.get("repository"),
                    override.get("behavior"),
                ) != (platform, repository, behavior):
                    errors.append(f"platform override drift: {override_id}")

    authority = document.get("authority")
    if not isinstance(authority, dict):
        errors.append("authority must be an object")
    else:
        for unknown in sorted(set(authority) - AUTHORITY_KEYS):
            errors.append(f"authority unknown property: {unknown}")
        for missing in sorted(AUTHORITY_KEYS - set(authority)):
            errors.append(f"authority missing property: {missing}")
        for field in sorted(AUTHORITY_KEYS):
            if authority.get(field) is not False:
                errors.append(f"authority must remain false: {field}")
    return errors


def validate_manifest(
    document: Any, release_input: Any, release_path: str | Path
) -> list[str]:
    """Validate the baseline manifest against its protected offline inputs."""

    if not isinstance(document, dict):
        return ["manifest must be an object"]
    errors = validate_repository_profile(document.get("repositories"))
    errors.extend(_validate_release_bindings(document, release_input, release_path))
    errors.extend(_validate_policy(document))
    return sorted(set(errors))


def _argument_parser(repository_root: Path) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify the frozen AO cross-platform development baseline."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=repository_root / "stack" / "development-baseline-manifest.json",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=(
            repository_root
            / "docs"
            / "contracts"
            / "development-baseline-manifest-v1.schema.json"
        ),
    )
    parser.add_argument(
        "--release-manifest",
        type=Path,
        default=repository_root / "stack" / "current-release-manifest.json",
    )
    parser.add_argument("--controller-commit", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    repository_root = Path(__file__).resolve().parent.parent
    args = _argument_parser(repository_root).parse_args(argv)
    if not COMMIT_PATTERN.fullmatch(args.controller_commit):
        print(
            "error=controller commit must be lowercase 40-character hex",
            file=sys.stderr,
        )
        return 2

    try:
        manifest = load_json_file(args.manifest, 1024 * 1024)
        schema = load_json_file(args.schema, 256 * 1024)
        release_input = load_json_file(args.release_manifest, 1024 * 1024)
        errors = validate_schema_contract(schema)
        errors.extend(validate_manifest(manifest, release_input, args.release_manifest))
    except InputError as exc:
        print(f"error={exc}", file=sys.stderr)
        return 1

    if errors:
        for error in errors:
            print(f"error={error}", file=sys.stderr)
        return 1

    print(f"controller_source_commit={args.controller_commit}")
    print(f"baseline_identity={identity_digest(manifest)}")
    print(f"repositories={len(manifest['repositories'])}")
    print(f"runtime_releases={len(manifest['runtime_releases'])}")
    print("errors=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
