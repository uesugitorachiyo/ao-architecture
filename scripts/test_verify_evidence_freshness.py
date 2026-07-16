import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from verify_evidence_freshness import validate_readback


def valid_manifest():
    return {
        "schema": "ao.architecture.current-release-manifest.v0.1",
        "status": "current_public_release_pair",
        "ao2": {
            "version": "v0.5.1",
            "release_url": "https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.1",
            "tag": "v0.5.1",
            "tag_target": "80ec5321f42d4bab17d5e64fdae6aa099ba59d4a",
            "is_draft": False,
            "is_prerelease": False,
            "asset_count": 23,
        },
        "control_plane": {
            "version": "v0.1.15",
            "release_url": "https://github.com/uesugitorachiyo/ao2-control-plane/releases/tag/v0.1.15",
            "tag": "v0.1.15",
            "tag_target": "f1702b387607566cac457458af9adb5871a5c412",
            "is_draft": False,
            "is_prerelease": False,
            "asset_count": 6,
        },
    }


def valid_matrix():
    return {
        "schema": "ao.architecture.contract-compatibility-matrix.v0.1",
        "status": "proposed",
        "edges": [
            {
                "producer": "ao-architecture",
                "consumer": "ao-mission",
                "contract_family": "authority_and_topology",
                "producer_contract": "authority_inventory",
                "consumer_contract": "mission_route_context",
                "compatibility_status": "tested_current_release_pair",
                "canonical_vector": {
                    "repository": "ao-architecture",
                    "path": "stack/fixtures/compatibility/architecture-route-context-v0.1.json",
                    "pr": "https://github.com/uesugitorachiyo/ao-architecture/pull/113",
                    "merge_commit": "417dc64b5805ab5aabc5e7d6a5a015e156ecf6b8",
                },
                "consumer_test": {
                    "repository": "ao-mission",
                    "path": "internal/mission/mission_test.go",
                    "pr": "https://github.com/uesugitorachiyo/ao-mission/pull/88",
                    "merge_commit": "6823f4eb82a89abe46ce484533d929649d09d8ad",
                },
            },
            {
                "producer": "ao-blueprint",
                "consumer": "ao-atlas",
                "contract_family": "requirements_to_workgraph",
                "producer_contract": "blueprint_pack",
                "consumer_contract": "context_pack",
                "compatibility_status": "tested_current_release_pair",
                "canonical_vector": {
                    "repository": "ao-blueprint",
                    "path": "examples/compatibility/blueprint-authorization-to-atlas-context-v0.1.json",
                    "pr": "https://github.com/uesugitorachiyo/ao-blueprint/pull/46",
                    "merge_commit": "2be0647f28b0ccc3222a5f6c4a4676dfd9bba946",
                },
                "consumer_test": {
                    "repository": "ao-atlas",
                    "path": "internal/atlas/atlas_test.go",
                    "pr": "https://github.com/uesugitorachiyo/ao-atlas/pull/731",
                    "merge_commit": "76303c122352b1deac63670e203bdb941ac4a3cc",
                },
            },
        ],
        "coverage": {
            "edge_count": 2,
            "uncovered_owner_pairs": 0,
            "compatibility_gate_complete": False,
            "canonical_vector_count": 2,
            "consumer_test_count": 2,
        },
        "safety": {
            "promotion_granted": False,
            "rsi_remains_denied": True,
            "migration_started": False,
        },
    }


