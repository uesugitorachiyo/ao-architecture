#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "stack" / "external-beta-tested-stack.json"
DEFAULT_READBACKS = ROOT / "docs" / "external-beta" / "readbacks"
EXPECTED_REPOSITORIES = {
    "ao-architecture", "ao-mission", "ao-blueprint", "ao-atlas", "ao-foundry",
    "ao-forge", "ao-covenant", "ao2", "ao2-control-plane", "ao-command",
    "ao-arena", "ao-crucible", "ao-sentinel", "ao-promoter",
}
CAPABILITY_LABELS = {
    "implemented", "executable-tested", "clean-room-rehearsed", "fixture-only",
    "planned", "unauthorized",
}
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
README_SECTIONS = ("Role", "Maturity", "Install", "Quickstart", "Safety", "External Beta")


def validate_manifest(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != "ao.architecture.external-beta-tested-stack.v0.1":
        errors.append("schema must be ao.architecture.external-beta-tested-stack.v0.1")
    if document.get("status") != "preflight_only":
        errors.append("status must be preflight_only")

    repositories = document.get("repositories")
    if not isinstance(repositories, list):
        errors.append("repositories must be an array")
        repositories = []
    if document.get("repository_count") != len(repositories):
        errors.append("repository_count must match repositories length")
    names: list[str] = []
    for index, entry in enumerate(repositories):
        if not isinstance(entry, dict):
            errors.append(f"repositories[{index}] must be an object")
            continue
        prefix = f"repositories[{index}]"
        name = entry.get("repository")
        names.append(name if isinstance(name, str) else "")
        for field in ("repository", "maturity", "role", "architecture_page"):
            if not isinstance(entry.get(field), str) or not entry[field]:
                errors.append(f"{prefix}.{field} is required")
        for field in ("tested_commit", "month6_evidence_commit"):
            value = entry.get(field)
            if not isinstance(value, str) or not COMMIT_RE.fullmatch(value):
                errors.append(f"{prefix}.{field} must be a 40-character lowercase commit")
        capabilities = entry.get("capabilities")
        if not isinstance(capabilities, list) or not capabilities:
            errors.append(f"{prefix}.capabilities must be a non-empty array")
        else:
            unsupported = sorted(set(capabilities) - CAPABILITY_LABELS)
            if unsupported:
                errors.append(f"{prefix} has unsupported capability: {', '.join(unsupported)}")

    actual = set(names)
    missing = sorted(EXPECTED_REPOSITORIES - actual)
    extra = sorted(actual - EXPECTED_REPOSITORIES)
    if missing:
        errors.append("missing repositories: " + ", ".join(missing))
    if extra:
        errors.append("unexpected repositories: " + ", ".join(extra))
    if len(names) != len(actual):
        errors.append("repositories must not contain duplicates")

    readiness = document.get("month6_launch_readiness")
    if not isinstance(readiness, dict):
        errors.append("month6_launch_readiness is required")
    else:
        if not COMMIT_RE.fullmatch(str(readiness.get("commit", ""))):
            errors.append("month6_launch_readiness.commit must be immutable")
        if not SHA256_RE.fullmatch(str(readiness.get("sha256", ""))):
            errors.append("month6_launch_readiness.sha256 must be a lowercase SHA-256 digest")
        if not isinstance(readiness.get("path"), str) or not readiness["path"]:
            errors.append("month6_launch_readiness.path is required")
        expected_counts = {
            "completed_nodes": 40, "ready_nodes": 0, "blocked_nodes": 0,
            "failed_nodes": 0, "final_response_allowed": True,
        }
        for field, expected in expected_counts.items():
            if readiness.get(field) != expected:
                errors.append(f"month6_launch_readiness.{field} must be {expected!r}")

    reconciliation = document.get("workspace_reconciliation")
    if not isinstance(reconciliation, dict):
        errors.append("workspace_reconciliation is required")
    else:
        if reconciliation.get("architecture_helix_divergence") != "preserved_excluded_from_external_beta":
            errors.append("architecture Helix divergence must remain preserved and excluded")
        if reconciliation.get("promoter_hardening_branch") != "preserved_excluded_use_origin_main":
            errors.append("Promoter hardening branch must remain preserved and excluded")

    safety = document.get("safety")
    if not isinstance(safety, dict):
        errors.append("safety is required")
    else:
        for field in (
            "external_beta_launched", "promotion_requested", "promotion_granted",
            "provider_calls", "release_or_publish", "authority_widened",
        ):
            if safety.get(field) is not False:
                errors.append(f"safety.{field} must be false")
        if safety.get("rsi_remains_denied") is not True:
            errors.append("safety.rsi_remains_denied must be true")
    return errors


def validate_component_readme(repository: str, text: str) -> list[str]:
    errors: list[str] = []
    for section in README_SECTIONS:
        if f"## {section}" not in text:
            errors.append(f"{repository} README missing section ## {section}")
    architecture_url = "https://github.com/uesugitorachiyo/ao-architecture"
    component_url = f"{architecture_url}/blob/main/components/{repository}.md"
    if architecture_url not in text:
        errors.append(f"{repository} README missing AO Architecture link")
    if component_url not in text:
        errors.append(f"{repository} README missing canonical component-page link")
    if "External beta has not launched" not in text:
        errors.append(f"{repository} README must state that external beta has not launched")
    if "No promotion is requested" not in text:
        errors.append(f"{repository} README must state that no promotion is requested")
    if "RSI remains denied" not in text:
        errors.append(f"{repository} README must state that RSI remains denied")
    if not any(f"`{label}`" in text for label in CAPABILITY_LABELS):
        errors.append(f"{repository} README must use an approved capability label")
    return errors


def validate_markdown_links(root: Path, paths: list[Path] | None = None) -> list[str]:
    errors: list[str] = []
    markdown_files = paths if paths is not None else sorted(root.rglob("*.md"))
    for markdown in markdown_files:
        text = markdown.read_text(errors="replace")
        for raw_target in MARKDOWN_LINK_RE.findall(text):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            relative = target.split("#", 1)[0]
            if not relative:
                continue
            resolved = (markdown.parent / relative).resolve()
            if not resolved.exists():
                errors.append(f"{markdown.relative_to(root)} has missing local link {target}")
    return errors


def validate_evidence_binding(document: dict[str, Any], workspace_root: Path) -> list[str]:
    readiness = document["month6_launch_readiness"]
    evidence = workspace_root / readiness["repository"] / readiness["path"]
    if not evidence.is_file():
        return [f"Month 6 launch-readiness evidence is missing: {evidence}"]
    digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
    if digest != readiness["sha256"]:
        return [f"Month 6 launch-readiness digest mismatch: expected {readiness['sha256']}, got {digest}"]
    payload = json.loads(evidence.read_text())
    checks = {
        "completed_recommendation_count": readiness["completed_nodes"],
        "ready_nodes": readiness["ready_nodes"],
        "blocked_nodes": readiness["blocked_nodes"],
        "failed_nodes": readiness["failed_nodes"],
        "final_response_allowed": readiness["final_response_allowed"],
        "no_promotion_requested": True,
        "rsi_remains_denied": True,
    }
    return [f"Month 6 evidence field {key} does not equal {expected!r}" for key, expected in checks.items() if payload.get(key) != expected]


def repository_head_matches(
    repository: str,
    expected: str,
    actual: str,
    architecture_ancestor_check: Any,
) -> bool:
    if actual == expected:
        return True
    return repository == "ao-architecture" and bool(architecture_ancestor_check())


def validate_repository_heads(document: dict[str, Any], workspace_root: Path) -> list[str]:
    errors: list[str] = []
    for entry in document["repositories"]:
        repository = workspace_root / entry["repository"]
        if not (repository / ".git").exists() and not (repository / "HEAD").exists():
            errors.append(f"repository checkout is missing: {repository}")
            continue
        result = subprocess.run(
            ["git", "-C", str(repository), "rev-parse", "origin/main"],
            text=True, capture_output=True, check=False,
        )
        actual = result.stdout.strip()
        ancestor = lambda: subprocess.run(
            ["git", "-C", str(repository), "merge-base", "--is-ancestor", entry["tested_commit"], actual],
            capture_output=True, check=False,
        ).returncode == 0
        if result.returncode != 0 or not repository_head_matches(
            entry["repository"], entry["tested_commit"], actual, ancestor
        ):
            errors.append(f"{entry['repository']} origin/main expected {entry['tested_commit']}, got {actual or 'unavailable'}")
    return errors


def validate_closure_readbacks(manifest_bytes: bytes, readbacks_root: Path) -> list[str]:
    digest = hashlib.sha256(manifest_bytes).hexdigest()
    expected: dict[str, dict[str, Any]] = {
        "sentinel.json": {
            "status": "clear_preflight_only",
            "public_wording_clear": True,
            "external_beta_launched": False,
            "promotion_requested": False,
            "rsi_remains_denied": True,
        },
        "promoter.json": {
            "status": "no_promotion_requested",
            "promotion_requested": False,
            "promotion_granted": False,
            "activation_authorized": False,
            "external_beta_launched": False,
            "rsi_remains_denied": True,
        },
        "command.json": {
            "status": "readback_agrees_no_promotion",
            "sentinel_status": "clear_preflight_only",
            "promoter_status": "no_promotion_requested",
            "external_beta_launched": False,
            "rsi_remains_denied": True,
        },
        "final-rollup.json": {
            "status": "preflight_documentation_ready_no_launch",
            "public_wording_clear": True,
            "promotion_requested": False,
            "promotion_granted": False,
            "external_beta_launched": False,
            "provider_calls": False,
            "release_or_publish": False,
            "rsi_remains_denied": True,
        },
    }
    errors: list[str] = []
    for name, fields in expected.items():
        path = readbacks_root / name
        try:
            document = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{name} is unreadable: {exc}")
            continue
        if document.get("tested_stack_manifest_sha256") != digest:
            errors.append(f"{name} tested_stack_manifest_sha256 does not match manifest")
        for field, value in fields.items():
            if document.get(field) != value:
                errors.append(f"{name} {field} must be {value!r}")
    return errors


def validate_component_repositories(document: dict[str, Any], workspace_root: Path) -> list[str]:
    errors: list[str] = []
    for entry in document["repositories"]:
        name = entry["repository"]
        if name == "ao-architecture":
            continue
        repository = workspace_root / name
        result = subprocess.run(
            ["git", "-C", str(repository), "show", "origin/main:README.md"],
            text=True, capture_output=True, check=False,
        )
        if result.returncode != 0:
            errors.append(f"{name} README is missing from origin/main")
            continue
        errors.extend(validate_component_readme(name, result.stdout))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify AO external-beta preflight sources")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--workspace-root", type=Path, default=ROOT.parent)
    parser.add_argument("--repository-only", action="store_true")
    args = parser.parse_args()
    try:
        document = json.loads(args.manifest.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"verify_external_beta_preflight.py: {exc}", file=sys.stderr)
        return 1
    errors = validate_manifest(document)
    if not errors:
        errors.extend(validate_markdown_links(ROOT))
        errors.extend(validate_closure_readbacks(args.manifest.read_bytes(), DEFAULT_READBACKS))
    if not errors and not args.repository_only:
        errors.extend(validate_evidence_binding(document, args.workspace_root))
        errors.extend(validate_repository_heads(document, args.workspace_root))
        errors.extend(validate_component_repositories(document, args.workspace_root))
    if errors:
        for error in errors:
            print(f"verify_external_beta_preflight.py: {error}", file=sys.stderr)
        return 1
    mode = "manifest" if args.repository_only else "workspace"
    print(f"verify_external_beta_preflight.py: {mode} preflight sources verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
