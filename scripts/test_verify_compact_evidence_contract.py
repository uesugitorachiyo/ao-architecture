import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "stack" / "compact-evidence-contract.json"
FIXTURE = ROOT / "stack" / "fixtures" / "compact-evidence" / "valid-manifest-v0.1.json"
sys.path.insert(0, str(ROOT / "scripts"))

REQUIREMENTS = {
    "versioned_manifest",
    "ordered_bounded_chunks",
    "deterministic_canonical_serialization",
    "chunk_and_total_record_counts",
    "first_and_last_record_id_per_chunk",
    "sha256_digest_per_chunk",
    "aggregate_manifest_digest",
    "unique_record_ids",
    "stable_record_ordering",
    "streaming_verification",
    "deterministic_lookup",
    "no_absolute_machine_local_paths",
    "no_credentials_or_private_values",
}


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def jsonl(records):
    return b"".join(canonical_json(record) + b"\n" for record in records)


def valid_manifest_and_chunks():
    chunks = {
        "chunks/000001.jsonl": jsonl([
            {"record_id": "evidence-000001", "kind": "node_evidence", "payload": {"status": "pass"}},
            {"record_id": "evidence-000002", "kind": "node_evidence", "payload": {"status": "pass"}},
        ]),
        "chunks/000002.jsonl": jsonl([
            {"record_id": "evidence-000003", "kind": "run_link", "payload": {"status": "pass"}},
        ]),
    }
    manifest = {
        "schema": "ao.architecture.compact-evidence-manifest.v0.1",
        "format_version": "v0.1",
        "chunk_order": ["chunks/000001.jsonl", "chunks/000002.jsonl"],
        "total_record_count": 3,
        "chunks": [
            {
                "path": "chunks/000001.jsonl",
                "record_count": 2,
                "first_record_id": "evidence-000001",
                "last_record_id": "evidence-000002",
                "sha256": hashlib.sha256(chunks["chunks/000001.jsonl"]).hexdigest(),
            },
            {
                "path": "chunks/000002.jsonl",
                "record_count": 1,
                "first_record_id": "evidence-000003",
                "last_record_id": "evidence-000003",
                "sha256": hashlib.sha256(chunks["chunks/000002.jsonl"]).hexdigest(),
            },
        ],
        "lookup": {
            "strategy": "ordered_chunk_ranges",
            "ranges": [
                {"first_record_id": "evidence-000001", "last_record_id": "evidence-000002", "chunk": "chunks/000001.jsonl"},
                {"first_record_id": "evidence-000003", "last_record_id": "evidence-000003", "chunk": "chunks/000002.jsonl"},
            ],
        },
    }
    aggregate = copy.deepcopy(manifest)
    aggregate["manifest_digest"] = ""
    manifest["manifest_digest"] = hashlib.sha256(canonical_json(aggregate)).hexdigest()
    return manifest, chunks


