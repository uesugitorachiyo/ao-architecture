#!/usr/bin/env python3
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


MODULE_PATH = Path(__file__).with_name("run_development_baseline_workflow.py")
SPEC = importlib.util.spec_from_file_location("workflow", MODULE_PATH)
workflow = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(workflow)


STAGES = list(workflow.REQUIRED_STAGES)


def document():
    stages = []
    for index, (stage_id, repository, outcome) in enumerate(STAGES):
        stages.append(
            {
                "id": stage_id,
                "repository": repository,
                "source_commit": "a" * 40,
                "consumes": [] if index == 0 else [STAGES[index - 1][0]],
                "argv": ["tool", "validate", "{run_root}"],
                "artifact": {"source": "stdout", "max_bytes": 4096},
                "terminal_status": "pass",
                "outcome": outcome,
            }
        )
    return {
        "schema": workflow.FIXTURE_SCHEMA,
        "correlation_id": "ao-cross-platform-development-baseline-20260822-r2",
        "baseline_identity": "sha256:" + "b" * 64,
        "stages": stages,
        "authority": {name: False for name in workflow.AUTHORITY_FIELDS},
    }


class ContractTests(unittest.TestCase):
    def assert_invalid(self, mutate, message):
        candidate = copy.deepcopy(document())
        mutate(candidate)
        with self.assertRaisesRegex(ValueError, message):
            workflow.validate_fixture(candidate)

    def test_valid_contract(self):
        workflow.validate_fixture(document())

    def test_mission_qualification_readback_uses_text_contract(self):
        fixture = json.loads((MODULE_PATH.parents[1] / "stack" / "fixtures" / "development-baseline-v1" / "fixture-manifest.json").read_text(encoding="utf-8"))
        mission_readback = next(stage for stage in fixture["stages"] if stage["id"] == "mission-readback")
        self.assertFalse(mission_readback["artifact"]["json"])

    def test_assurance_outputs_use_run_owned_working_directory(self):
        fixture = json.loads((MODULE_PATH.parents[1] / "stack" / "fixtures" / "development-baseline-v1" / "fixture-manifest.json").read_text(encoding="utf-8"))
        for stage_id in ("crucible-assurance", "sentinel-assurance", "promoter-no-promotion"):
            stage = next(item for item in fixture["stages"] if item["id"] == stage_id)
            self.assertEqual(stage["working_directory"], "stage_root")
            self.assertEqual(stage["prepare_argv"][:2], ["go", "build"])
            self.assertTrue(stage["artifact"]["path"].startswith("tmp/"))

    def test_unknown_working_directory_fails_closed(self):
        self.assert_invalid(lambda d: d["stages"][0].update(working_directory="workspace"), "working directory")

    def test_missing_producer(self):
        self.assert_invalid(lambda d: d["stages"][1].update(consumes=[]), "producer")

    def test_wrong_repository(self):
        self.assert_invalid(lambda d: d["stages"][2].update(repository="ao-mission"), "repository")

    def test_wrong_source(self):
        self.assert_invalid(lambda d: d["stages"][0].update(source_commit="main"), "source commit")

    def test_source_must_match_frozen_baseline(self):
        candidate = document()
        baseline = {"repositories": [{"name": repository, "commit": "a" * 40} for _, repository, _ in STAGES if repository != "ao-mission"] + [{"name": "ao-mission", "commit": "0" * 40}]}
        baseline["repositories"] = list({item["name"]: item for item in baseline["repositories"]}.values())
        candidate["baseline_identity"] = workflow._sha256(json.dumps(baseline, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
        with self.assertRaisesRegex(ValueError, "not frozen"):
            workflow.validate_baseline_binding(candidate, baseline)

    def test_correlation_drift(self):
        self.assert_invalid(lambda d: d.update(correlation_id="other"), "correlation")

    def test_digest_mismatch(self):
        self.assert_invalid(lambda d: d.update(baseline_identity="sha256:" + "0" * 63), "baseline identity")

    def test_over_authority(self):
        self.assert_invalid(lambda d: d["authority"].update(provider_calls=True), "authority")

    def test_provider_request(self):
        self.assert_invalid(lambda d: d["stages"][6].update(argv=["ao2", "--provider", "codex"]), "forbidden")

    def test_publication_request(self):
        self.assert_invalid(lambda d: d["stages"][4].update(argv=["forge", "publish"]), "forbidden")

    def test_promotion_request(self):
        self.assert_invalid(lambda d: d["stages"][-1].update(outcome="promoted"), "no_promotion")

    def test_rsi_request(self):
        self.assert_invalid(lambda d: d["stages"][6].update(argv=["ao2", "rsi"]), "forbidden")

    def test_nonterminal_stage(self):
        self.assert_invalid(lambda d: d["stages"][3].update(terminal_status="running"), "terminal")

    def test_duplicate_stage(self):
        self.assert_invalid(lambda d: d["stages"].__setitem__(2, copy.deepcopy(d["stages"][1])), "stage order")

    def test_unsafe_artifact_path(self):
        self.assert_invalid(lambda d: d["stages"][0].update(artifact={"source": "file", "path": "../escape.json", "max_bytes": 1}), "artifact path")

    def test_shell_dispatch(self):
        self.assert_invalid(lambda d: d["stages"][0].update(argv=["sh", "-c", "true"]), "shell")

    def test_cleanup_must_be_owned(self):
        candidate = document()
        candidate["cleanup"] = {"scope": "workspace"}
        with self.assertRaisesRegex(ValueError, "unknown fixture property"):
            workflow.validate_fixture(candidate)


class ResultTests(unittest.TestCase):
    def test_sanitized_environment_retains_msvc_toolchain_not_credentials(self):
        provider_key_name = "OPENAI_" + "API" + "_KEY"
        source = {"PATH": "tools", "INCLUDE": "headers", "LIB": "libraries", "GITHUB_TOKEN": "secret", provider_key_name: "secret"}
        with mock.patch.dict(workflow.os.environ, source, clear=True):
            environment = workflow._environment(Path("run"))
        self.assertEqual(environment["INCLUDE"], "headers")
        self.assertEqual(environment["LIB"], "libraries")
        self.assertNotIn("GITHUB_TOKEN", environment)
        self.assertNotIn(provider_key_name, environment)

    def test_result_validation_rejects_digest_and_cleanup_drift(self):
        result = {
            "schema": workflow.RESULT_SCHEMA,
            "status": "pass",
            "correlation_id": document()["correlation_id"],
            "baseline_identity": document()["baseline_identity"],
            "stages": [{"id": item[0], "status": "pass", "artifact_sha256": "sha256:" + "c" * 64} for item in STAGES],
            "authority": {name: False for name in workflow.AUTHORITY_FIELDS},
            "cleanup": {"run_owned_processes": 0, "run_owned_listeners": 0, "temporary_root": "removed"},
        }
        workflow.validate_result(result)
        broken = copy.deepcopy(result)
        broken["stages"][0]["artifact_sha256"] = "sha256:bad"
        with self.assertRaisesRegex(ValueError, "artifact digest"):
            workflow.validate_result(broken)
        broken = copy.deepcopy(result)
        broken["cleanup"]["temporary_root"] = "present"
        with self.assertRaisesRegex(ValueError, "cleanup"):
            workflow.validate_result(broken)


if __name__ == "__main__":
    unittest.main()
