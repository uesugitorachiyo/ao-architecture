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
VERIFIED_AO2_V059 = {
    "release_url": "https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.9",
    "tag_target": "fec09515dfe4e550eeaddc7da497b1fe912012b4",
    "current_main_commit": "1ea4c482ad105227a5701f6b8eafcd16c42d06e9",
    "release_workflow_run": "https://github.com/uesugitorachiyo/ao2/actions/runs/31210590627",
    "post_release_workflow_run": "https://github.com/uesugitorachiyo/ao2/actions/runs/31214323411",
    "consumer_smoke_workflow_run": "https://github.com/uesugitorachiyo/ao2/actions/runs/31214325492",
    "approved_manifest_digest": "5f82c24b239c50dadb72e2bfafe1a310b04724cfacff5acee88f5164ec3c59cd",
    "promotion_plan_digest": "4e61e689432e9eddb7885448bd7bf2a70ccb46cc8ca5103be76ec9814d09c591",
    "physical_windows_evidence_digest": "df4384874bb2f89c67fe0b5c588cfbcbb89d2e50b123595dd5d1ca4a5b38a8f0",
    "evidence_path": "https://github.com/uesugitorachiyo/ao2/actions/runs/31214323411",
    "asset_sha256": {
        "ao2-0.5.9-linux-x86_64.tar.gz": "b710ce6d5a125dce382de72376a7c7266413efd5578955a21fb5fa82ee61d4f6",
        "ao2-0.5.9-macos-aarch64.tar.gz": "2726b1da29c066fa5c16398eee8c4d679e08627b32b4e1b34d6e6f7debf4250f",
        "ao2-0.5.9-windows-x86_64.tar.gz": "14ab915d3b8adec4c26c72a30f9e0ffcc974fb7a28b0a991e4ae89b02c124cc4",
        "promotion-plan.json": "4e61e689432e9eddb7885448bd7bf2a70ccb46cc8ca5103be76ec9814d09c591",
        "SHA256SUMS": "721b83b86edb4b39b8c87a6d7f1c6beac157989e41e8bd6e30c2f8435c11ba7e",
    },
    "windows_smoke_job": "https://github.com/uesugitorachiyo/ao2/actions/runs/31214323411",
}

VERIFIED_TIER1_CURRENT_MAIN = {
    "ao-mission": "45747af3ca16e2ed596a57c8fbc25a49e78bbc6a",
    "ao-command": "6fc2a26a0a62b4cc9d23ad039ac205f8f11fb3d9",
}

VERIFIED_MISSION_V012 = {
    "release_url": "https://github.com/uesugitorachiyo/ao-mission/releases/tag/v0.1.2",
    "tag_target": "582bdb830851039846ac5f760ef5f6774e453f17",
    "current_main_commit": "45747af3ca16e2ed596a57c8fbc25a49e78bbc6a",
    "release_workflow_run": "https://github.com/uesugitorachiyo/ao-mission/actions/runs/31211864834",
    "asset_sha256": {
        "ao-mission-0.1.2-linux-x86_64.tar.gz": "948041ab395b140b46fb588356a99a9de628b0a329ebeabd15f104dd8f8f5615",
        "ao-mission-0.1.2-macos-aarch64.tar.gz": "74752b1a7e9abfdf0ca754738b9f0b7635b11318cb4e9486ee773b649637c90c",
        "ao-mission-0.1.2-windows-x86_64.tar.gz": "8e1ea30d2184a367272d432d6810bc53f0af1fedd079981cbfcb22a71e09334e",
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

    errors.extend(validate_release_component(document, "ao2", "ao2", "v0.5.9", 5))
    ao2 = document.get("ao2", {})
    if isinstance(ao2, dict):
        for field, expected in VERIFIED_AO2_V059.items():
            if ao2.get(field) != expected:
                errors.append(f"ao2.{field} must match the verified v0.5.9 release")

    errors.extend(validate_release_component(document, "control_plane", "ao2-control-plane", "v0.1.19", 7))
    control_plane = document.get("control_plane", {})
    if isinstance(control_plane, dict) and control_plane.get("new_release_required") is not False:
        errors.append("control_plane.new_release_required must be false")

    tier1_tools = document.get("tier1_tools")
    expected_tools = {
        "ao-mission": ("v0.1.2", 3),
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
                for field, expected in VERIFIED_MISSION_V012.items():
                    if entry.get(field) != expected:
                        errors.append(f"ao-mission.{field} must match the verified v0.1.2 release")

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
