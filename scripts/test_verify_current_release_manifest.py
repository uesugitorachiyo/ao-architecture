import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from verify_current_release_manifest import validate_manifest, validate_stack_lock_alignment

AO2_VERSION = "v0.5.2"
AO2_RELEASE_URL = "https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.2"
AO2_TAG_TARGET = "732a97950121321b3cfad29d86526df9c0b5fad5"
AO2_MAIN_COMMIT = "a1728338277f076f9122bff2718617193199a623"
AO2_APPROVED_MANIFEST_DIGEST = "8268de6f7ccf2f9a194b9123df7a3845cb4660bc10476f6da1df7a5859f48574"
AO2_EVIDENCE_PATH = "ao-stack-qualification-release-dsa-20260718-20260718T224504Z/publish-ao2-v052-result.json"
AO2_WINDOWS_SMOKE_JOB = "https://github.com/uesugitorachiyo/ao2/actions/runs/29690626068/job/88202569707"
CONTROL_PLANE_VERSION = "v0.1.17"
CONTROL_PLANE_RELEASE_URL = "https://github.com/uesugitorachiyo/ao2-control-plane/releases/tag/v0.1.17"
CONTROL_PLANE_TAG_TARGET = "6336801eedc4a8402d12b306b98603ce0a6fb6b5"
CONTROL_PLANE_MAIN_COMMIT = "2a2c4bfe6a65b2076e1e006639e661e14226e9d6"


class VerifyCurrentReleaseManifestTest(unittest.TestCase):
    def test_accepts_current_public_release_pair_manifest(self):
        document = {
            "schema": "ao.architecture.current-release-manifest.v0.1",
            "status": "current_public_release_pair",
            "generated_at_utc": "2026-07-15T20:10:02Z",
            "source_of_truth": "public GitHub releases plus AO2 v0.5.2 and Control Plane v0.1.17 publication evidence",
            "ao2": {
                "repository": "ao2",
                "version": AO2_VERSION,
                "release_url": AO2_RELEASE_URL,
                "tag": AO2_VERSION,
                "tag_target": AO2_TAG_TARGET,
                "current_main_commit": AO2_MAIN_COMMIT,
                "release_prep_pr": "https://github.com/uesugitorachiyo/ao2/pull/322",
                "release_prep_merge_commit": AO2_TAG_TARGET,
                "post_public_docs_pr": "https://github.com/uesugitorachiyo/ao2/pull/324",
                "post_public_docs_commit": AO2_MAIN_COMMIT,
                "is_draft": False,
                "is_prerelease": False,
                "asset_count": 23,
                "approved_manifest_digest": AO2_APPROVED_MANIFEST_DIGEST,
                "evidence_path": AO2_EVIDENCE_PATH,
                "windows_smoke_job": AO2_WINDOWS_SMOKE_JOB,
            },
            "control_plane": {
                "repository": "ao2-control-plane",
                "version": CONTROL_PLANE_VERSION,
                "release_url": CONTROL_PLANE_RELEASE_URL,
                "tag": CONTROL_PLANE_VERSION,
                "tag_target": CONTROL_PLANE_TAG_TARGET,
                "current_main_commit": CONTROL_PLANE_MAIN_COMMIT,
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
                "canonical_vector_count": 1,
                "consumer_test_count": 1,
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

    def test_rejects_negative_compatibility_evidence_counts(self):
        document = {
            "schema": "ao.architecture.current-release-manifest.v0.1",
            "status": "current_public_release_pair",
            "generated_at_utc": "2026-07-15T20:10:02Z",
            "source_of_truth": "public GitHub releases plus AO2 v0.5.2 and Control Plane v0.1.17 publication evidence",
            "ao2": {
                "repository": "ao2",
                "version": AO2_VERSION,
                "release_url": AO2_RELEASE_URL,
                "tag": AO2_VERSION,
                "tag_target": AO2_TAG_TARGET,
                "current_main_commit": AO2_MAIN_COMMIT,
                "is_draft": False,
                "is_prerelease": False,
                "asset_count": 23,
                "approved_manifest_digest": AO2_APPROVED_MANIFEST_DIGEST,
                "evidence_path": AO2_EVIDENCE_PATH,
                "windows_smoke_job": AO2_WINDOWS_SMOKE_JOB,
            },
            "control_plane": {
                "repository": "ao2-control-plane",
                "version": CONTROL_PLANE_VERSION,
                "release_url": CONTROL_PLANE_RELEASE_URL,
                "tag": CONTROL_PLANE_VERSION,
                "tag_target": CONTROL_PLANE_TAG_TARGET,
                "current_main_commit": CONTROL_PLANE_MAIN_COMMIT,
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
                "canonical_vector_count": -1,
                "consumer_test_count": -1,
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
        errors = validate_manifest(document)
        self.assertIn("pairing.canonical_vector_count must be a non-negative integer", errors)
        self.assertIn("pairing.consumer_test_count must be a non-negative integer", errors)

    def test_rejects_external_beta_launch_claim(self):
        document = {
            "schema": "ao.architecture.current-release-manifest.v0.1",
            "status": "current_public_release_pair",
            "generated_at_utc": "2026-07-15T20:10:02Z",
            "source_of_truth": "public GitHub releases plus AO2 v0.5.2 and Control Plane v0.1.17 publication evidence",
            "ao2": {
                "repository": "ao2",
                "version": AO2_VERSION,
                "release_url": AO2_RELEASE_URL,
                "tag": AO2_VERSION,
                "tag_target": AO2_TAG_TARGET,
                "current_main_commit": AO2_MAIN_COMMIT,
                "is_draft": False,
                "is_prerelease": False,
                "asset_count": 23,
                "approved_manifest_digest": AO2_APPROVED_MANIFEST_DIGEST,
                "evidence_path": AO2_EVIDENCE_PATH,
                "windows_smoke_job": AO2_WINDOWS_SMOKE_JOB,
            },
            "control_plane": {
                "repository": "ao2-control-plane",
                "version": CONTROL_PLANE_VERSION,
                "release_url": CONTROL_PLANE_RELEASE_URL,
                "tag": CONTROL_PLANE_VERSION,
                "tag_target": CONTROL_PLANE_TAG_TARGET,
                "current_main_commit": CONTROL_PLANE_MAIN_COMMIT,
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
                "version": AO2_VERSION,
                "current_main_commit": AO2_MAIN_COMMIT,
            },
            "control_plane": {
                "repository": "ao2-control-plane",
                "version": CONTROL_PLANE_VERSION,
                "current_main_commit": CONTROL_PLANE_MAIN_COMMIT,
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
                    "commit": CONTROL_PLANE_MAIN_COMMIT,
                    "detected_version": CONTROL_PLANE_VERSION,
                },
            ]
        }
        self.assertIn("ao2 stack lock version must match current release manifest", validate_stack_lock_alignment(manifest, lock))


if __name__ == "__main__":
    unittest.main()
