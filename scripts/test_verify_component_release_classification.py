import sys
import json
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

    def test_control_plane_release_contract_matches_public_archives(self) -> None:
        root = Path(__file__).resolve().parents[1]
        expected_artifacts = [
            "ao2-control-plane-{version}-linux-x86_64.tar.gz",
            "ao2-control-plane-{version}-macos-aarch64.tar.gz",
            "ao2-control-plane-{version}-windows-x86_64.tar.gz",
        ]
        classification = json.loads(
            (root / "stack" / "component-release-classification.json").read_text()
        )
        inventory = json.loads(
            (root / "stack" / "distributable-inventory.json").read_text()
        )
        classified = next(
            item
            for item in classification["repositories"]
            if item["repository"] == "ao2-control-plane"
        )
        distributable = next(
            item
            for item in inventory["repositories"]
            if item["repository"] == "ao2-control-plane"
        )

        self.assertEqual(classified["artifact_names"], expected_artifacts)
        self.assertEqual(distributable["artifact_names"], expected_artifacts)
        self.assertEqual(
            distributable["supported_targets"],
            ["linux-x86_64", "macos-aarch64", "windows-x86_64"],
        )


def validate_manifest_path(path: Path) -> list[str]:
    import json

    return validate_manifest(json.loads(path.read_text()))


if __name__ == "__main__":
    unittest.main()