class VerifyCompactEvidenceContractTest(unittest.TestCase):
    def test_contract_records_canonical_compact_evidence_requirements(self):
        self.assertTrue(CONTRACT.exists(), "stack/compact-evidence-contract.json is required")
        contract = json.loads(CONTRACT.read_text())

        self.assertEqual(contract["schema"], "ao.architecture.compact-evidence-contract.v0.1")
        self.assertEqual(contract["status"], "proposed")
        self.assertEqual(contract["format_version"], "v0.1")
        self.assertEqual(contract["owner"], "ao-architecture")
        self.assertEqual(set(contract["requirements"]), REQUIREMENTS)
        self.assertEqual(contract["standard_input_sizes"], [100, 1000, 10000])
        self.assertGreaterEqual(contract["high_cardinality_fixture_floor"], 9000)
        self.assertLessEqual(contract["bounded_chunk_max_records"], 1000)
        self.assertEqual(contract["record_ordering"], "stable_lexicographic_record_id")
        self.assertEqual(contract["lookup"], "ordered_chunk_ranges")
        self.assertTrue(contract["compatibility"]["legacy_per_file_evidence_supported"])
        self.assertTrue(contract["compatibility"]["compact_and_legacy_records_equivalent"])
        self.assertTrue(contract["compatibility"]["generators_compact_only_after_consumers_compatible"])
        self.assertFalse(contract["safety"]["allow_absolute_machine_local_paths"])
        self.assertFalse(contract["safety"]["allow_credentials_or_private_values"])

    def test_contract_validator_rejects_missing_required_semantics(self):
        from verify_compact_evidence_contract import validate_contract_document

        errors = validate_contract_document({
            "schema": "ao.architecture.compact-evidence-contract.v0.1",
            "status": "active",
            "format_version": "v0.1",
            "owner": "ao-foundry",
            "requirements": ["versioned_manifest"],
            "standard_input_sizes": [100, 1000],
            "high_cardinality_fixture_floor": 100,
            "bounded_chunk_max_records": 5000,
            "compatibility": {
                "legacy_per_file_evidence_supported": False,
                "compact_and_legacy_records_equivalent": True,
                "generators_compact_only_after_consumers_compatible": False,
            },
            "safety": {
                "allow_absolute_machine_local_paths": True,
                "allow_credentials_or_private_values": True,
            },
        })

        self.assertIn("status must remain proposed until all consumers are compatible", errors)
        self.assertIn("owner must be ao-architecture", errors)
        self.assertIn("requirements missing streaming_verification", errors)
        self.assertIn("standard_input_sizes must be [100, 1000, 10000]", errors)
        self.assertIn("high_cardinality_fixture_floor must be at least 9000", errors)
        self.assertIn("bounded_chunk_max_records must be between 1 and 1000", errors)
        self.assertIn("compatibility.legacy_per_file_evidence_supported must be true", errors)
        self.assertIn("compatibility.generators_compact_only_after_consumers_compatible must be true", errors)
        self.assertIn("safety.allow_absolute_machine_local_paths must be false", errors)
        self.assertIn("safety.allow_credentials_or_private_values must be false", errors)

    def test_fixture_manifest_verifies(self):
        from verify_compact_evidence_contract import load_fixture_chunks, validate_compact_manifest

        self.assertTrue(FIXTURE.exists(), "compact evidence fixture manifest is required")
        manifest = json.loads(FIXTURE.read_text())
        chunks = load_fixture_chunks(FIXTURE)
        self.assertEqual(validate_compact_manifest(manifest, chunks), [])

    def test_manifest_validator_rejects_corrupt_chunk_sets(self):
        from verify_compact_evidence_contract import validate_compact_manifest

        manifest, chunks = valid_manifest_and_chunks()
        self.assertEqual(validate_compact_manifest(manifest, chunks), [])

        missing_chunks = dict(chunks)
        del missing_chunks["chunks/000002.jsonl"]
        self.assertIn("chunks/000002.jsonl is missing", validate_compact_manifest(manifest, missing_chunks))

        extra_chunks = dict(chunks)
        extra_chunks["chunks/extra.jsonl"] = b"{}\n"
        self.assertIn("chunks/extra.jsonl is not declared by manifest", validate_compact_manifest(manifest, extra_chunks))

        duplicate_chunks = dict(chunks)
        duplicate_chunks["chunks/000002.jsonl"] = jsonl([
            {"record_id": "evidence-000002", "kind": "run_link", "payload": {"status": "pass"}},
        ])
        self.assertIn("duplicate record_id evidence-000002", validate_compact_manifest(manifest, duplicate_chunks))

        out_of_order = dict(chunks)
        out_of_order["chunks/000002.jsonl"] = jsonl([
            {"record_id": "evidence-000000", "kind": "run_link", "payload": {"status": "pass"}},
        ])
        self.assertIn("record_id evidence-000000 is out of order", validate_compact_manifest(manifest, out_of_order))

        count_mismatch = copy.deepcopy(manifest)
        count_mismatch["chunks"][0]["record_count"] = 99
        self.assertIn("chunks/000001.jsonl record_count mismatch", validate_compact_manifest(count_mismatch, chunks))

        range_mismatch = copy.deepcopy(manifest)
        range_mismatch["chunks"][0]["last_record_id"] = "evidence-999999"
        self.assertIn("chunks/000001.jsonl last_record_id mismatch", validate_compact_manifest(range_mismatch, chunks))

        digest_mismatch = copy.deepcopy(manifest)
        digest_mismatch["chunks"][0]["sha256"] = "0" * 64
        self.assertIn("chunks/000001.jsonl sha256 mismatch", validate_compact_manifest(digest_mismatch, chunks))

        malformed_chunks = dict(chunks)
        malformed_chunks["chunks/000001.jsonl"] = b"{not-json}\n"
        self.assertIn("chunks/000001.jsonl line 1 malformed JSON", validate_compact_manifest(manifest, malformed_chunks))

        path_traversal = copy.deepcopy(manifest)
        path_traversal["chunks"][0]["path"] = "../secret.jsonl"
        self.assertIn("chunks[0].path must be a safe relative path", validate_compact_manifest(path_traversal, chunks))


if __name__ == "__main__":
    unittest.main()
