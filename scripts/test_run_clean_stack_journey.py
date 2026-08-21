import importlib.util
import json
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("run_clean_stack_journey.py")
SPEC = importlib.util.spec_from_file_location("clean_stack_journey", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def passing_journey():
    return {
        "schema": "ao.stack.windows.clean-machine-journey.v1",
        "status": "passed",
        "execution_environment": {
            "native_windows": True,
            "clean_machine": True,
            "workspace_path_contains_spaces": True,
            "credential_free": True,
        },
        "authority": {
            "provider_calls": 0,
            "publications": 0,
            "deployments": 0,
            "compatibility_activations": 0,
            "pushes": 0,
            "merges": 0,
        },
        "steps": [
            {"step": name, "result": "passed"}
            for name in MODULE.REQUIRED_STEPS
        ],
        "cleanup": {"processes": 0, "services": 0, "listeners": 0, "temporary_state": 0},
    }


def test_validate_accepts_complete_clean_machine_journey():
    MODULE.validate_journey(passing_journey())


def test_validate_rejects_missing_upgrade_and_recovery_steps():
    document = passing_journey()
    document["steps"] = [step for step in document["steps"] if step["step"] not in {"upgrade", "recovery"}]
    try:
        MODULE.validate_journey(document)
    except ValueError as error:
        assert "required steps" in str(error)
    else:
        raise AssertionError("incomplete journey was accepted")


def test_validate_rejects_nonzero_authority_or_dirty_cleanup():
    document = passing_journey()
    document["authority"]["provider_calls"] = 1
    document["cleanup"]["processes"] = 1
    try:
        MODULE.validate_journey(document)
    except ValueError as error:
        assert "authority" in str(error) or "cleanup" in str(error)
    else:
        raise AssertionError("unsafe journey was accepted")


def test_report_is_public_safe_and_deterministic():
    document = passing_journey()
    body = MODULE.serialize_report(document)
    assert b"C:\\Users" not in body
    assert b"token" not in body.lower()
    assert json.loads(body)["schema"] == "ao.stack.windows.clean-machine-journey.v1"
