#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from verify_external_beta_preflight import (
    EXPECTED_REPOSITORIES,
    validate_closure_readbacks,
    validate_manifest,
    validate_markdown_links,
    repository_head_matches,
)


def valid_manifest() -> dict:
    repositories = []
    for name in sorted(EXPECTED_REPOSITORIES):
        repositories.append(
            {
                "repository": name,
                "tested_commit": "1" * 40,
                "month6_evidence_commit": "2" * 40,
                "maturity": "alpha",
                "capabilities": ["implemented", "executable-tested"],
                "role": f"Canonical role for {name}",
                "architecture_page": f"components/{name}.md",
            }
        )
    return {
        "schema": "ao.architecture.external-beta-tested-stack.v0.1",
        "status": "preflight_only",
        "repository_count": len(repositories),
        "repositories": repositories,
        "month6_launch_readiness": {
            "repository": "ao-atlas",
            "commit": "3" * 40,
            "path": "docs/evidence/ao-stack-month6-beta-launch-v01/nodes/month6-recommendation-40-launch-readiness-workgraph/launch-readiness-workgraph.json",
            "sha256": "4" * 64,
            "completed_nodes": 40,
            "ready_nodes": 0,
            "blocked_nodes": 0,
            "failed_nodes": 0,
            "final_response_allowed": True,
        },
        "workspace_reconciliation": {
            "promoter_hardening_branch": "preserved_excluded_use_origin_main",
        },
        "safety": {
            "external_beta_launched": False,
            "promotion_requested": False,
            "promotion_granted": False,
            "provider_calls": False,
            "release_or_publish": False,
            "authority_widened": False,
            "rsi_remains_denied": True,
        },
    }


class ExternalBetaManifestTest(unittest.TestCase):
    def test_accepts_complete_preflight_manifest(self) -> None:
        self.assertEqual(validate_manifest(valid_manifest()), [])

    def test_rejects_missing_repository(self) -> None:
        document = valid_manifest()
        document["repositories"].pop()
        document["repository_count"] -= 1
        self.assertIn("missing repositories", "\n".join(validate_manifest(document)))

    def test_rejects_unknown_capability_label(self) -> None:
        document = valid_manifest()
        document["repositories"][0]["capabilities"] = ["production-ready"]
        self.assertIn("unsupported capability", "\n".join(validate_manifest(document)))

    def test_rejects_mutable_or_missing_evidence_binding(self) -> None:
        document = valid_manifest()
        document["month6_launch_readiness"]["sha256"] = "latest"
        self.assertIn("sha256", "\n".join(validate_manifest(document)))

    def test_rejects_promotion_or_launched_beta(self) -> None:
        for field in ("external_beta_launched", "promotion_requested", "promotion_granted"):
            with self.subTest(field=field):
                document = copy.deepcopy(valid_manifest())
                document["safety"][field] = True
                self.assertIn(field, "\n".join(validate_manifest(document)))

    def test_rejects_rsi_claim(self) -> None:
        document = valid_manifest()
        document["safety"]["rsi_remains_denied"] = False
        self.assertIn("rsi_remains_denied", "\n".join(validate_manifest(document)))

    def test_local_markdown_link_checker_rejects_missing_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("[missing](docs/missing.md)\n")
            self.assertIn("missing local link", "\n".join(validate_markdown_links(root)))

    def test_architecture_head_accepts_pinned_ancestor_only(self) -> None:
        expected = "1" * 40
        actual = "2" * 40
        self.assertTrue(repository_head_matches("ao-architecture", expected, actual, lambda: True))
        self.assertFalse(repository_head_matches("ao-architecture", expected, actual, lambda: False))
        self.assertFalse(repository_head_matches("ao-mission", expected, actual, lambda: True))

    def test_closure_readbacks_bind_manifest_and_denied_authority(self) -> None:
        manifest_bytes = b'{"status":"preflight_only"}\n'
        digest = hashlib.sha256(manifest_bytes).hexdigest()
        documents = {
            "sentinel.json": {
                "status": "clear_preflight_only",
                "tested_stack_manifest_sha256": digest,
                "public_wording_clear": True,
                "external_beta_launched": False,
                "promotion_requested": False,
                "rsi_remains_denied": True,
            },
            "promoter.json": {
                "status": "no_promotion_requested",
                "tested_stack_manifest_sha256": digest,
                "promotion_requested": False,
                "promotion_granted": False,
                "activation_authorized": False,
                "external_beta_launched": False,
                "rsi_remains_denied": True,
            },
            "command.json": {
                "status": "readback_agrees_no_promotion",
                "tested_stack_manifest_sha256": digest,
                "sentinel_status": "clear_preflight_only",
                "promoter_status": "no_promotion_requested",
                "external_beta_launched": False,
                "rsi_remains_denied": True,
            },
            "final-rollup.json": {
                "status": "preflight_documentation_ready_no_launch",
                "tested_stack_manifest_sha256": digest,
                "public_wording_clear": True,
                "promotion_requested": False,
                "promotion_granted": False,
                "external_beta_launched": False,
                "provider_calls": False,
                "release_or_publish": False,
                "rsi_remains_denied": True,
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, document in documents.items():
                (root / name).write_text(json.dumps(document))
            self.assertEqual(validate_closure_readbacks(manifest_bytes, root), [])
            documents["promoter.json"]["promotion_requested"] = True
            (root / "promoter.json").write_text(json.dumps(documents["promoter.json"]))
            self.assertIn("promoter.json promotion_requested", "\n".join(validate_closure_readbacks(manifest_bytes, root)))


if __name__ == "__main__":
    unittest.main()
