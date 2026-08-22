import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from verify_current_release_manifest import validate_manifest, validate_stack_lock_alignment

AO2_VERSION = "v0.5.11"
AO2_RELEASE_URL = "https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.11"
AO2_TAG_TARGET = "8307795b3434af920f6cef088e56ca8fcc76775b"
AO2_MAIN_COMMIT = "8307795b3434af920f6cef088e56ca8fcc76775b"
AO2_RELEASE_WORKFLOW_RUN = "https://github.com/uesugitorachiyo/ao2/actions/runs/31619411288"
AO2_POST_RELEASE_WORKFLOW_RUN = "https://github.com/uesugitorachiyo/ao2/actions/runs/31622142672"
AO2_CONSUMER_SMOKE_WORKFLOW_RUN = AO2_POST_RELEASE_WORKFLOW_RUN
AO2_APPROVED_MANIFEST_DIGEST = "bc4ee1eeb8d920a0633bc6c9bd2b5f8bc5d210f80a9b4f2f10afbe68c377bf46"
AO2_PROMOTION_PLAN_DIGEST = AO2_APPROVED_MANIFEST_DIGEST
AO2_PHYSICAL_WINDOWS_EVIDENCE_DIGEST = "d2c05bb81a9d19ffe51e1a1c35e3e44073a5f464d31d1dc1c20f4163d9c5d37d"
AO2_EVIDENCE_PATH = AO2_POST_RELEASE_WORKFLOW_RUN
AO2_ASSET_SHA256 = {
    "ao2-0.5.11-linux-x86_64.tar.gz": "c62c204d520bf51b4c63caecf2a8f48840e44b2828e1e439c68da4994d1abc07",
    "ao2-0.5.11-macos-aarch64.tar.gz": "857fbe69e606ab99f07dffd3183e6f2d869b8efd4fc604e37efd16607308e6ab",
    "ao2-0.5.11-windows-x86_64.tar.gz": "327829e9e3e3edf3eeb3b48d3b1ead46af0fa47a768ee6e1843c285e8b1d2756",
    "promotion-plan.json": AO2_PROMOTION_PLAN_DIGEST,
    "SHA256SUMS": "abf0290702cd20b3c971a51e9d6ee16ecc2d4327b692d4ba7447afddc96bc4f2",
}
AO2_WINDOWS_SMOKE_JOB = AO2_POST_RELEASE_WORKFLOW_RUN
CONTROL_PLANE_VERSION = "v0.1.19"
CONTROL_PLANE_RELEASE_URL = "https://github.com/uesugitorachiyo/ao2-control-plane/releases/tag/v0.1.19"
CONTROL_PLANE_TAG_TARGET = "5de3541e9007e12d95b125e7f911c02932e21479"
CONTROL_PLANE_MAIN_COMMIT = "eb420864794ceb9ebadef8f3f551772095edb758"
MISSION_TAG_TARGET = "5d4562578a4751d56910ef108b930fbb8dc91e7d"
MISSION_MAIN_COMMIT = MISSION_TAG_TARGET
MISSION_RELEASE_WORKFLOW_RUN = "https://github.com/uesugitorachiyo/ao-mission/actions/runs/32532729277"
MISSION_ASSET_SHA256 = {
    "ao-mission-0.1.5-linux-x86_64.tar.gz": "5aed0659e94c35fc1808b16d092c18e5f782f217170844335bedc59337ac3b25",
    "ao-mission-0.1.5-macos-aarch64.tar.gz": "54ea5fafac4a65fc1bad6c2d8ec079b084c528aee3fe228692d9cc154ff2d037",
    "ao-mission-0.1.5-windows-x86_64.zip": "c868653395e0ab19d2c95cc0adbb1e8d97bb5ef0002390040748a7f381cb9a43",
}
COMMAND_TAG_TARGET = "ffef6d76306e892c3e7a7f39734433d5a832006a"
COMMAND_MAIN_COMMIT = "ffef6d76306e892c3e7a7f39734433d5a832006a"
ATLAS_TAG_TARGET = "3603a2bb8af5adafcd9ff17b807ab89f32283d18"
FORGE_TAG_TARGET = "d1723769949269dcd0589916d83769dcb7275f98"
COVENANT_TAG_TARGET = "2fd72a0426a747868826581612fa1dc9727b53b9"


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
            "source_of_truth": "public GitHub releases plus AO2 v0.5.11 and Control Plane v0.1.19 publication evidence",
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
                    "version": "v0.1.5",
                    "release_url": "https://github.com/uesugitorachiyo/ao-mission/releases/tag/v0.1.5",
                    "tag": "v0.1.5",
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
                    "version": "v0.1.3",
                    "release_url": "https://github.com/uesugitorachiyo/ao-command/releases/tag/v0.1.3",
                    "tag": "v0.1.3",
                    "tag_target": COMMAND_TAG_TARGET,
                    "current_main_commit": COMMAND_MAIN_COMMIT,
                    "is_draft": False,
                    "is_prerelease": False,
                    "asset_count": 3,
                },
            ],
            "tier2_tools": [
                {
                    "repository": "ao-atlas", "version": "v0.2.1",
                    "release_url": "https://github.com/uesugitorachiyo/ao-atlas/releases/tag/v0.2.1",
                    "tag": "v0.2.1", "tag_target": ATLAS_TAG_TARGET,
                    "current_main_commit": ATLAS_TAG_TARGET, "is_draft": False,
                    "is_prerelease": False, "asset_count": 15,
                },
                {
                    "repository": "ao-forge", "version": "v0.1.5",
                    "release_url": "https://github.com/uesugitorachiyo/ao-forge/releases/tag/v0.1.5",
                    "tag": "v0.1.5", "tag_target": FORGE_TAG_TARGET,
                    "current_main_commit": FORGE_TAG_TARGET, "is_draft": False,
                    "is_prerelease": False, "asset_count": 16,
                },
                {
                    "repository": "ao-covenant", "version": "v0.1.1",
                    "release_url": "https://github.com/uesugitorachiyo/ao-covenant/releases/tag/v0.1.1",
                    "tag": "v0.1.1", "tag_target": COVENANT_TAG_TARGET,
                    "current_main_commit": COVENANT_TAG_TARGET, "is_draft": False,
                    "is_prerelease": False, "asset_count": 13,
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
        self.assertIn("ao2.version must be v0.5.11", validate_manifest(document))

    def test_rejects_previous_ao2_v056_as_current_release(self):
        document = {"ao2": ao2_release()}
        document["ao2"].update(
            {
                "version": "v0.5.6",
                "tag": "v0.5.6",
                "release_url": "https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.6",
            }
        )
        self.assertIn("ao2.version must be v0.5.11", validate_manifest(document))

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
                    "source_of_truth": "public GitHub releases plus AO2 v0.5.11 publication evidence",
                    "ao2": ao2_release(),
                }
                document["ao2"][field] = {} if isinstance(expected, dict) else "0" * len(expected)
                self.assertIn(f"ao2.{field} must match the verified v0.5.11 release", validate_manifest(document))

    def test_requires_published_tier1_tool_records(self):
        errors = validate_manifest({"tier1_tools": []})
        self.assertIn(
            "tier1_tools must contain exactly ao-command and ao-mission",
            errors,
        )

    def test_requires_published_tier2_tool_records(self):
        self.assertIn(
            "tier2_tools must contain exactly ao-atlas, ao-covenant, and ao-forge",
            validate_manifest({"tier2_tools": []}),
        )

    def test_rejects_stale_mission_current_main_commit(self):
        document = {
            "tier1_tools": [
                {
                    "repository": "ao-mission",
                    "version": "v0.1.5",
                    "release_url": "https://github.com/uesugitorachiyo/ao-mission/releases/tag/v0.1.5",
                    "tag": "v0.1.5",
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
                    "version": "v0.1.3",
                    "release_url": "https://github.com/uesugitorachiyo/ao-command/releases/tag/v0.1.3",
                    "tag": "v0.1.3",
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
                    "version": "v0.1.5",
                    "release_url": "https://github.com/uesugitorachiyo/ao-mission/releases/tag/v0.1.5",
                    "tag": "v0.1.5",
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
                    "version": "v0.1.3",
                    "release_url": "https://github.com/uesugitorachiyo/ao-command/releases/tag/v0.1.3",
                    "tag": "v0.1.3",
                    "tag_target": COMMAND_TAG_TARGET,
                    "current_main_commit": COMMAND_MAIN_COMMIT,
                    "is_draft": False,
                    "is_prerelease": False,
                    "asset_count": 3,
                },
            ]
        }
        self.assertIn(
            "ao-mission.asset_sha256 must match the verified v0.1.5 release",
            validate_manifest(document),
        )

    def test_rejects_negative_compatibility_evidence_counts(self):
        document = {
            "schema": "ao.architecture.current-release-manifest.v0.1",
            "status": "current_public_release_pair",
            "generated_at_utc": "2026-07-27T20:00:00Z",
            "source_of_truth": "public GitHub releases plus AO2 v0.5.11 and Control Plane v0.1.19 publication evidence",
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
            "source_of_truth": "public GitHub releases plus AO2 v0.5.11 and Control Plane v0.1.19 publication evidence",
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
                    "version": "v0.1.5",
                    "current_main_commit": MISSION_MAIN_COMMIT,
                },
                {
                    "repository": "ao-command",
                    "version": "v0.1.3",
                    "current_main_commit": COMMAND_MAIN_COMMIT,
                },
            ]
        }
        lock = {
            "repositories": [
                {
                    "repository": "ao-mission",
                    "commit": MISSION_TAG_TARGET,
                    "detected_version": "v0.1.5",
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
