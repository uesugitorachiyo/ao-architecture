import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from verify_current_release_manifest import validate_manifest, validate_stack_lock_alignment

AO2_VERSION = "v0.5.5"
AO2_RELEASE_URL = "https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.5"
AO2_TAG_TARGET = "dbaca8904564c4118b27a43356b7968725cd546e"
AO2_MAIN_COMMIT = "0598920c5f2712966c4ec8ae415f1bbb91e76209"
AO2_RELEASE_WORKFLOW_RUN = "https://github.com/uesugitorachiyo/ao2/actions/runs/30293757188"
AO2_POST_RELEASE_WORKFLOW_RUN = "https://github.com/uesugitorachiyo/ao2/actions/runs/30294693422"
AO2_CONSUMER_SMOKE_WORKFLOW_RUN = "https://github.com/uesugitorachiyo/ao2/actions/runs/30294695399"
AO2_APPROVED_MANIFEST_DIGEST = "8268de6f7ccf2f9a194b9123df7a3845cb4660bc10476f6da1df7a5859f48574"
AO2_PROMOTION_PLAN_DIGEST = "fc0a50b716a2e6866fb442076ec83b0a119866effe3b9ed2cbaab85b014c6c40"
AO2_PHYSICAL_WINDOWS_EVIDENCE_DIGEST = "107c49f3b0fd4921a4615b359fc4e3e7616dfdc37b8941ccf4a53ccd9242a5ab"
AO2_EVIDENCE_PATH = "ao2-doctor-v0.5.5-release-20260727T174627Z/canonical-closure-regression-20260727T191907Z/canonical-summary.json"
AO2_ASSET_SHA256 = {
    "ao2-0.5.5-linux-x86_64.tar.gz": "c34aa59f6abc9069d77e51632660a14116ebfad6a77ad8ef8e162fccaf13db95",
    "ao2-0.5.5-macos-aarch64.tar.gz": "05476d49d3036512aea4fa97ae17af96c84e99dcbb86b78500790112d9c2db3a",
    "ao2-0.5.5-windows-x86_64.tar.gz": "58374127f50d80716a222f59491070fdf5e1882f088d448ddc90cb2c2a3b8ab0",
    "promotion-plan.json": AO2_PROMOTION_PLAN_DIGEST,
    "SHA256SUMS": "152d991f0c15eb8c17996873b8849f3a2dc6d45557328f36aee32468b9423b78",
}
AO2_WINDOWS_SMOKE_JOB = AO2_RELEASE_WORKFLOW_RUN
CONTROL_PLANE_VERSION = "v0.1.18"
CONTROL_PLANE_RELEASE_URL = "https://github.com/uesugitorachiyo/ao2-control-plane/releases/tag/v0.1.18"
CONTROL_PLANE_TAG_TARGET = "6257ec23fde726d4a0133c5b62231881fb6aaa9a"
CONTROL_PLANE_MAIN_COMMIT = "78c4f70c3795da90751951fb69229d662c909a11"
MISSION_TAG_TARGET = "2901a9cb887b72296a56b70a5a3be7350b28fe65"
MISSION_MAIN_COMMIT = "c39bfd6e2b185ae1934de0e907f206e842d66bf1"
COMMAND_TAG_TARGET = "0bcadf5701fdac88f9fd792cba3a9a6686de16e5"
COMMAND_MAIN_COMMIT = "cc6e91fc8d5c5226a41517024cb8a906e5f9c902"


def ao2_release():
    return {
        "repository": "ao2",
        "version": AO2_VERSION,
        "release_url": AO2_RELEASE_URL,
        "tag": AO2_VERSION,
        "tag_target": AO2_TAG_TARGET,
        "current_main_commit": AO2_MAIN_COMMIT,
        "release_workflow_run": AO2_RELEASE_WORKFLOW_RUN,
        "post_release_workflow_run": AO2_POST_RELEASE_WORKFLOW_RUN,
        "consumer_smoke_workflow_run": AO2_CONSUMER_SMOKE_WORKFLOW_RUN,
        "is_draft": False,
        "is_prerelease": False,
        "asset_count": 5,
        "approved_manifest_digest": AO2_APPROVED_MANIFEST_DIGEST,
        "promotion_plan_digest": AO2_PROMOTION_PLAN_DIGEST,
        "physical_windows_evidence_digest": AO2_PHYSICAL_WINDOWS_EVIDENCE_DIGEST,
        "evidence_path": AO2_EVIDENCE_PATH,
        "asset_sha256": AO2_ASSET_SHA256,
        "windows_smoke_job": AO2_WINDOWS_SMOKE_JOB,
    }


