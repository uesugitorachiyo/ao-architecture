import hashlib
import io
from pathlib import Path
import tarfile
import tempfile
import unittest
import zipfile

from scripts import run_public_stack_canary as canary


class ManifestTests(unittest.TestCase):
    def test_each_target_selects_all_seven_components(self):
        for target in ("linux-x86_64", "macos-aarch64", "windows-x86_64"):
            with self.subTest(target=target):
                assets = canary.select_assets(target)
                self.assertEqual(7, len(assets))
                self.assertEqual(7, len({asset.component for asset in assets}))

    def test_selected_assets_are_pinned_public_release_downloads(self):
        for target in canary.TARGETS:
            for asset in canary.select_assets(target):
                with self.subTest(target=target, component=asset.component):
                    self.assertRegex(asset.sha256, r"^[0-9a-f]{64}$")
                    self.assertTrue(
                        asset.url.startswith("https://github.com/uesugitorachiyo/")
                    )
                    self.assertIn("/releases/download/", asset.url)


class SafeInstallTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.destination = self.root / "install"

    def tearDown(self):
        self.temporary.cleanup()

    def asset(self, archive, binary="tool"):
        return canary.Asset(
            component="example",
            version="v1.0.0",
            source_sha="a" * 40,
            url="https://github.com/uesugitorachiyo/example/releases/download/v1.0.0/tool",
            sha256="0" * 64,
            archive=archive,
            binary=binary,
        )

    def write(self, name, content):
        path = self.root / name
        path.write_bytes(content)
        return path

    def make_tar(self, entries):
        path = self.root / "asset.tar.gz"
        with tarfile.open(path, "w:gz") as archive:
            for name, content in entries:
                info = tarfile.TarInfo(name)
                info.size = len(content)
                info.mode = 0o755
                archive.addfile(info, io.BytesIO(content))
        return path

    def make_zip(self, entries):
        path = self.root / "asset.zip"
        with zipfile.ZipFile(path, "w") as archive:
            for name, content in entries:
                archive.writestr(name, content)
        return path

    def test_verify_digest_rejects_changed_bytes(self):
        path = self.write("asset", b"changed")
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            canary.verify_digest(path, "0" * 64)

    def test_verify_digest_accepts_exact_bytes(self):
        path = self.write("asset", b"exact")
        canary.verify_digest(path, hashlib.sha256(b"exact").hexdigest())

    def test_tar_install_copies_regular_binary(self):
        archive = self.make_tar([("nested/tool", b"binary")])
        installed = canary.install_asset(
            self.asset("tar.gz"), archive, self.destination
        )
        self.assertEqual((self.destination / "tool",), installed)
        self.assertEqual(b"binary", installed[0].read_bytes())

    def test_zip_install_copies_regular_binary(self):
        archive = self.make_zip([("nested/tool.exe", b"binary")])
        installed = canary.install_asset(
            self.asset("zip", "tool.exe"), archive, self.destination
        )
        self.assertEqual((self.destination / "tool.exe",), installed)
        self.assertEqual(b"binary", installed[0].read_bytes())

    def test_raw_install_renames_public_asset_to_binary(self):
        archive = self.write("downloaded-name", b"binary")
        installed = canary.install_asset(
            self.asset("raw"), archive, self.destination
        )
        self.assertEqual((self.destination / "tool",), installed)
        self.assertEqual(b"binary", installed[0].read_bytes())

    def test_tar_install_rejects_parent_traversal(self):
        archive = self.make_tar([("../escape", b"bad")])
        with self.assertRaisesRegex(ValueError, "unsafe archive path"):
            canary.install_asset(self.asset("tar.gz"), archive, self.destination)

    def test_zip_install_rejects_duplicate_binary_names(self):
        archive = self.make_zip(
            [("first/tool.exe", b"one"), ("second/tool.exe", b"two")]
        )
        with self.assertRaisesRegex(ValueError, "duplicate binary"):
            canary.install_asset(
                self.asset("zip", "tool.exe"), archive, self.destination
            )

    def test_tar_install_rejects_links(self):
        path = self.root / "link.tar.gz"
        with tarfile.open(path, "w:gz") as archive:
            info = tarfile.TarInfo("tool")
            info.type = tarfile.SYMTYPE
            info.linkname = "outside"
            archive.addfile(info)
        with self.assertRaisesRegex(ValueError, "link"):
            canary.install_asset(self.asset("tar.gz"), path, self.destination)


if __name__ == "__main__":
    unittest.main()
