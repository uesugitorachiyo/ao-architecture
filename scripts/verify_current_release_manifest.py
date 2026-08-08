#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "stack" / "current-release-manifest.json"
DEFAULT_LOCK = ROOT / "stack" / "ao-stack.lock.json"
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
VERIFIED_AO2_V0510 = {
    "release_url": "https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.10",
    "tag_target": "9f4f8a8cf596127a982627b4af25c90a9a842095",
    "current_main_commit": "9f4f8a8cf596127a982627b4af25c90a9a842095",
    "release_workflow_run": "https://github.com/uesugitorachiyo/ao2/actions/runs/31279647320",
    "post_release_workflow_run": "https://github.com/uesugitorachiyo/ao2/actions/runs/31279647320",
    "consumer_smoke_workflow_run": "https://github.com/uesugitorachiyo/ao2/actions/runs/31279647320",
    "approved_manifest_digest": "a44bb65d59f46f3c3bf469dc7b26f0688fbf640f4f04ee9932a5a8fe186aeee3",
    "promotion_plan_digest": "0e1ae4663eb09c3135b66326177855cb8d93bab84d776b130114c5d2c344dd21",
    "physical_windows_evidence_digest": "a46f869c2c3512746ae686d65935b1612c1ef1ac0788f16bcd7de0d719268d81",
    "evidence_path": "https://github.com/uesugitorachiyo/ao2/actions/runs/31279647320",
    "asset_sha256": {
        "ao2-0.5.10-linux-x86_64.tar.gz": "fd1ff2aaa86e72238f8a3d3a9ab7be296aff4bc8017b3ec626b6501fe4e42318",
        "ao2-0.5.10-macos-aarch64.tar.gz": "e29122f3d330e8b84949c24f65cf50a9b6387e04d902f148897afd283b2af31b",
        "ao2-0.5.10-windows-x86_64.tar.gz": "37eb8d06a90ad705cffa51ce3d9dc9bce4f0ac162d95b4d524ffc97b8e284d33",
        "promotion-plan.json": "0e1ae4663eb09c3135b66326177855cb8d93bab84d776b130114c5d2c344dd21",
        "SHA256SUMS": "6485b289c8ec1aeaf005017313003f6b30ce165922f345b108dca31b3dd1b1af",
    },
    "windows_smoke_job": "https://github.com/uesugitorachiyo/ao2/actions/runs/31279647320",
}

VERIFIED_TIER1_CURRENT_MAIN = {
    "ao-mission": "2d4d24e6eb998066b537048516c9fb0c1bbc4f2a",
    "ao-command": "6fc2a26a0a62b4cc9d23ad039ac205f8f11fb3d9",
}

VERIFIED_MISSION_V013 = {
    "release_url": "https://github.com/uesugitorachiyo/ao-mission/releases/tag/v0.1.3",
    "tag_target": "2d4d24e6eb998066b537048516c9fb0c1bbc4f2a",
    "current_main_commit": "2d4d24e6eb998066b537048516c9fb0c1bbc4f2a",
    "release_workflow_run": "https://github.com/uesugitorachiyo/ao-mission/actions/runs/31280520769",
    "asset_sha256": {
        "ao-mission-0.1.3-linux-x86_64.tar.gz": "ff5f4cf3c5cd1892ae2367cfb624607e0cedea59bf4d5b01e96444b4f8fef65d",
        "ao-mission-0.1.3-macos-aarch64.tar.gz": "85031d253f12712b715d8f99560fd4237d431bec5367dee825c7928fcf2d7443",
        "ao-mission-0.1.3-windows-x86_64.zip": "2ac052285126b2737d6d846ebab730f5615ad4baef4cc1a0596dceebf86465cc",
    },
}


def require_string(errors: list[str], obj: dict[str, Any], field: str, prefix: str) -> str:
    value = obj.get(field)
    if not isinstance(value, str) or not value:
        errors.append(f"{prefix}.{field} is required")
        return ""
    return value