class VerifyCurrentReleaseManifestTest(unittest.TestCase):
    def test_accepts_current_public_release_pair_manifest(self):
        document = {
            "schema": "ao.architecture.current-release-manifest.v0.1",
            "status": "current_public_release_pair",
            "generated_at_utc": "2026-07-27T20:00:00Z",
            "source_of_truth": "public GitHub releases plus AO2 v0.5.5 and Control Plane v0.1.18 publication evidence",
            "ao2": ao2_release(),
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
                    "current_main_commit": MISSION_MAIN_COMMIT,
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
                    "current_main_commit": COMMAND_MAIN_COMMIT,
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

    def test_rejects_stale_ao2_v053_release(self):
        document = {
            "schema": "ao.architecture.current-release-manifest.v0.1",
            "status": "current_public_release_pair",
            "generated_at_utc": "2026-07-27T20:00:00Z",
            "source_of_truth": "public GitHub releases plus AO2 v0.5.3 and Control Plane v0.1.18 publication evidence",
            "ao2": ao2_release(),
        }
        document["ao2"].update(
            {
                "version": "v0.5.3",
                "tag": "v0.5.3",
                "release_url": "https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.3",
            }
        )
        self.assertIn("ao2.version must be v0.5.5", validate_manifest(document))

    def test_requires_exact_ao2_v055_publication_evidence(self):
        exact_fields = {
            "release_url": AO2_RELEASE_URL,
            "tag_target": AO2_TAG_TARGET,
            "current_main_commit": AO2_MAIN_COMMIT,
            "release_workflow_run": AO2_RELEASE_WORKFLOW_RUN,
            "post_release_workflow_run": AO2_POST_RELEASE_WORKFLOW_RUN,
            "consumer_smoke_workflow_run": AO2_CONSUMER_SMOKE_WORKFLOW_RUN,
            "approved_manifest_digest": AO2_APPROVED_MANIFEST_DIGEST,
            "promotion_plan_digest": AO2_PROMOTION_PLAN_DIGEST,
            "physical_windows_evidence_digest": AO2_PHYSICAL_WINDOWS_EVIDENCE_DIGEST,
            "evidence_path": AO2_EVIDENCE_PATH,
            "asset_sha256": AO2_ASSET_SHA256,
            "windows_smoke_job": AO2_WINDOWS_SMOKE_JOB,
        }
        for field, expected in exact_fields.items():
            with self.subTest(field=field):
                document = {
                    "schema": "ao.architecture.current-release-manifest.v0.1",
                    "status": "current_public_release_pair",
                    "generated_at_utc": "2026-07-27T20:00:00Z",
                    "source_of_truth": "public GitHub releases plus AO2 v0.5.5 publication evidence",
                    "ao2": ao2_release(),
                }
                document["ao2"][field] = {} if isinstance(expected, dict) else "0" * len(expected)
                self.assertIn(f"ao2.{field} must match the verified v0.5.5 release", validate_manifest(document))

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
            "generated_at_utc": "2026-07-27T20:00:00Z",
            "source_of_truth": "public GitHub releases plus AO2 v0.5.5 and Control Plane v0.1.18 publication evidence",
            "ao2": ao2_release(),
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
            "generated_at_utc": "2026-07-27T20:00:00Z",
            "source_of_truth": "public GitHub releases plus AO2 v0.5.5 and Control Plane v0.1.18 publication evidence",
            "ao2": ao2_release(),
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
                    "current_main_commit": MISSION_MAIN_COMMIT,
                },
                {
                    "repository": "ao-command",
                    "version": "v0.1.1",
                    "current_main_commit": COMMAND_MAIN_COMMIT,
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
