import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from verify_component_release_classification import validate_manifest


VALID_MANIFEST = {
    "schema": "ao.architecture.component-release-classification.v0.1",
    "status": "active",
    "repositories": [
        {
            "repository": "ao2",
            "tier": 1,
            "publication_allowed": True,
            "binary_free": False,
            "artifact_only": False,
            "entry_points": ["ao2"],
            "supported_platforms": ["linux", "macos", "windows"],
            "version_source": "package.json",
            "release_owner": "ao2",
            "install_promise": "public operator binary",
            "artifact_names": [
                "ao2-{version}-linux-aarch64.tar.gz",
                "ao2-{version}-macos-aarch64.tar.gz",
                "ao2-{version}-windows-x86_64.tar.gz",
            ],
        }
    ],
}


class ComponentReleaseClassificationTests(unittest.TestCase):
    def test_rejects_missing_repositories(self) -> None:
        errors = validate_manifest(VALID_MANIFEST)
        self.assertIn("manifest must classify 14 repositories", errors)

    def test_default_manifest_validates(self) -> None:
        root = Path(__file__).resolve().parents[1]
        manifest = root / "stack" / "component-release-classification.json"
        self.assertEqual(validate_manifest_path(manifest), [])


def validate_manifest_path(path: Path) -> list[str]:
    import json

    return validate_manifest(json.loads(path.read_text()))


if __name__ == "__main__":
    unittest.main()
