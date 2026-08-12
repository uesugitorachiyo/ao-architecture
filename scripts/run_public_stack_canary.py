#!/usr/bin/env python3
"""Install and verify the supported AO Stack from public release assets."""

from dataclasses import dataclass
import hashlib
from pathlib import Path, PurePosixPath
import shutil
import stat
import tarfile
import zipfile


TARGETS = ("linux-x86_64", "macos-aarch64", "windows-x86_64")


@dataclass(frozen=True)
class Asset:
    component: str
    version: str
    source_sha: str
    url: str
    sha256: str
    archive: str
    binary: str


def _asset(component, version, source_sha, target, filename, sha256, archive, binary):
    return Asset(
        component=component,
        version=version,
        source_sha=source_sha,
        url=(
            f"https://github.com/uesugitorachiyo/{component}/releases/download/"
            f"{version}/{filename}"
        ),
        sha256=sha256,
        archive=archive,
        binary=binary + (".exe" if target == "windows-x86_64" else ""),
    )


_COMPONENTS = {
    "ao2": (
        "v0.5.11",
        "8307795b3434af920f6cef088e56ca8fcc76775b",
        "ao2",
        {
            "linux-x86_64": ("ao2-0.5.11-linux-x86_64.tar.gz", "c62c204d520bf51b4c63caecf2a8f48840e44b2828e1e439c68da4994d1abc07", "tar.gz"),
            "macos-aarch64": ("ao2-0.5.11-macos-aarch64.tar.gz", "857fbe69e606ab99f07dffd3183e6f2d869b8efd4fc604e37efd16607308e6ab", "tar.gz"),
            "windows-x86_64": ("ao2-0.5.11-windows-x86_64.tar.gz", "327829e9e3e3edf3eeb3b48d3b1ead46af0fa47a768ee6e1843c285e8b1d2756", "tar.gz"),
        },
    ),
    "ao2-control-plane": (
        "v0.1.19",
        "5de3541e9007e12d95b125e7f911c02932e21479",
        "ao2-cp-server",
        {
            "linux-x86_64": ("ao2-control-plane-0.1.19-linux-x86_64.tar.gz", "588903471152cbc2cae1fc9d514d69b72c153b913a368cb6bf01da09c2789cbf", "tar.gz"),
            "macos-aarch64": ("ao2-control-plane-0.1.19-macos-aarch64.tar.gz", "06addc587bd282763c47d9ee4e36cb8ebea0c114881296569ef4d0b4dff86972", "tar.gz"),
            "windows-x86_64": ("ao2-control-plane-0.1.19-windows-x86_64.tar.gz", "c3528322730afd4a0c3988f9b2a23767f67febbf96b62340988546346ad00e05", "tar.gz"),
        },
    ),
    "ao-mission": (
        "v0.1.4",
        "cee287597024b5a1e990c6e272518236bc9e32fa",
        "ao-mission",
        {
            "linux-x86_64": ("ao-mission-0.1.4-linux-x86_64.tar.gz", "041d4b4ab076601bf6fe15335cb70a5d9f87301beb239e8e106b3ee4fd12f800", "tar.gz"),
            "macos-aarch64": ("ao-mission-0.1.4-macos-aarch64.tar.gz", "d8b418e42b57306862c75fc10e5c347109c13c144a18e240d2a2edba29c1a34e", "tar.gz"),
            "windows-x86_64": ("ao-mission-0.1.4-windows-x86_64.zip", "027ceba61e7b1d3655cce63a1ce4269824d7a5e3acf65fef5fabb0b539c53221", "zip"),
        },
    ),
    "ao-atlas": (
        "v0.2.0",
        "2bf243ce8d8c71d845754398238b14d1ab77d0e6",
        "ao-atlas",
        {
            "linux-x86_64": ("ao-atlas-v0.2.0-linux-x86_64.tar.gz", "121edad10e6775af809c4003b5b7820a06d3b140ff543a440a66b5c16987ac08", "tar.gz"),
            "macos-aarch64": ("ao-atlas-v0.2.0-macos-aarch64.tar.gz", "85678feba42d92d866e5f75c80cad80e5aa11dad18cb7292a396b16047b428a5", "tar.gz"),
            "windows-x86_64": ("ao-atlas-v0.2.0-windows-x86_64.tar.gz", "b53de90d5c2e69511e74e287eabd8437d87128892473843e576e366d1e4e62e7", "tar.gz"),
        },
    ),
    "ao-command": (
        "v0.1.2",
        "a728d90077c1340e295468e5017b5e166bc5bc7a",
        "ao-command",
        {
            "linux-x86_64": ("ao-command-0.1.2-linux-x86_64.tar.gz", "0d169a2434af12849c8e7865eb4b241651ca2edf34afbd3e4b378d678853c7be", "tar.gz"),
            "macos-aarch64": ("ao-command-0.1.2-macos-aarch64.tar.gz", "be5c246e73c2eb72a2f665a355e918841ffbbc105568df12c11f7597a538d9df", "tar.gz"),
            "windows-x86_64": ("ao-command-0.1.2-windows-x86_64.zip", "24ef4d1368a4cfd4754e3bef6ee7e6a3555eb655324efb2279168d1d3fb56414", "zip"),
        },
    ),
    "ao-forge": (
        "v0.1.4",
        "e104b47c2e14b6c0927b885e137907ad227aeb5c",
        "forge",
        {
            "linux-x86_64": ("ao-forge_Linux_x86_64.tar.gz", "19f15f022eed60f7acd97830835c0cb22eb0fb4df8046e4250e1d99904073ed2", "tar.gz"),
            "macos-aarch64": ("ao-forge_Darwin_arm64.tar.gz", "50a13927e4f83bbdb600f78a4107e5800e88512f48a7ce9e748ee19a31c2b0f4", "tar.gz"),
            "windows-x86_64": ("ao-forge_Windows_x86_64.zip", "a6250e975f0f7976bf5268d71c2f1791dd53c4413aebec9dff52b99989c204d5", "zip"),
        },
    ),
    "ao-covenant": (
        "v0.1.1",
        "2fd72a0426a747868826581612fa1dc9727b53b9",
        "covenant",
        {
            "linux-x86_64": ("ao-covenant_v0.1.1_linux_amd64", "f6820fdc7b99873071e7f68fc50d9bfd922750a2e788d9fca5aa8fb37cc8180b", "raw"),
            "macos-aarch64": ("ao-covenant_v0.1.1_darwin_amd64", "9a5ca7c6920c44b6e120d6c5bd8baf190b66e188d43485639c6fc5355190868e", "raw"),
            "windows-x86_64": ("ao-covenant_v0.1.1_windows_amd64.exe", "fd6e3a0033608d3f47dccb60f48191e4c4b2dc4fdce893c87d8ea96199610c5d", "raw"),
        },
    ),
}