def validate_release_component(
    document: dict[str, Any],
    component: str,
    expected_repository: str,
    expected_version: str,
    expected_asset_count: int,
) -> list[str]:
    errors: list[str] = []
    entry = document.get(component)
    if not isinstance(entry, dict):
        return [f"{component} is required"]
    prefix = component
    if entry.get("repository") != expected_repository:
        errors.append(f"{prefix}.repository must be {expected_repository}")
    if entry.get("version") != expected_version:
        errors.append(f"{prefix}.version must be {expected_version}")
    release_url = require_string(errors, entry, "release_url", prefix)
    if release_url and not release_url.startswith("https://github.com/uesugitorachiyo/"):
        errors.append(f"{prefix}.release_url must point to the public GitHub release")
    tag = require_string(errors, entry, "tag", prefix)
    if tag and tag != expected_version:
        errors.append(f"{prefix}.tag must match {expected_version}")
    tag_target = require_string(errors, entry, "tag_target", prefix)
    if tag_target and not COMMIT_RE.fullmatch(tag_target):
        errors.append(f"{prefix}.tag_target must be a 40-character lowercase hexadecimal commit")
    current_main_commit = require_string(errors, entry, "current_main_commit", prefix)
    if current_main_commit and not COMMIT_RE.fullmatch(current_main_commit):
        errors.append(f"{prefix}.current_main_commit must be a 40-character lowercase hexadecimal commit")
    if entry.get("is_draft") is not False:
        errors.append(f"{prefix}.is_draft must be false")
    if entry.get("is_prerelease") is not False:
        errors.append(f"{prefix}.is_prerelease must be false")
    if entry.get("asset_count") != expected_asset_count:
        errors.append(f"{prefix}.asset_count must be {expected_asset_count}")
    return errors


