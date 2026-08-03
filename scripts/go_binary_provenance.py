from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any


TARGET_SETTINGS = {
    "linux-x86_64": ("linux", "amd64"),
    "linux-aarch64": ("linux", "arm64"),
    "macos-aarch64": ("darwin", "arm64"),
    "windows-x86_64": ("windows", "amd64"),
}


class BinaryProvenanceError(ValueError):
    pass


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise BinaryProvenanceError(f"duplicate binary metadata key: {key}")
        result[key] = value
    return result


def read_binary_metadata(binary: Path) -> dict[str, Any]:
    reader = Path(__file__).with_name("read_go_binary_metadata.go")
    environment = os.environ.copy()
    environment.update({"GOPROXY": "off", "GOSUMDB": "off", "GOTOOLCHAIN": "local"})
    try:
        result = subprocess.run(
            ["go", "run", str(reader), str(binary)],
            text=True,
            capture_output=True,
            check=False,
            env=environment,
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise BinaryProvenanceError(f"read Go build metadata: {exc}") from exc
    if result.returncode != 0:
        detail = result.stderr.strip() or f"reader exited {result.returncode}"
        raise BinaryProvenanceError(detail)
    try:
        metadata = json.loads(result.stdout, object_pairs_hook=_strict_object)
    except json.JSONDecodeError as exc:
        raise BinaryProvenanceError(f"binary metadata is malformed: {exc}") from exc
    if not isinstance(metadata, dict):
        raise BinaryProvenanceError("binary metadata must be an object")
    return metadata


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
