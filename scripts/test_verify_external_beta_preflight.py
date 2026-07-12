#!/usr/bin/env python3
from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from verify_external_beta_preflight import (
    EXPECTED_REPOSITORIES,
    validate_component_readme,
    validate_manifest,
    validate_markdown_links,
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
            "architecture_helix_divergence": "preserved_excluded_from_external_beta",
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

    def test_component_readme_requires_canonical_sections_and_links(self) -> None:
        readme = """# AO Mission

## Role
Mission lifecycle.

## Maturity
Alpha. `implemented` and `executable-tested`.

## Install
`go build ./cmd/ao-mission`

## Quickstart
`ao-mission --help`

## Safety
No provider, release, or RSI authority.

## External Beta
External beta has not launched. No promotion is requested. RSI remains denied.

[AO Architecture](https://github.com/uesugitorachiyo/ao-architecture)
[Canonical component page](https://github.com/uesugitorachiyo/ao-architecture/blob/main/components/ao-mission.md)
"""
        self.assertEqual(validate_component_readme("ao-mission", readme), [])
        self.assertIn("missing section ## Safety", "\n".join(validate_component_readme("ao-mission", readme.replace("## Safety", "## Guard"))))

    def test_local_markdown_link_checker_rejects_missing_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("[missing](docs/missing.md)\n")
            self.assertIn("missing local link", "\n".join(validate_markdown_links(root)))


if __name__ == "__main__":
    unittest.main()
