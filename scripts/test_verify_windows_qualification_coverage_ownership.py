import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "stack" / "windows-qualification-coverage-ownership.json"
sys.path.insert(0, str(ROOT / "scripts"))


def valid_contract():
    return {
        "schema": "ao.architecture.windows-qualification-coverage-ownership.v0.1",
        "status": "active",
        "profile_version": "ao2.windows-stack-qualification.profiles.v1",
        "profile_digest": "sha256:profile-v1",
        "expected_profile_digest": "sha256:profile-v1",
        "known_commands": [
            "hosted-windows:test-cli-release-readiness",
            "physical-windows:windows-worker-pytest",
            "physical-windows:windows-file-locking-rollback",
        ],
        "invariants": [
            {
                "id": "portable-release-readiness",
                "description": "Broad portable release-readiness regression coverage.",
                "producing_repository": "ao2",
                "canonical_owner": "hosted_native_windows",
                "required_inputs": ["ao2@f2c6a2242406232dd833ac826bc27f05ebaccf54"],
                "exact_head_bindings": {"ao2": "f2c6a2242406232dd833ac826bc27f05ebaccf54"},
                "command_profile_shard_id": "hosted-windows:test-cli-release-readiness",
                "failure_semantics": "blocks release readiness",
                "downstream_consumer": "ao2 stable release gate",
                "gate_status": "required",
            },
            {
                "id": "worker-protocol",
                "description": "Outbound task-board protocol and actual worker lifecycle.",
                "producing_repository": "ao2",
                "canonical_owner": "physical_windows",
                "required_inputs": ["ao2@f2c6a2242406232dd833ac826bc27f05ebaccf54"],
                "exact_head_bindings": {"ao2": "f2c6a2242406232dd833ac826bc27f05ebaccf54"},
                "command_profile_shard_id": "physical-windows:windows-worker-pytest",
                "failure_semantics": "blocks physical Windows qualification",
                "downstream_consumer": "Windows worker release qualification",
                "gate_status": "required",
            },
            {
                "id": "file-locking-rollback",
                "description": "Windows file locking and rollback behavior on the physical host.",
                "producing_repository": "ao2",
                "canonical_owner": "both",
                "non_duplicate_reason": "Hosted Windows catches portable lock API regressions; physical Windows catches installed worker rollback behavior.",
                "required_inputs": ["ao2@f2c6a2242406232dd833ac826bc27f05ebaccf54"],
                "exact_head_bindings": {"ao2": "f2c6a2242406232dd833ac826bc27f05ebaccf54"},
                "command_profile_shard_id": "physical-windows:windows-file-locking-rollback",
                "failure_semantics": "blocks final frozen-head reconciliation",
                "downstream_consumer": "Windows installed candidate verification",
                "gate_status": "required",
            },
        ],
    }


class VerifyWindowsQualificationCoverageOwnershipTest(unittest.TestCase):
    def validate(self, document):
        try:
            from verify_windows_qualification_coverage_ownership import validate_document
        except ModuleNotFoundError as exc:
            self.fail(f"coverage ownership validator module is missing: {exc}")
        return validate_document(document)

    def test_contract_records_canonical_ownership_model(self):
        self.assertTrue(CONTRACT.exists(), "stack/windows-qualification-coverage-ownership.json is required")
        contract = json.loads(CONTRACT.read_text())

        self.assertEqual([], self.validate(contract))
        self.assertEqual(contract["schema"], "ao.architecture.windows-qualification-coverage-ownership.v0.1")
        self.assertEqual(contract["status"], "active")
        self.assertEqual(contract["profile_version"], "ao2.windows-stack-qualification.profiles.v1")
        self.assertEqual(contract["profile_digest"], contract["expected_profile_digest"])

        owners = {item["id"]: item["canonical_owner"] for item in contract["invariants"]}
        self.assertEqual(owners["portable-rust-go-python-regressions"], "hosted_native_windows")
        self.assertEqual(owners["outbound-task-board-protocol"], "physical_windows")
        self.assertEqual(owners["windows-file-locking-rollback"], "both")

    def test_rejects_missing_invariant_owner(self):
        contract = valid_contract()
        del contract["invariants"][0]["canonical_owner"]

        errors = self.validate(contract)

        self.assertIn("invariants[0].canonical_owner must be hosted_native_windows, physical_windows, or both", errors)

    def test_rejects_unknown_command_profile_shard_id(self):
        contract = valid_contract()
        contract["invariants"][0]["command_profile_shard_id"] = "physical-windows:unknown-command"

        errors = self.validate(contract)

        self.assertIn("invariants[0].command_profile_shard_id must reference known_commands", errors)

    def test_rejects_duplicate_ownership_without_independent_reason(self):
        contract = valid_contract()
        contract["invariants"][2]["non_duplicate_reason"] = ""

        errors = self.validate(contract)

        self.assertIn("invariants[2].non_duplicate_reason is required when canonical_owner is both", errors)

    def test_rejects_skipped_required_gate(self):
        contract = valid_contract()
        contract["invariants"][1]["gate_status"] = "skipped"

        errors = self.validate(contract)

        self.assertIn("invariants[1].gate_status must be required", errors)

    def test_rejects_stale_profile_digest(self):
        contract = valid_contract()
        contract["profile_digest"] = "sha256:old-profile"

        errors = self.validate(contract)

        self.assertIn("profile_digest must match expected_profile_digest", errors)

    def test_rejects_cross_compilation_as_native_windows_owner(self):
        contract = valid_contract()
        contract["invariants"][0]["canonical_owner"] = "cross_compiled_windows"

        errors = self.validate(contract)

        self.assertIn("invariants[0].canonical_owner must be hosted_native_windows, physical_windows, or both", errors)


if __name__ == "__main__":
    unittest.main()
