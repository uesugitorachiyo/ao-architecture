from __future__ import annotations

from typing import Any


TARGET_SETTINGS = {
    "linux-x86_64": ("linux", "amd64"),
    "macos-aarch64": ("darwin", "arm64"),
    "windows-x86_64": ("windows", "amd64"),
}


class BinaryProvenanceError(ValueError):
    pass


def validate_binary_provenance(
    metadata: dict[str, Any], source_sha: str, target: str
) -> dict[str, Any]:
    settings_value = metadata.get("Settings")
    if not isinstance(settings_value, list):
        raise BinaryProvenanceError("exact binary provenance is required")
    settings: dict[str, str] = {}
    for item in settings_value:
        if not isinstance(item, dict):
            raise BinaryProvenanceError("binary provenance settings must be objects")
        key = item.get("Key")
        value = item.get("Value")
        if not isinstance(key, str) or not isinstance(value, str) or key in settings:
            raise BinaryProvenanceError("binary provenance settings are invalid")
        settings[key] = value

    required = ("GOOS", "GOARCH", "vcs", "vcs.revision", "vcs.modified")
    if any(key not in settings for key in required):
        raise BinaryProvenanceError("exact binary provenance is required")
    if settings["vcs"] != "git":
        raise BinaryProvenanceError("binary source control must be git")
    if settings["vcs.revision"] != source_sha:
        raise BinaryProvenanceError("binary source revision does not match source SHA")
    if settings["vcs.modified"] != "false":
        raise BinaryProvenanceError("binary source must be unmodified")
    expected = TARGET_SETTINGS.get(target)
    if expected is None:
        raise BinaryProvenanceError("binary target is unsupported")
    if (settings["GOOS"], settings["GOARCH"]) != expected:
        raise BinaryProvenanceError("binary target does not match target")
    return {
        "goarch": settings["GOARCH"],
        "goos": settings["GOOS"],
        "vcs": settings["vcs"],
        "vcs_modified": False,
        "vcs_revision": settings["vcs.revision"],
    }