def validate_manifest(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != "ao.architecture.current-release-manifest.v0.1":
        errors.append("schema must be ao.architecture.current-release-manifest.v0.1")
    if document.get("status") != "current_public_release_pair":
        errors.append("status must be current_public_release_pair")
    require_string(errors, document, "generated_at_utc", "manifest")
    source = require_string(errors, document, "source_of_truth", "manifest")
    if source and "public GitHub releases" not in source:
        errors.append("source_of_truth must reference public GitHub releases")

    errors.extend(validate_release_component(document, "ao2", "ao2", "v0.5.10", 5))
    ao2 = document.get("ao2", {})
    if isinstance(ao2, dict):
        for field, expected in VERIFIED_AO2_V0510.items():
            if ao2.get(field) != expected:
                errors.append(f"ao2.{field} must match the verified v0.5.10 release")

    errors.extend(validate_release_component(document, "control_plane", "ao2-control-plane", "v0.1.19", 7))
    control_plane = document.get("control_plane", {})
    if isinstance(control_plane, dict) and control_plane.get("new_release_required") is not False:
        errors.append("control_plane.new_release_required must be false")

    tier1_tools = document.get("tier1_tools")
    expected_tools = {
        "ao-mission": ("v0.1.3", 3),
        "ao-command": ("v0.1.2", 3),
    }
    if not isinstance(tier1_tools, list):
        errors.append("tier1_tools must be an array")
    else:
        by_repository = {
            entry.get("repository"): entry
            for entry in tier1_tools
            if isinstance(entry, dict) and isinstance(entry.get("repository"), str)
        }
        if set(by_repository) != set(expected_tools) or len(tier1_tools) != len(expected_tools):
            errors.append("tier1_tools must contain exactly ao-command and ao-mission")
        for repository, (version, asset_count) in expected_tools.items():
            entry = by_repository.get(repository)
            if entry is None:
                continue
            errors.extend(
                validate_release_component(
                    {"tier1_tool": entry},
                    "tier1_tool",
                    repository,
                    version,
                    asset_count,
                )
            )
            if entry.get("current_main_commit") != VERIFIED_TIER1_CURRENT_MAIN[repository]:
                errors.append(f"{repository}.current_main_commit must match the verified {repository.removeprefix('ao-').title()} current main")
            if repository == "ao-mission":
                for field, expected in VERIFIED_MISSION_V013.items():
                    if entry.get(field) != expected:
                        errors.append(f"ao-mission.{field} must match the verified v0.1.3 release")

    pairing = document.get("pairing")
    if not isinstance(pairing, dict):
        errors.append("pairing is required")
    else:
        if pairing.get("status") != "current_public_release_pair":
            errors.append("pairing.status must be current_public_release_pair")
        if pairing.get("control_plane_update_required") is not False:
            errors.append("pairing.control_plane_update_required must be false")
        if pairing.get("full_stack_compatibility_complete") is not False:
            errors.append("pairing.full_stack_compatibility_complete must remain false")
        if pairing.get("compatibility_matrix_status") != "proposed":
            errors.append("pairing.compatibility_matrix_status must remain proposed")
        canonical_vector_count = pairing.get("canonical_vector_count")
        consumer_test_count = pairing.get("consumer_test_count")
        if not isinstance(canonical_vector_count, int) or canonical_vector_count < 0:
            errors.append("pairing.canonical_vector_count must be a non-negative integer")
        if not isinstance(consumer_test_count, int) or consumer_test_count < 0:
            errors.append("pairing.consumer_test_count must be a non-negative integer")

    boundaries = document.get("boundaries")
    if not isinstance(boundaries, dict):
        errors.append("boundaries is required")
    else:
        for field in (
            "external_beta_launched",
            "promotion_requested",
            "promotion_granted",
            "provider_pilot",
            "architecture_task_release_or_publish",
        ):
            if boundaries.get(field) is not False:
                errors.append(f"{field} must remain false")
        if boundaries.get("rsi_remains_denied") is not True:
            errors.append("rsi_remains_denied must remain true")
    return errors


def validate_stack_lock_alignment(document: dict[str, Any], lock: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    repositories = lock.get("repositories")
    if not isinstance(repositories, list):
        return ["stack lock repositories must be an array"]
    lock_by_name = {
        entry.get("repository"): entry
        for entry in repositories
        if isinstance(entry, dict) and isinstance(entry.get("repository"), str)
    }
    checks = (
        ("ao2", "ao2"),
        ("control_plane", "ao2-control-plane"),
    )
    for manifest_key, repository_name in checks:
        manifest_entry = document.get(manifest_key)
        lock_entry = lock_by_name.get(repository_name)
        if not isinstance(manifest_entry, dict):
            errors.append(f"{manifest_key} manifest entry is required for stack lock alignment")
            continue
        if not isinstance(lock_entry, dict):
            errors.append(f"{repository_name} stack lock entry is required")
            continue
        if lock_entry.get("detected_version") != manifest_entry.get("version"):
            errors.append(f"{repository_name} stack lock version must match current release manifest")
        if lock_entry.get("commit") != manifest_entry.get("current_main_commit"):
            errors.append(f"{repository_name} stack lock commit must match current main commit")
    tier1_tools = document.get("tier1_tools")
    if isinstance(tier1_tools, list):
        for manifest_entry in tier1_tools:
            if not isinstance(manifest_entry, dict):
                continue
            repository_name = manifest_entry.get("repository")
            if not isinstance(repository_name, str):
                continue
            lock_entry = lock_by_name.get(repository_name)
            if not isinstance(lock_entry, dict):
                errors.append(f"{repository_name} stack lock entry is required")
                continue
            if lock_entry.get("detected_version") != manifest_entry.get("version"):
                errors.append(f"{repository_name} stack lock version must match current release manifest")
            if lock_entry.get("commit") != manifest_entry.get("current_main_commit"):
                errors.append(f"{repository_name} stack lock commit must match current main commit")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AO current public release manifest")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    args = parser.parse_args()
    try:
        document = json.loads(args.manifest.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"verify_current_release_manifest.py: {exc}", file=sys.stderr)
        return 1
    errors = validate_manifest(document)
    try:
        lock = json.loads(args.lock.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"verify_current_release_manifest.py: {exc}", file=sys.stderr)
        return 1
    errors.extend(validate_stack_lock_alignment(document, lock))
    if errors:
        for error in errors:
            print(f"verify_current_release_manifest.py: {error}", file=sys.stderr)
        return 1
    print("verify_current_release_manifest.py: current public release pair verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