def select_assets(target):
    if target not in TARGETS:
        raise ValueError(f"unsupported target: {target}")
    assets = []
    for component, (version, source_sha, binary, targets) in _COMPONENTS.items():
        filename, sha256, archive = targets[target]
        assets.append(
            _asset(component, version, source_sha, target, filename, sha256, archive, binary)
        )
    return tuple(assets)


def verify_digest(path, expected):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    actual = digest.hexdigest()
    if actual != expected:
        raise ValueError(f"SHA-256 mismatch: expected {expected}, got {actual}")


def _safe_name(name):
    if not name or "\\" in name:
        raise ValueError(f"unsafe archive path: {name!r}")
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"unsafe archive path: {name!r}")
    return path


def _copy_binary(source, destination, binary):
    destination.mkdir(parents=True, exist_ok=True)
    output = destination / binary
    with output.open("wb") as handle:
        shutil.copyfileobj(source, handle)
    output.chmod(output.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return output


def install_asset(asset, archive, destination):
    archive = Path(archive)
    destination = Path(destination)
    if asset.archive == "raw":
        if not archive.is_file() or archive.is_symlink():
            raise ValueError("raw asset must be a regular file")
        with archive.open("rb") as source:
            return (_copy_binary(source, destination, asset.binary),)

    matches = []
    if asset.archive == "tar.gz":
        with tarfile.open(archive, "r:gz") as bundle:
            for member in bundle.getmembers():
                name = _safe_name(member.name)
                if member.issym() or member.islnk():
                    raise ValueError(f"archive link is not allowed: {member.name}")
                if member.isdir():
                    continue
                if not member.isfile():
                    raise ValueError(f"archive entry is not a regular file: {member.name}")
                if name.name == asset.binary:
                    matches.append(member)
            if len(matches) > 1:
                raise ValueError(f"duplicate binary in archive: {asset.binary}")
            if not matches:
                raise ValueError(f"missing binary in archive: {asset.binary}")
            source = bundle.extractfile(matches[0])
            if source is None:
                raise ValueError(f"cannot read binary from archive: {asset.binary}")
            with source:
                return (_copy_binary(source, destination, asset.binary),)

    if asset.archive == "zip":
        with zipfile.ZipFile(archive) as bundle:
            for member in bundle.infolist():
                name = _safe_name(member.filename)
                mode = member.external_attr >> 16
                if stat.S_ISLNK(mode):
                    raise ValueError(f"archive link is not allowed: {member.filename}")
                if member.is_dir():
                    continue
                if name.name == asset.binary:
                    matches.append(member)
            if len(matches) > 1:
                raise ValueError(f"duplicate binary in archive: {asset.binary}")
            if not matches:
                raise ValueError(f"missing binary in archive: {asset.binary}")
            with bundle.open(matches[0]) as source:
                return (_copy_binary(source, destination, asset.binary),)

    raise ValueError(f"unsupported archive type: {asset.archive}")
