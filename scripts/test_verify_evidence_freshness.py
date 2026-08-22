import copy
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from verify_evidence_freshness import validate_live_readback, validate_readback

AO2_VERSION = "v0.5.11"
AO2_RELEASE_URL = "https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.11"
AO2_TAG_TARGET = "8307795b3434af920f6cef088e56ca8fcc76775b"
CONTROL_PLANE_VERSION = "v0.1.19"
CONTROL_PLANE_RELEASE_URL = "https://github.com/uesugitorachiyo/ao2-control-plane/releases/tag/v0.1.19"
CONTROL_PLANE_TAG_TARGET = "5de3541e9007e12d95b125e7f911c02932e21479"
AO2_COMPATIBILITY_EVIDENCE_VERSION = "v0.5.10"
AO2_COMPATIBILITY_EVIDENCE_PATH = "tests/fixtures/compatibility/ao2-execution-receipt-v0.5.10.json"
AO2_COMPATIBILITY_EVIDENCE_COMMIT = "214f0648ec2b15df0729f90b26a4da258882dba1"
AO2_STALE_REASON_CODE = "AO2_COMPATIBILITY_EVIDENCE_VERSION_STALE"
NOW = datetime(2026, 8, 22, 0, 5, tzinfo=timezone.utc)


def valid_manifest():
    return {
        "schema": "ao.architecture.current-release-manifest.v0.1",
        "status": "current_public_release_pair",
        "ao2": {
            "version": AO2_VERSION,
            "release_url": AO2_RELEASE_URL,
            "tag": AO2_VERSION,
            "tag_target": AO2_TAG_TARGET,
            "is_draft": False,
            "is_prerelease": False,
            "asset_count": 5,
        },
        "control_plane": {
            "version": CONTROL_PLANE_VERSION,
            "release_url": CONTROL_PLANE_RELEASE_URL,
            "tag": CONTROL_PLANE_VERSION,
            "tag_target": CONTROL_PLANE_TAG_TARGET,
            "is_draft": False,
            "is_prerelease": False,
            "asset_count": 7,
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
            {
                "producer": "ao2",
                "consumer": "ao2-control-plane",
                "contract_family": "execution_to_observation",
                "producer_contract": "execution_receipt",
                "consumer_contract": "evidence_event",
                "compatibility_status": "tested_current_release_pair",
                "canonical_vector": {
                    "repository": "ao2",
                    "path": AO2_COMPATIBILITY_EVIDENCE_PATH,
                    "pr": "https://github.com/uesugitorachiyo/ao2/pull/638",
                    "merge_commit": AO2_COMPATIBILITY_EVIDENCE_COMMIT,
                },
                "consumer_test": {
                    "repository": "ao2-control-plane",
                    "path": "crates/ao2-cp-server/tests/compatibility_vectors.rs",
                    "pr": "https://github.com/uesugitorachiyo/ao2-control-plane/pull/142",
                    "merge_commit": "247719d219bb797e005358347c0269e69b3ea5d3",
                },
            },
        ],
        "coverage": {
            "edge_count": 3,
            "uncovered_owner_pairs": 0,
            "compatibility_gate_complete": False,
            "canonical_vector_count": 3,
            "consumer_test_count": 3,
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
                "version": AO2_VERSION,
                "release_url": AO2_RELEASE_URL,
                "tag_target": AO2_TAG_TARGET,
                "is_draft": False,
                "is_prerelease": False,
                "asset_count": 5,
            },
            "control_plane": {
                "version": CONTROL_PLANE_VERSION,
                "release_url": CONTROL_PLANE_RELEASE_URL,
                "tag_target": CONTROL_PLANE_TAG_TARGET,
                "is_draft": False,
                "is_prerelease": False,
                "asset_count": 7,
            },
        },
        "compatibility_matrix": {
            "matrix_status": "proposed",
            "edge_count": 3,
            "tested_edge_count": 3,
            "fresh_edge_count": 3,
            "stale_edge_count": 0,
            "canonical_vector_count": 3,
            "consumer_test_count": 3,
            "proposed_edge_count": 0,
            "compatibility_gate_complete": False,
        },
        "compatibility_gate": {
            "state": "ready",
            "activation_authorized": False,
            "activation_evidence": "",
            "reason_code": "AO2_COMPATIBILITY_EVIDENCE_CURRENT",
            "reason": "The verified unchanged-contract bridge binds AO2 v0.5.11 to the native v0.5.10 execution-to-observation vector and Control Plane v0.1.19 consumer test.",
            "details": {},
            "allowed_states": ["false", "ready", "active", "blocked", "denied"],
            "readiness_criteria": {
                "release_metadata_matches_manifest": True,
                "matrix_counts_match": True,
                "tested_edges_have_vectors": True,
                "tested_edges_have_consumer_tests": True,
                "local_architecture_vectors_exist": True,
                "compatibility_evidence_current": True,
                "all_tested_edges_fresh": True,
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


def valid_version_skew():
    root = Path(__file__).resolve().parents[1]
    return json.loads((root / "stack" / "execution-observation-version-skew.json").read_text())


class VerifyEvidenceFreshnessTest(unittest.TestCase):
    def test_live_readback_consumes_current_version_skew(self):
        errors = validate_live_readback(
            valid_readback(),
            valid_manifest(),
            valid_matrix(),
            valid_version_skew(),
            NOW,
            existing_paths={"stack/fixtures/compatibility/architecture-route-context-v0.1.json"},
        )
        self.assertEqual(errors, [])

    def test_live_readback_rejects_expired_version_skew(self):
        expired = datetime(2026, 8, 23, 0, 1, tzinfo=timezone.utc)
        errors = validate_live_readback(
            valid_readback(),
            valid_manifest(),
            valid_matrix(),
            valid_version_skew(),
            expired,
            existing_paths={"stack/fixtures/compatibility/architecture-route-context-v0.1.json"},
        )
        self.assertIn("version_skew: compatibility evidence is stale", errors)
        self.assertIn("fresh readback requires current version-skew evidence", errors)

    def test_accepts_truthful_current_ready_readback(self):
        errors = validate_readback(
            valid_readback(),
            valid_manifest(),
            valid_matrix(),
            existing_paths={"stack/fixtures/compatibility/architecture-route-context-v0.1.json"},
        )
        self.assertEqual(errors, [])

    def test_rejects_fresh_claim_when_current_ao2_outpaces_bound_evidence(self):
        readback = valid_readback()
        matrix = valid_matrix()
        matrix["edges"][2]["canonical_vector"]["path"] = "tests/fixtures/compatibility/ao2-execution-receipt-v0.5.8.json"
        errors = validate_readback(
            readback,
            valid_manifest(),
            matrix,
            existing_paths={"stack/fixtures/compatibility/architecture-route-context-v0.1.json"},
        )
        self.assertIn(
            "AO2 compatibility evidence v0.5.8 is stale for current release v0.5.11; readback must be stale and gate blocked",
            errors,
        )

    def test_rejects_blocked_claim_when_all_evidence_is_current(self):
        readback = valid_readback()
        readback["status"] = "stale"
        readback["compatibility_gate"]["state"] = "blocked"
        errors = validate_readback(
            readback,
            valid_manifest(),
            valid_matrix(),
            existing_paths={"stack/fixtures/compatibility/architecture-route-context-v0.1.json"},
        )
        self.assertIn("readback status must be fresh when all compatibility evidence is current", errors)
        self.assertIn(
            "compatibility_gate.state must be ready when all compatibility evidence is current",
            errors,
        )

    def test_rejects_unbridged_future_ao2_release(self):
        manifest = valid_manifest()
        manifest["ao2"]["version"] = "v0.5.12"
        errors = validate_readback(
            valid_readback(),
            manifest,
            valid_matrix(),
            existing_paths={"stack/fixtures/compatibility/architecture-route-context-v0.1.json"},
        )
        self.assertTrue(any("is stale for current release v0.5.12" in error for error in errors))

    def test_rejects_nonexistent_ao2_evidence_path_and_fabricated_commit(self):
        matrix = valid_matrix()
        edge = matrix["edges"][2]
        edge["canonical_vector"]["path"] = "tests/fixtures/compatibility/ao2-execution-receipt-v0.0.1.json"
        edge["canonical_vector"]["merge_commit"] = "f" * 40
        errors = validate_readback(
            valid_readback(),
            valid_manifest(),
            matrix,
            existing_paths={"stack/fixtures/compatibility/architecture-route-context-v0.1.json"},
        )
        self.assertIn("AO2 compatibility canonical vector path is not the verified evidence path", errors)
        self.assertIn("AO2 compatibility canonical vector merge commit is not the verified evidence commit", errors)

    def test_rejects_ao2_compatibility_evidence_without_bound_version(self):
        matrix = valid_matrix()
        matrix["edges"][2]["canonical_vector"]["path"] = "tests/fixtures/compatibility/ao2-execution-receipt.json"
        errors = validate_readback(
            valid_readback(),
            valid_manifest(),
            matrix,
            existing_paths={"stack/fixtures/compatibility/architecture-route-context-v0.1.json"},
        )
        self.assertIn("AO2 compatibility canonical vector path must bind an evidence version", errors)

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
