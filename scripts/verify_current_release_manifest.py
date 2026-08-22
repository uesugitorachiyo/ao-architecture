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
VERIFIED_AO2_V0511 = {
    "release_url": "https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.11",
    "tag_target": "8307795b3434af920f6cef088e56ca8fcc76775b",
    "current_main_commit": "8307795b3434af920f6cef088e56ca8fcc76775b",
    "release_workflow_run": "https://github.com/uesugitorachiyo/ao2/actions/runs/31619411288",
    "post_release_workflow_run": "https://github.com/uesugitorachiyo/ao2/actions/runs/31622142672",
    "consumer_smoke_workflow_run": "https://github.com/uesugitorachiyo/ao2/actions/runs/31622142672",
    "approved_manifest_digest": "bc4ee1eeb8d920a0633bc6c9bd2b5f8bc5d210f80a9b4f2f10afbe68c377bf46",
    "promotion_plan_digest": "bc4ee1eeb8d920a0633bc6c9bd2b5f8bc5d210f80a9b4f2f10afbe68c377bf46",
    "physical_windows_evidence_digest": "d2c05bb81a9d19ffe51e1a1c35e3e44073a5f464d31d1dc1c20f4163d9c5d37d",
    "evidence_path": "https://github.com/uesugitorachiyo/ao2/actions/runs/31622142672",
    "asset_sha256": {
        "ao2-0.5.11-linux-x86_64.tar.gz": "c62c204d520bf51b4c63caecf2a8f48840e44b2828e1e439c68da4994d1abc07",
        "ao2-0.5.11-macos-aarch64.tar.gz": "857fbe69e606ab99f07dffd3183e6f2d869b8efd4fc604e37efd16607308e6ab",
        "ao2-0.5.11-windows-x86_64.tar.gz": "327829e9e3e3edf3eeb3b48d3b1ead46af0fa47a768ee6e1843c285e8b1d2756",
        "promotion-plan.json": "bc4ee1eeb8d920a0633bc6c9bd2b5f8bc5d210f80a9b4f2f10afbe68c377bf46",
        "SHA256SUMS": "abf0290702cd20b3c971a51e9d6ee16ecc2d4327b692d4ba7447afddc96bc4f2",
    },
    "windows_smoke_job": "https://github.com/uesugitorachiyo/ao2/actions/runs/31622142672",
}

VERIFIED_TIER1_CURRENT_MAIN = {
    "ao-mission": "5d4562578a4751d56910ef108b930fbb8dc91e7d",
    "ao-command": "ffef6d76306e892c3e7a7f39734433d5a832006a",
}

VERIFIED_MISSION_V015 = {
    "release_url": "https://github.com/uesugitorachiyo/ao-mission/releases/tag/v0.1.5",
    "tag_target": "5d4562578a4751d56910ef108b930fbb8dc91e7d",
    "current_main_commit": "5d4562578a4751d56910ef108b930fbb8dc91e7d",
    "release_workflow_run": "https://github.com/uesugitorachiyo/ao-mission/actions/runs/32532729277",
    "asset_sha256": {
        "ao-mission-0.1.5-linux-x86_64.tar.gz": "5aed0659e94c35fc1808b16d092c18e5f782f217170844335bedc59337ac3b25",
        "ao-mission-0.1.5-macos-aarch64.tar.gz": "54ea5fafac4a65fc1bad6c2d8ec079b084c528aee3fe228692d9cc154ff2d037",
        "ao-mission-0.1.5-windows-x86_64.zip": "c868653395e0ab19d2c95cc0adbb1e8d97bb5ef0002390040748a7f381cb9a43",
    },
}

VERIFIED_TIER2_RELEASES = {
    "ao-atlas": ("v0.2.1", "3603a2bb8af5adafcd9ff17b807ab89f32283d18", 15),
    "ao-forge": ("v0.1.5", "d1723769949269dcd0589916d83769dcb7275f98", 16),
    "ao-covenant": ("v0.1.1", "2fd72a0426a747868826581612fa1dc9727b53b9", 13),
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

    errors.extend(validate_release_component(document, "ao2", "ao2", "v0.5.11", 5))
    ao2 = document.get("ao2", {})
    if isinstance(ao2, dict):
        for field, expected in VERIFIED_AO2_V0511.items():
            if ao2.get(field) != expected:
                errors.append(f"ao2.{field} must match the verified v0.5.11 release")

    errors.extend(validate_release_component(document, "control_plane", "ao2-control-plane", "v0.1.19", 7))
    control_plane = document.get("control_plane", {})
    if isinstance(control_plane, dict) and control_plane.get("new_release_required") is not False:
        errors.append("control_plane.new_release_required must be false")

    tier1_tools = document.get("tier1_tools")
    expected_tools = {
        "ao-mission": ("v0.1.5", 3),
        "ao-command": ("v0.1.3", 3),
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
                for field, expected in VERIFIED_MISSION_V015.items():
                    if entry.get(field) != expected:
                        errors.append(f"ao-mission.{field} must match the verified v0.1.5 release")

    tier2_tools = document.get("tier2_tools")
    if not isinstance(tier2_tools, list):
        errors.append("tier2_tools must be an array")
    else:
        by_repository = {
            entry.get("repository"): entry
            for entry in tier2_tools
            if isinstance(entry, dict) and isinstance(entry.get("repository"), str)
        }
        if set(by_repository) != set(VERIFIED_TIER2_RELEASES) or len(tier2_tools) != len(VERIFIED_TIER2_RELEASES):
            errors.append("tier2_tools must contain exactly ao-atlas, ao-covenant, and ao-forge")
        for repository, (version, tag_target, asset_count) in VERIFIED_TIER2_RELEASES.items():
            entry = by_repository.get(repository)
            if entry is None:
                continue
            errors.extend(
                validate_release_component(
                    {"tier2_tool": entry}, "tier2_tool", repository, version, asset_count
                )
            )
            if entry.get("tag_target") != tag_target:
                errors.append(f"{repository}.tag_target must match the verified {version} release")

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
