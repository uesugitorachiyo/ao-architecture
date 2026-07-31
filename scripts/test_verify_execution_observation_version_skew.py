import copy
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from verify_execution_observation_version_skew import read_strict_json, validate_contract


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 7, 31, 23, 0, tzinfo=timezone.utc)


def valid_contract():
    return json.loads((ROOT / "stack" / "execution-observation-version-skew.json").read_text())


class VersionSkewContractTest(unittest.TestCase):
    def test_accepts_current_three_pair_contract(self):
        self.assertEqual(validate_contract(valid_contract(), NOW), [])

    def test_rejects_required_negative_matrix(self):
        mutations = [
            ("wrong schema", lambda value: value.update(schema="wrong")),
            ("wrong source head", lambda value: value["pairs"][2].update(ao2_source_sha="0" * 40)),
            ("wrong version", lambda value: value["pairs"][1].update(ao2_version="v0.5.5")),
            ("altered digest", lambda value: value["evidence"].update(producer_sha256="altered")),
            ("unsupported skew", lambda value: value["pairs"][0].update(status="unsupported")),
            ("authority change", lambda value: value["boundaries"].update(permits_release=True)),
        ]
        for label, mutate in mutations:
            with self.subTest(label=label):
                candidate = copy.deepcopy(valid_contract())
                mutate(candidate)
                self.assertTrue(validate_contract(candidate, NOW))

    def test_rejects_stale_timestamp(self):
        stale = datetime(2026, 8, 31, tzinfo=timezone.utc)
        self.assertIn("compatibility evidence is stale", validate_contract(valid_contract(), stale))

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


if __name__ == "__main__":
    unittest.main()
