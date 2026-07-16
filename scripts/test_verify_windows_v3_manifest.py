import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from verify_windows_v3_manifest import validate_manifest


class VerifyWindowsV3ManifestTest(unittest.TestCase):
    def test_accepts_repository_controlled_manifest_fixture(self):
        manifest = __import__("json").loads(
            Path("stack/fixtures/windows-v3/source-manifest-current-public-pair.json").read_text()
        )
        self.assertEqual(validate_manifest(manifest), [])

    def test_rejects_ao_stack_manifest_omitting_ao_mission(self):
        manifest = {
            "schema": "ao.architecture.windows-v3-source-manifest.v0.1",
            "scope": "ao-stack",
            "source": "repository_controlled_fixture_only",
            "repositories": [
                {"repository": "ao2"},
                {"repository": "ao2-control-plane"},
            ],
            "windows_v3_instance_access_authorized": False,
            "windows_v3_manifest_mutation_authorized": False,
            "external_beta_launched": False,
            "promotion_granted": False,
            "rsi_remains_denied": True,
        }
        self.assertIn("ao-stack manifests must include ao-mission", validate_manifest(manifest))

    def test_rejects_windows_v3_mutation_authority(self):
        manifest = {
            "schema": "ao.architecture.windows-v3-source-manifest.v0.1",
            "scope": "ao-stack",
            "source": "repository_controlled_fixture_only",
            "repositories": [{"repository": "ao-mission"}],
            "windows_v3_instance_access_authorized": True,
            "windows_v3_manifest_mutation_authorized": True,
            "external_beta_launched": False,
            "promotion_granted": False,
            "rsi_remains_denied": True,
        }
        errors = validate_manifest(manifest)
        self.assertIn("windows_v3_instance_access_authorized must remain false", errors)
        self.assertIn("windows_v3_manifest_mutation_authorized must remain false", errors)


if __name__ == "__main__":
    unittest.main()