def valid_readback():
    return {
        "schema": "ao.architecture.evidence-freshness-readback.v0.1",
        "status": "fresh",
        "current_public_release_pair": {
            "ao2": {
                "version": "v0.5.1",
                "release_url": "https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.1",
                "tag_target": "80ec5321f42d4bab17d5e64fdae6aa099ba59d4a",
                "is_draft": False,
                "is_prerelease": False,
                "asset_count": 23,
            },
            "control_plane": {
                "version": "v0.1.15",
                "release_url": "https://github.com/uesugitorachiyo/ao2-control-plane/releases/tag/v0.1.15",
                "tag_target": "f1702b387607566cac457458af9adb5871a5c412",
                "is_draft": False,
                "is_prerelease": False,
                "asset_count": 6,
            },
        },
        "compatibility_matrix": {
            "matrix_status": "proposed",
            "edge_count": 2,
            "tested_edge_count": 2,
            "canonical_vector_count": 2,
            "consumer_test_count": 2,
            "proposed_edge_count": 0,
            "compatibility_gate_complete": False,
        },
        "compatibility_gate": {
            "state": "ready",
            "activation_authorized": False,
            "activation_evidence": "",
            "reason": "fresh evidence is present; activation is not authorized in Month 1",
            "allowed_states": ["false", "ready", "active", "blocked", "denied"],
            "readiness_criteria": {
                "release_metadata_matches_manifest": True,
                "matrix_counts_match": True,
                "tested_edges_have_vectors": True,
                "tested_edges_have_consumer_tests": True,
                "local_architecture_vectors_exist": True,
                "external_beta_launched": False,
                "promotion_requested": False,
                "promotion_granted": False,
                "provider_pilot": False,
                "release_or_publish": False,
                "rsi_remains_denied": True,
            },
        },
        "boundaries": {
            "external_beta_launched": False,
            "promotion_requested": False,
            "promotion_granted": False,
            "provider_pilot": False,
            "release_or_publish": False,
            "tag_or_upload": False,
            "deployment": False,
            "live_self_modification": False,
            "rsi_remains_denied": True,
        },
    }


class VerifyEvidenceFreshnessTest(unittest.TestCase):
    def test_accepts_fresh_gate_ready_readback(self):
        errors = validate_readback(
            valid_readback(),
            valid_manifest(),
            valid_matrix(),
            existing_paths={"stack/fixtures/compatibility/architecture-route-context-v0.1.json"},
        )
        self.assertEqual(errors, [])

    def test_rejects_public_metadata_drift(self):
        readback = valid_readback()
        readback["current_public_release_pair"]["ao2"]["tag_target"] = "0" * 40
        errors = validate_readback(
            readback,
            valid_manifest(),
            valid_matrix(),
            existing_paths={"stack/fixtures/compatibility/architecture-route-context-v0.1.json"},
        )
        self.assertIn("ao2.tag_target must match current release manifest", errors)

    def test_rejects_matrix_count_drift(self):
        readback = valid_readback()
        readback["compatibility_matrix"]["canonical_vector_count"] = 1
        errors = validate_readback(
            readback,
            valid_manifest(),
            valid_matrix(),
            existing_paths={"stack/fixtures/compatibility/architecture-route-context-v0.1.json"},
        )
        self.assertIn("compatibility_matrix.canonical_vector_count must equal tested edge count", errors)

    def test_rejects_missing_local_architecture_vector(self):
        errors = validate_readback(valid_readback(), valid_manifest(), valid_matrix(), existing_paths=set())
        self.assertIn(
            "local architecture vector missing: stack/fixtures/compatibility/architecture-route-context-v0.1.json",
            errors,
        )

    def test_rejects_active_gate_without_activation_evidence(self):
        readback = valid_readback()
        readback["compatibility_gate"]["state"] = "active"
        readback["compatibility_gate"]["activation_authorized"] = False
        readback["compatibility_gate"]["activation_evidence"] = ""
        errors = validate_readback(
            readback,
            valid_manifest(),
            valid_matrix(),
            existing_paths={"stack/fixtures/compatibility/architecture-route-context-v0.1.json"},
        )
        self.assertIn("compatibility_gate active requires activation_authorized=true", errors)
        self.assertIn("compatibility_gate active requires activation_evidence", errors)

    def test_rejects_boundary_overclaims(self):
        readback = valid_readback()
        readback["boundaries"]["promotion_granted"] = True
        readback["compatibility_gate"]["readiness_criteria"]["rsi_remains_denied"] = False
        errors = validate_readback(
            readback,
            valid_manifest(),
            valid_matrix(),
            existing_paths={"stack/fixtures/compatibility/architecture-route-context-v0.1.json"},
        )
        self.assertIn("promotion_granted must remain false", errors)
        self.assertIn("readiness_criteria.rsi_remains_denied must be true", errors)


if __name__ == "__main__":
    unittest.main()
