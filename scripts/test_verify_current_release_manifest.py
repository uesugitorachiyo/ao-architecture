import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from verify_current_release_manifest import validate_manifest, validate_stack_lock_alignment

AO2_VERSION = "v0.5.10"
AO2_RELEASE_URL = "https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.10"
AO2_TAG_TARGET = "9f4f8a8cf596127a982627b4af25c90a9a842095"
AO2_MAIN_COMMIT = "9f4f8a8cf596127a982627b4af25c90a9a842095"
AO2_RELEASE_WORKFLOW_RUN = "https://github.com/uesugitorachiyo/ao2/actions/runs/31279647320"
AO2_POST_RELEASE_WORKFLOW_RUN = "https://github.com/uesugitorachiyo/ao2/actions/runs/31279647320"
AO2_CONSUMER_SMOKE_WORKFLOW_RUN = "https://github.com/uesugitorachiyo/ao2/actions/runs/31279647320"
AO2_APPROVED_MANIFEST_DIGEST = "a44bb65d59f46f3c3bf469dc7b26f0688fbf640f4f04ee9932a5a8fe186aeee3"
AO2_PROMOTION_PLAN_DIGEST = "0e1ae4663eb09c3135b66326177855cb8d93bab84d776b130114c5d2c344dd21"
AO2_PHYSICAL_WINDOWS_EVIDENCE_DIGEST = "a46f869c2c3512746ae686d65935b1612c1ef1ac0788f16bcd7de0d719268d81"
AO2_EVIDENCE_PATH = AO2_POST_RELEASE_WORKFLOW_RUN
AO2_ASSET_SHA256 = {
    "ao2-0.5.10-linux-x86_64.tar.gz": "fd1ff2aaa86e72238f8a3d3a9ab7be296aff4bc8017b3ec626b6501fe4e42318",
    "ao2-0.5.10-macos-aarch64.tar.gz": "e29122f3d330e8b84949c24f65cf50a9b6387e04d902f148897afd283b2af31b",
    "ao2-0.5.10-windows-x86_64.tar.gz": "37eb8d06a90ad705cffa51ce3d9dc9bce4f0ac162d95b4d524ffc97b8e284d33",
    "promotion-plan.json": AO2_PROMOTION_PLAN_DIGEST,
    "SHA256SUMS": "6485b289c8ec1aeaf005017313003f6b30ce165922f345b108dca31b3dd1b1af",
}
AO2_WINDOWS_SMOKE_JOB = AO2_POST_RELEASE_WORKFLOW_RUN
CONTROL_PLANE_VERSION = "v0.1.19"
CONTROL_PLANE_RELEASE_URL = "https://github.com/uesugitorachiyo/ao2-control-plane/releases/tag/v0.1.19"
CONTROL_PLANE_TAG_TARGET = "5de3541e9007e12d95b125e7f911c02932e21479"
CONTROL_PLANE_MAIN_COMMIT = "eb420864794ceb9ebadef8f3f551772095edb758"
MISSION_TAG_TARGET = "2d4d24e6eb998066b537048516c9fb0c1bbc4f2a"
MISSION_MAIN_COMMIT = "2d4d24e6eb998066b537048516c9fb0c1bbc4f2a"
MISSION_RELEASE_WORKFLOW_RUN = "https://github.com/uesugitorachiyo/ao-mission/actions/runs/31280520769"
MISSION_ASSET_SHA256 = {
    "ao-mission-0.1.3-linux-x86_64.tar.gz": "ff5f4cf3c5cd1892ae2367cfb624607e0cedea59bf4d5b01e96444b4f8fef65d",
    "ao-mission-0.1.3-macos-aarch64.tar.gz": "85031d253f12712b715d8f99560fd4237d431bec5367dee825c7928fcf2d7443",
    "ao-mission-0.1.3-windows-x86_64.zip": "2ac052285126b2737d6d846ebab730f5615ad4baef4cc1a0596dceebf86465cc",
}
COMMAND_TAG_TARGET = "a728d90077c1340e295468e5017b5e166bc5bc7a"
COMMAND_MAIN_COMMIT = "6fc2a26a0a62b4cc9d23ad039ac205f8f11fb3d9"


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
            "source_of_truth": "public GitHub releases plus AO2 v0.5.10 and Control Plane v0.1.19 publication evidence",
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
                    "version": "v0.1.3",
                    "release_url": "https://github.com/uesugitorachiyo/ao-mission/releases/tag/v0.1.3",
                    "tag": "v0.1.3",
                    "tag_target": MISSION_TAG_TARGET,
                    "current_main_commit": MISSION_MAIN_COMMIT,
                    "release_workflow_run": MISSION_RELEASE_WORKFLOW_RUN,
                    "asset_sha256": MISSION_ASSET_SHA256,
                    "is_draft": False,
                    "is_prerelease": False,
                    "asset_count": 3,
                },
                {
                    "repository": "ao-command",
                    "version": "v0.1.2",
                    "release_url": "https://github.com/uesugitorachiyo/ao-command/releases/tag/v0.1.2",
                    "tag": "v0.1.2",
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
            "source_of_truth": "public GitHub releases plus AO2 v0.5.3 and Control Plane v0.1.19 publication evidence",
            "ao2": ao2_release(),
        }
        document["ao2"].update(
            {
                "version": "v0.5.3",
                "tag": "v0.5.3",
                "release_url": "https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.3",
            }
        )
        self.assertIn("ao2.version must be v0.5.10", validate_manifest(document))

    def test_rejects_previous_ao2_v056_as_current_release(self):
        document = {"ao2": ao2_release()}
        document["ao2"].update(
            {
                "version": "v0.5.6",
                "tag": "v0.5.6",
                "release_url": "https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.6",
            }
        )
        self.assertIn("ao2.version must be v0.5.10", validate_manifest(document))

    def test_requires_exact_ao2_v059_publication_evidence(self):
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
                    "source_of_truth": "public GitHub releases plus AO2 v0.5.10 publication evidence",
                    "ao2": ao2_release(),
                }
                document["ao2"][field] = {} if isinstance(expected, dict) else "0" * len(expected)
                self.assertIn(f"ao2.{field} must match the verified v0.5.10 release", validate_manifest(document))

    def test_requires_published_tier1_tool_records(self):
        errors = validate_manifest({"tier1_tools": []})
        self.assertIn(
            "tier1_tools must contain exactly ao-command and ao-mission",
            errors,
        )

    def test_rejects_stale_mission_current_main_commit(self):
        document = {
            "tier1_tools": [
                {
                    "repository": "ao-mission",
                    "version": "v0.1.3",
                    "release_url": "https://github.com/uesugitorachiyo/ao-mission/releases/tag/v0.1.3",
                    "tag": "v0.1.3",
                    "tag_target": MISSION_TAG_TARGET,
                    "current_main_commit": "0" * 40,
                    "release_workflow_run": MISSION_RELEASE_WORKFLOW_RUN,
                    "asset_sha256": MISSION_ASSET_SHA256,
                    "is_draft": False,
                    "is_prerelease": False,
                    "asset_count": 3,
                },
                {
                    "repository": "ao-command",
                    "version": "v0.1.2",
                    "release_url": "https://github.com/uesugitorachiyo/ao-command/releases/tag/v0.1.2",
                    "tag": "v0.1.2",
                    "tag_target": COMMAND_TAG_TARGET,
                    "current_main_commit": COMMAND_MAIN_COMMIT,
                    "is_draft": False,
                    "is_prerelease": False,
                    "asset_count": 3,
                },
            ]
        }
        self.assertIn(
            "ao-mission.current_main_commit must match the verified Mission current main",
            validate_manifest(document),
        )

    def test_rejects_stale_mission_release_evidence(self):
        document = {
            "tier1_tools": [
                {
                    "repository": "ao-mission",
                    "version": "v0.1.3",
                    "release_url": "https://github.com/uesugitorachiyo/ao-mission/releases/tag/v0.1.3",
                    "tag": "v0.1.3",
                    "tag_target": MISSION_TAG_TARGET,
                    "current_main_commit": MISSION_MAIN_COMMIT,
                    "release_workflow_run": MISSION_RELEASE_WORKFLOW_RUN,
                    "asset_sha256": {},
                    "is_draft": False,
                    "is_prerelease": False,
                    "asset_count": 3,
                },
                {
                    "repository": "ao-command",
                    "version": "v0.1.2",
                    "release_url": "https://github.com/uesugitorachiyo/ao-command/releases/tag/v0.1.2",
                    "tag": "v0.1.2",
                    "tag_target": COMMAND_TAG_TARGET,
                    "current_main_commit": COMMAND_MAIN_COMMIT,
                    "is_draft": False,
                    "is_prerelease": False,
                    "asset_count": 3,
                },
            ]
        }
        self.assertIn(
            "ao-mission.asset_sha256 must match the verified v0.1.3 release",
            validate_manifest(document),
        )

    def test_rejects_negative_compatibility_evidence_counts(self):
        document = {
            "schema": "ao.architecture.current-release-manifest.v0.1",
            "status": "current_public_release_pair",
            "generated_at_utc": "2026-07-27T20:00:00Z",
            "source_of_truth": "public GitHub releases plus AO2 v0.5.10 and Control Plane v0.1.19 publication evidence",
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
            "source_of_truth": "public GitHub releases plus AO2 v0.5.10 and Control Plane v0.1.19 publication evidence",
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
                    "version": "v0.1.3",
                    "current_main_commit": MISSION_MAIN_COMMIT,
                },
                {
                    "repository": "ao-command",
                    "version": "v0.1.2",
                    "current_main_commit": COMMAND_MAIN_COMMIT,
                },
            ]
        }
        lock = {
            "repositories": [
                {
                    "repository": "ao-mission",
                    "commit": MISSION_TAG_TARGET,
                    "detected_version": "v0.1.3",
                },
                {
                    "repository": "ao-command",
                    "commit": COMMAND_TAG_TARGET,
                    "detected_version": "v0.1.1",
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
