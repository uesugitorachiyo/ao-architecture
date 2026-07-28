import copy
import unittest
from pathlib import Path

try:
    from scripts.verify_github_issue_production_compatibility import (
        EXPECTED_PROVENANCE,
        EXPECTED_READBACK,
        _execution_environment,
        validate_document,
        validate_provenance,
        validate_readback,
    )
except ModuleNotFoundError:
    from verify_github_issue_production_compatibility import (
        EXPECTED_PROVENANCE,
        EXPECTED_READBACK,
        _execution_environment,
        validate_document,
        validate_provenance,
        validate_readback,
    )


ROOT = Path(__file__).resolve().parents[1]


def valid_document():
    return {
        "schema": "ao.architecture.autonomous-issue-repair.production-compatibility.v1",
        "status": "passed",
        "contract": {
            "schema_id": "ao.architecture.autonomous-issue-repair.discovery-result.v1",
            "architecture_commit": "b8c64860003238ab45fe7c76d7e8950f80a4043b",
            "schema_path": "stack/schemas/github-issue-repair/bounded-discovery-result-v1.schema.json",
            "schema_sha256": "f53c8ab36753cc645c48f391d8538ddb0b26cd9fe72edfd149e653e9975b3547",
        },
        "producer": {
            "repository": "uesugitorachiyo/ao2",
            "commit": "53e45313e8031071d730601a64be22b4d9b0c7fe",
            "pull_request": "https://github.com/uesugitorachiyo/ao2/pull/597",
            "workflow_run_ids": [30342174321, 30342174346],
            "input_repository": "uesugitorachiyo/ao-command",
            "input_path": "examples/github-issue-repair/discovery-page-envelope.valid.json",
            "input_sha256": "0fcb475fff6f23374b1785c8895e3f2c78ca62a832638189657e575164100414",
            "output_sha256": "b6d4eb04916984388af3568a9715c02397bf95b0cac7c67b3fe7c0f04242e3c3",
        },
        "consumer": {
            "repository": "uesugitorachiyo/ao-command",
            "commit": "c1c729db79e6be6037184ea9322f59d1cf511748",
            "pull_request": "https://github.com/uesugitorachiyo/ao-command/pull/150",
            "workflow_run_id": 30344676144,
            "fixture_path": "examples/github-issue-repair/discovery-result.valid.json",
            "fixture_sha256": "b6d4eb04916984388af3568a9715c02397bf95b0cac7c67b3fe7c0f04242e3c3",
            "readback_schema": "ao.command.github-issue-repair-readback.v1",
        },
        "verification": {
            "completed_at": "2026-07-28T09:02:42Z",
            "producer_replay": "passed",
            "byte_match": True,
            "consumer_readback": "passed",
            "consumer_status": "candidate_selected",
            "dependency_prefetch": "lockfile_verified",
        },
        "boundaries": {
            "operator_mode": "read_only",
            "cold_runner_dependency_prefetch_required": True,
            "producer_runtime_network_required": False,
            "github_mutation": False,
            "credential_access": False,
            "provider_access": False,
            "approval_granted": False,
            "safe_to_execute": False,
            "release_or_publication": False,
            "activates_compatibility_gate": False,
        },
    }


class ProductionCompatibilityTests(unittest.TestCase):
    def test_accepts_exact_production_pair(self):
        self.assertEqual(validate_document(valid_document()), [])

    def test_rejects_identity_digest_and_status_changes(self):
        cases = {
            "producer commit": ("producer", "commit", "0" * 40),
            "consumer commit": ("consumer", "commit", "1" * 40),
            "producer digest": ("producer", "output_sha256", "2" * 64),
            "consumer digest": ("consumer", "fixture_sha256", "3" * 64),
            "contract digest": ("contract", "schema_sha256", "4" * 64),
            "producer replay": ("verification", "producer_replay", "failed"),
            "consumer readback": ("verification", "consumer_readback", "failed"),
        }
        for name, (section, field, value) in cases.items():
            with self.subTest(name=name):
                document = valid_document()
                document[section][field] = value
                self.assertTrue(validate_document(document))

    def test_rejects_unsafe_boundaries(self):
        for field in (
            "producer_runtime_network_required",
            "github_mutation",
            "credential_access",
            "provider_access",
            "approval_granted",
            "safe_to_execute",
            "release_or_publication",
            "activates_compatibility_gate",
        ):
            with self.subTest(field=field):
                document = valid_document()
                document["boundaries"][field] = True
                self.assertIn(
                    f"boundaries.{field} must be false",
                    validate_document(document),
                )

    def test_rejects_unknown_or_missing_fields(self):
        document = valid_document()
        document["execute"] = False
        self.assertIn("document fields must exactly match the strict schema", validate_document(document))

        document = valid_document()
        del document["producer"]["workflow_run_ids"]
        self.assertIn("producer fields must exactly match the strict schema", validate_document(document))

    def test_hosted_replay_is_mandatory(self):
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
        for expected in (
            "name: Checkout exact AO2 discovery producer",
            "repository: uesugitorachiyo/ao2",
            "ref: 53e45313e8031071d730601a64be22b4d9b0c7fe",
            "path: tmp/ao2-production",
            "name: Checkout exact AO Command discovery consumer",
            "repository: uesugitorachiyo/ao-command",
            "ref: c1c729db79e6be6037184ea9322f59d1cf511748",
            "path: tmp/ao-command-production",
            "persist-credentials: false",
            "name: Verify production discovery compatibility",
            "--ao2-repository tmp/ao2-production",
            "--command-repository tmp/ao-command-production",
            "--replay",
        ):
            self.assertIn(expected, workflow)

    def test_validation_does_not_mutate_input(self):
        document = valid_document()
        before = copy.deepcopy(document)
        validate_document(document)
        self.assertEqual(document, before)

    def test_rejects_incomplete_or_changed_provenance(self):
        for field in EXPECTED_PROVENANCE:
            with self.subTest(field=field):
                provenance = copy.deepcopy(EXPECTED_PROVENANCE)
                provenance[field] = None
                self.assertTrue(validate_provenance(provenance))

        provenance = copy.deepcopy(EXPECTED_PROVENANCE)
        provenance["unexpected"] = False
        self.assertIn(
            "provenance fields must exactly match the production contract",
            validate_provenance(provenance),
        )

    def test_rejects_incomplete_or_changed_readback(self):
        for field in EXPECTED_READBACK:
            with self.subTest(field=field):
                readback = copy.deepcopy(EXPECTED_READBACK)
                readback[field] = None
                self.assertTrue(validate_readback(readback))

        readback = copy.deepcopy(EXPECTED_READBACK)
        readback["unexpected"] = False
        self.assertIn(
            "readback fields must exactly match the production contract",
            validate_readback(readback),
        )

    def test_replay_environment_pins_tools_and_excludes_credentials(self):
        environment = _execution_environment()
        self.assertEqual(environment["RUSTUP_TOOLCHAIN"], "1.95.0")
        self.assertEqual(environment["GOTOOLCHAIN"], "local")
        self.assertEqual(environment["GOPROXY"], "off")
        self.assertEqual(environment["CARGO_NET_OFFLINE"], "true")
        for name in (
            "GH_TOKEN",
            "GITHUB_TOKEN",
            "OPENAI" + "_API" + "_KEY",
            "ANTHROPIC" + "_API" + "_KEY",
        ):
            self.assertNotIn(name, environment)


if __name__ == "__main__":
    unittest.main()
