import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from verify_current_release_manifest import validate_manifest, validate_stack_lock_alignment


class VerifyCurrentReleaseManifestTest(unittest.TestCase):
    def test_accepts_current_public_release_pair_manifest(self):
        document = {
            "schema": "ao.architecture.current-release-manifest.v0.1",
            "status": "current_public_release_pair",
            "generated_at_utc": "2026-07-15T20:10:02Z",
            "source_of_truth": "public GitHub releases plus AO2 v0.5.1 publication evidence",
            "ao2": {
                "repository": "ao2",
                "version": "v0.5.1",
                "release_url": "https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.1",
                "tag": "v0.5.1",
                "tag_target": "80ec5321f42d4bab17d5e64fdae6aa099ba59d4a",
                "current_main_commit": "d56d62199bac36800d55e426ac2049e1e21bdd7c",
                "release_prep_pr": "https://github.com/uesugitorachiyo/ao2/pull/286",
                "release_prep_merge_commit": "80ec5321f42d4bab17d5e64fdae6aa099ba59d4a",
                "post_public_docs_pr": "https://github.com/uesugitorachiyo/ao2/pull/287",
                "post_public_docs_commit": "d56d62199bac36800d55e426ac2049e1e21bdd7c",
                "is_draft": False,
                "is_prerelease": False,
                "asset_count": 23,
                "approved_manifest_digest": "bd8103e7a038f47e1b4fef1a2a19ae65cc221675ea11149d39cfb679ae2a08fc",
                "evidence_path": "ao2-v0.5.1-stable-patch-release-20260715T174801Z/final-report.md",
                "windows_smoke_job": "https://github.com/uesugitorachiyo/ao2/actions/runs/29445275460/job/87454080941",
            },
            "control_plane": {
                "repository": "ao2-control-plane",
                "version": "v0.1.15",
                "release_url": "https://github.com/uesugitorachiyo/ao2-control-plane/releases/tag/v0.1.15",
                "tag": "v0.1.15",
                "tag_target": "f1702b387607566cac457458af9adb5871a5c412",
                "current_main_commit": "a000cf9948ee1c43a4835c0bac48d12106de56bf",
                "is_draft": False,
                "is_prerelease": False,
                "asset_count": 6,
                "new_release_required": False,
            },
            "pairing": {
                "status": "current_public_release_pair",
                "control_plane_update_required": False,
                "full_stack_compatibility_complete": False,
                "compatibility_matrix_status": "proposed",
                "canonical_vector_count": 0,
                "consumer_test_count": 0,
            },
            "boundaries": {
                "external_beta_launched": False,
                "promotion_requested": False,
                "promotion_granted": False,
                "provider_pilot": False,
                "rsi_remains_denied": True,
                "architecture_task_release_or_publish": False,
            },
        }
        self.assertEqual(validate_manifest(document), [])

    def test_rejects_external_beta_launch_claim(self):
        document = {
            "schema": "ao.architecture.current-release-manifest.v0.1",
            "status": "current_public_release_pair",
            "generated_at_utc": "2026-07-15T20:10:02Z",
            "source_of_truth": "public GitHub releases plus AO2 v0.5.1 publication evidence",
            "ao2": {
                "repository": "ao2",
                "version": "v0.5.1",
                "release_url": "https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.1",
                "tag": "v0.5.1",
                "tag_target": "80ec5321f42d4bab17d5e64fdae6aa099ba59d4a",
                "current_main_commit": "d56d62199bac36800d55e426ac2049e1e21bdd7c",
                "is_draft": False,
                "is_prerelease": False,
                "asset_count": 23,
                "approved_manifest_digest": "bd8103e7a038f47e1b4fef1a2a19ae65cc221675ea11149d39cfb679ae2a08fc",
                "evidence_path": "ao2-v0.5.1-stable-patch-release-20260715T174801Z/final-report.md",
                "windows_smoke_job": "https://github.com/uesugitorachiyo/ao2/actions/runs/29445275460/job/87454080941",
            },
            "control_plane": {
                "repository": "ao2-control-plane",
                "version": "v0.1.15",
                "release_url": "https://github.com/uesugitorachiyo/ao2-control-plane/releases/tag/v0.1.15",
                "tag": "v0.1.15",
                "tag_target": "f1702b387607566cac457458af9adb5871a5c412",
                "current_main_commit": "a000cf9948ee1c43a4835c0bac48d12106de56bf",
                "is_draft": False,
                "is_prerelease": False,
                "asset_count": 6,
                "new_release_required": False,
            },
            "pairing": {
                "status": "current_public_release_pair",
                "control_plane_update_required": False,
                "full_stack_compatibility_complete": False,
                "compatibility_matrix_status": "proposed",
                "canonical_vector_count": 0,
                "consumer_test_count": 0,
            },
            "boundaries": {
                "external_beta_launched": True,
                "promotion_requested": False,
                "promotion_granted": False,
                "provider_pilot": False,
                "rsi_remains_denied": True,
                "architecture_task_release_or_publish": False,
            },
        }
        self.assertIn("external_beta_launched must remain false", validate_manifest(document))

    def test_rejects_stack_lock_release_drift(self):
        manifest = {
            "ao2": {
                "repository": "ao2",
                "version": "v0.5.1",
                "current_main_commit": "d56d62199bac36800d55e426ac2049e1e21bdd7c",
            },
            "control_plane": {
                "repository": "ao2-control-plane",
                "version": "v0.1.15",
                "current_main_commit": "a000cf9948ee1c43a4835c0bac48d12106de56bf",
            },
        }
        lock = {
            "repositories": [
                {
                    "repository": "ao2",
                    "commit": "541e766b5da00b65fa2c2e34b1d7ff0dc363eef6",
                    "detected_version": "v0.4.81",
                },
                {
                    "repository": "ao2-control-plane",
                    "commit": "a000cf9948ee1c43a4835c0bac48d12106de56bf",
                    "detected_version": "v0.1.15",
                },
            ]
        }
        self.assertIn("ao2 stack lock version must match current release manifest", validate_stack_lock_alignment(manifest, lock))


if __name__ == "__main__":
    unittest.main()
