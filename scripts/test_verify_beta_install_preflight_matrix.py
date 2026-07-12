import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from verify_beta_install_preflight_matrix import validate_matrix


def valid_matrix():
    required_checks = [
        "stack_lock_present",
        "native_tests_available",
        "contract_registry_available",
        "operator_cli_available",
        "evidence_store_writable",
    ]
    return {
        "schema": "ao.architecture.beta-install-preflight-matrix.v0.1",
        "status": "planning_only",
        "scope": "ao-stack",
        "platforms": [
            {
                "platform": "macos",
                "runner": "macos-latest",
                "required_checks": required_checks,
                "blocks_beta_install": True,
                "executes_install": False,
            },
            {
                "platform": "linux",
                "runner": "ubuntu-latest",
                "required_checks": required_checks,
                "blocks_beta_install": True,
                "executes_install": False,
            },
            {
                "platform": "windows",
                "runner": "windows-latest",
                "required_checks": required_checks,
                "blocks_beta_install": True,
                "executes_install": False,
            },
        ],
        "safety": {
            "planning_only": True,
            "provider_calls": False,
            "release_or_publish": False,
            "credential_use": False,
            "promotion_granted": False,
            "rsi_remains_denied": True,
        },
    }


class VerifyBetaInstallPreflightMatrixTest(unittest.TestCase):
    def test_accepts_beta_install_preflight_matrix(self):
        self.assertEqual(validate_matrix(valid_matrix()), [])

    def test_rejects_missing_windows_platform(self):
        matrix = valid_matrix()
        matrix["platforms"] = matrix["platforms"][:2]
        self.assertIn("missing platforms: windows", validate_matrix(matrix))

    def test_rejects_executable_or_promoting_matrix(self):
        matrix = valid_matrix()
        matrix["platforms"][0]["executes_install"] = True
        matrix["safety"]["promotion_granted"] = True
        errors = validate_matrix(matrix)
        self.assertIn("platforms[0].executes_install must be false", errors)
        self.assertIn("safety.promotion_granted must be false", errors)

    def test_accepts_current_stack_matrix(self):
        matrix = __import__("json").loads(Path("stack/beta-install-preflight-matrix.json").read_text())
        self.assertEqual(validate_matrix(matrix), [])


if __name__ == "__main__":
    unittest.main()
