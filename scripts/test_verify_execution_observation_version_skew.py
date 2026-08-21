import copy
import json
import os
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from verify_execution_observation_version_skew import read_strict_json, validate_contract


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 8, 21, 0, 5, tzinfo=timezone.utc)


def valid_contract():
    return json.loads((ROOT / "stack" / "execution-observation-version-skew.json").read_text())


class VersionSkewContractTest(unittest.TestCase):
    def test_accepts_current_three_pair_contract(self):
        self.assertEqual(validate_contract(valid_contract(), NOW), [])

    def test_binds_final_v0511_candidate_heads(self):
        candidate = valid_contract()["pairs"][2]
        self.assertEqual(candidate["ao2_version"], "v0.5.11")
        self.assertEqual(candidate["ao2_source_sha"], "8307795b3434af920f6cef088e56ca8fcc76775b")
        self.assertEqual(candidate["control_plane_version"], "v0.1.19")
        self.assertEqual(candidate["control_plane_source_sha"], "4e41da173dc9f1ee37f4ae99b85791e5f05ea453")
        self.assertEqual(candidate["status"], "supported_by_unchanged_bridge")

    def test_rejects_required_negative_matrix(self):
        mutations = [
            ("wrong schema", lambda value: value.update(schema="wrong")),
            ("wrong source head", lambda value: value["pairs"][2].update(ao2_source_sha="0" * 40)),
            ("wrong version", lambda value: value["pairs"][1].update(ao2_version="v0.5.5")),
            ("altered digest", lambda value: value["evidence"].update(producer_sha256="0" * 64)),
            ("unsupported skew", lambda value: value["pairs"][0].update(status="unsupported")),
            ("authority change", lambda value: value["boundaries"].update(permits_release=True)),
        ]
        for label, mutate in mutations:
            with self.subTest(label=label):
                candidate = copy.deepcopy(valid_contract())
                mutate(candidate)
                self.assertTrue(validate_contract(candidate, NOW))

    def test_rejects_stale_timestamp(self):
        stale = datetime(2026, 8, 22, 0, 1, tzinfo=timezone.utc)
        self.assertIn("compatibility evidence is stale", validate_contract(valid_contract(), stale))

    def test_rejects_extended_expiry(self):
        candidate = valid_contract()
        candidate["valid_until"] = "2100-01-01T00:00:00Z"
        self.assertIn(
            "valid_until must match the bound compatibility vector",
            validate_contract(candidate, NOW),
        )

    def test_rejects_future_generation_time(self):
        candidate = valid_contract()
        candidate["generated_at"] = "2026-08-21T00:30:00Z"
        errors = validate_contract(candidate, NOW)
        self.assertIn("generated_at must match the bound compatibility vector", errors)
        self.assertIn("generated_at cannot be in the future", errors)

    def test_expires_at_exact_boundary(self):
        boundary = datetime(2026, 8, 22, 0, 0, tzinfo=timezone.utc)
        self.assertIn("compatibility evidence is stale", validate_contract(valid_contract(), boundary))

    def test_rejects_malformed_and_unknown_fields(self):
        candidate = valid_contract()
        candidate["unknown_authority"] = True
        candidate["generated_at"] = "not-a-timestamp"
        errors = validate_contract(candidate, NOW)
        self.assertIn("top-level fields must exactly match the strict schema", errors)
        self.assertIn("generated_at must be an RFC3339 UTC timestamp", errors)

    def test_strict_reader_rejects_duplicate_keys_and_oversized_input(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "contract.json"
            path.write_text('{"schema":"one","schema":"two"}')
            with self.assertRaisesRegex(ValueError, "duplicate key"):
                read_strict_json(path)
            path.write_bytes(b" " * 1_048_577)
            with self.assertRaisesRegex(ValueError, "exceeds"):
                read_strict_json(path)

    def test_strict_reader_rejects_symlink(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "target.json"
            target.write_text("{}")
            link = Path(directory) / "contract.json"
            try:
                link.symlink_to(target)
            except OSError as exc:
                if os.name == "nt" and getattr(exc, "winerror", None) == 1314:
                    self.skipTest("Windows symlink privilege is not held")
                raise
            with self.assertRaisesRegex(ValueError, "regular non-symlink"):
                read_strict_json(link)


if __name__ == "__main__":
    unittest.main()
