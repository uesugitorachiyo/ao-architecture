import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from verify_current_release_manifest import validate_manifest, validate_stack_lock_alignment

AO2_VERSION = "v0.5.3"
AO2_RELEASE_URL = "https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.3"
AO2_TAG_TARGET = "947e566bd3f54ed902f3c14fc0c90e21a24359bc"
AO2_MAIN_COMMIT = AO2_TAG_TARGET
AO2_APPROVED_MANIFEST_DIGEST = "6f9da69f76b07dc2181f50a411a4350ec1bef0a31b006cb6a57a5fdad7c71a97"
AO2_EVIDENCE_PATH = "ao-stack-productization-adoption-month1-6-20260719T203430Z/month6/ao2-v0.5.3-public-verification-29802133424/public-verification.json"
AO2_WINDOWS_SMOKE_JOB = "https://github.com/uesugitorachiyo/ao2/actions/runs/29802133424"
CONTROL_PLANE_VERSION = "v0.1.18"
CONTROL_PLANE_RELEASE_URL = "https://github.com/uesugitorachiyo/ao2-control-plane/releases/tag/v0.1.18"
CONTROL_PLANE_TAG_TARGET = "6257ec23fde726d4a0133c5b62231881fb6aaa9a"
CONTROL_PLANE_MAIN_COMMIT = CONTROL_PLANE_TAG_TARGET
MISSION_TAG_TARGET = "2901a9cb887b72296a56b70a5a3be7350b28fe65"
COMMAND_TAG_TARGET = "0bcadf5701fdac88f9fd792cba3a9a6686de16e5"


class VerifyCurrentReleaseManifestTest(unittest.TestCase):
    def test_accepts_current_public_release_pair_manifest(self):
        document = {
            "schema": "ao.architecture.current-release-manifest.v0.1",
            "status": "current_public_release_pair",
            "generated_at_utc": "2026-07-15T20:10:02Z",
            "source_of_truth": "public GitHub releases plus AO2 v0.5.3 and Control Plane v0.1.18 publication evidence",
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
                "asset_count": 5,
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
                "asset_count": 7,
                "new_release_required": False,
            },
            "tier1_tools": [
                {
                    "repository": "ao-mission",
                    "version": "v0.1.0",
                    "release_url": "https://github.com/uesugitorachiyo/ao-mission/releases/tag/v0.1.0",
                    "tag": "v0.1.0",
                    "tag_target": MISSION_TAG_TARGET,
                    "current_main_commit": "ab1f90b3da22799e15ef2c81583b836fe3672451",
                    "is_draft": False,
                    "is_prerelease": False,
                    "asset_count": 3,
                },
                {
                    "repository": "ao-command",
                    "version": "v0.1.1",
                    "release_url": "https://github.com/uesugitorachiyo/ao-command/releases/tag/v0.1.1",
                    "tag": "v0.1.1",
                    "tag_target": COMMAND_TAG_TARGET,
                    "current_main_commit": COMMAND_TAG_TARGET,
                    "is_draft": False,
                    "is_prerelease": False,
                    "asset_count": 3,
                },
            ],
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

    def test_requires_published_tier1_tool_records(self):
        errors = validate_manifest({"tier1_tools": []})
        self.assertIn(
            "tier1_tools must contain exactly ao-command and ao-mission",
            errors,
        )

    def test_rejects_negative_compatibility_evidence_counts(self):
        document = {
            "schema": "ao.architecture.current-release-manifest.v0.1",
            "status": "current_public_release_pair",
            "generated_at_utc": "2026-07-15T20:10:02Z",
            "source_of_truth": "public GitHub releases plus AO2 v0.5.3 and Control Plane v0.1.18 publication evidence",
            "ao2": {
                "repository": "ao2",
                "version": AO2_VERSION,
                "release_url": AO2_RELEASE_URL,
                "tag": AO2_VERSION,
                "tag_target": AO2_TAG_TARGET,
                "current_main_commit": AO2_MAIN_COMMIT,
                "is_draft": False,
                "is_prerelease": False,
                "asset_count": 5,
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
                "asset_count": 7,
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
            "source_of_truth": "public GitHub releases plus AO2 v0.5.3 and Control Plane v0.1.18 publication evidence",
            "ao2": {
                "repository": "ao2",
                "version": AO2_VERSION,
                "release_url": AO2_RELEASE_URL,
                "tag": AO2_VERSION,
                "tag_target": AO2_TAG_TARGET,
                "current_main_commit": AO2_MAIN_COMMIT,
                "is_draft": False,
                "is_prerelease": False,
                "asset_count": 5,
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
                "asset_count": 7,
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

    def test_rejects_tier1_tool_stack_lock_drift(self):
        manifest = {
            "tier1_tools": [
                {
                    "repository": "ao-mission",
                    "version": "v0.1.0",
                    "current_main_commit": "ab1f90b3da22799e15ef2c81583b836fe3672451",
                },
                {
                    "repository": "ao-command",
                    "version": "v0.1.1",
                    "current_main_commit": COMMAND_TAG_TARGET,
                },
            ]
        }
        lock = {
            "repositories": [
                {
                    "repository": "ao-mission",
                    "commit": MISSION_TAG_TARGET,
                    "detected_version": "v0.1.0",
                },
                {
                    "repository": "ao-command",
                    "commit": COMMAND_TAG_TARGET,
                    "detected_version": "v0.1.0",
                },
            ]
        }
        errors = validate_stack_lock_alignment(manifest, lock)
        self.assertIn(
            "ao-command stack lock version must match current release manifest",
            errors,
        )


if __name__ == "__main__":
    unittest.main()
