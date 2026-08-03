#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import re
import stat
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path, PurePath
from typing import Any, Iterable
from urllib.parse import quote


GENERATOR_NAME = "ao-architecture-go-supply-chain-candidate"
GENERATOR_VERSION = "1.0.0"
MAX_MODULE_JSON_BYTES = 8 << 20
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]{0,127}$")


class CandidateError(ValueError):
    pass


def strict_object(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CandidateError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")


def portable_path(value: PurePath) -> str:
    return str(value).replace("\\", "/")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_timestamp(value: str) -> str:
    if not value.endswith("Z"):
        raise CandidateError("generated timestamp must be UTC")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise CandidateError("generated timestamp must be UTC") from exc
    if parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z") != value:
        raise CandidateError("generated timestamp must be canonical UTC")
    return value


def resolve_regular(root: Path, value: str, label: str) -> Path:
    relative = Path(value)
    if relative.is_absolute() or not value or any(part in ("", ".", "..") for part in relative.parts):
        raise CandidateError(f"{label} has unsafe path")
    current = root
    for part in relative.parts:
        current = current / part
        try:
            mode = current.lstat().st_mode
        except OSError as exc:
            raise CandidateError(f"{label} must be a regular non-symlink file") from exc
        if stat.S_ISLNK(mode):
            raise CandidateError(f"{label} must be a regular non-symlink file")
    if not stat.S_ISREG(current.stat().st_mode):
        raise CandidateError(f"{label} must be a regular non-symlink file")
    try:
        current.resolve(strict=True).relative_to(root)
    except (OSError, ValueError) as exc:
        raise CandidateError(f"{label} has unsafe path") from exc
    return current


def resolve_output(root: Path, value: str) -> Path:
    relative = Path(value)
    if relative.is_absolute() or not value or any(part in ("", ".", "..") for part in relative.parts):
        raise CandidateError("output has unsafe path")
    current = root
    for part in relative.parts[:-1]:
        current = current / part
        if current.exists() and stat.S_ISLNK(current.lstat().st_mode):
            raise CandidateError("output has unsafe path")
    output = root / relative
    if output.exists() and (output.is_symlink() or any(output.iterdir())):
        raise CandidateError("output must be absent or empty")
    output.mkdir(parents=True, exist_ok=True)
    return output


def parse_module_stream(path: Path) -> tuple[str, list[dict[str, str]]]:
    if path.stat().st_size > MAX_MODULE_JSON_BYTES:
        raise CandidateError("module JSON exceeds size limit")
    text = path.read_text(encoding="utf-8")
    decoder = json.JSONDecoder(object_pairs_hook=strict_object)
    offset = 0
    values: list[dict[str, Any]] = []
    while offset < len(text):
        while offset < len(text) and text[offset].isspace():
            offset += 1
        if offset == len(text):
            break
        try:
            value, offset = decoder.raw_decode(text, offset)
        except json.JSONDecodeError as exc:
            raise CandidateError(f"module JSON is malformed: {exc}") from exc
        if not isinstance(value, dict):
            raise CandidateError("module JSON entries must be objects")
        values.append(value)
    if not values:
        raise CandidateError("module JSON is empty")
    main = [value for value in values if value.get("Main") is True]
    if len(main) != 1 or not isinstance(main[0].get("Path"), str):
        raise CandidateError("module JSON must contain one main module")
    components: list[dict[str, str]] = []
    seen: set[str] = set()
    for value in values:
        if value.get("Main") is True:
            continue
        if value.get("Replace") is not None:
            raise CandidateError("module replacements require an explicit producer contract")
        module_path = value.get("Path")
        version = value.get("Version")
        if not isinstance(module_path, str) or not module_path or not isinstance(version, str) or not version:
            raise CandidateError("dependency modules require path and version")
        if module_path in seen:
            raise CandidateError(f"duplicate module path: {module_path}")
        seen.add(module_path)
        component = {"path": module_path, "version": version}
        if isinstance(value.get("Sum"), str) and value["Sum"]:
            component["sum"] = value["Sum"]
        components.append(component)
    components.sort(key=lambda item: (item["path"], item["version"]))
    return main[0]["Path"], components


def validate_modules_against_lock(modules: list[dict[str, str]], lock_bytes: bytes) -> None:
    try:
        lock_lines = lock_bytes.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise CandidateError("dependency lock must be UTF-8") from exc
    for module in modules:
        prefix = f"{module['path']} {module['version']}"
        if not any(line.startswith(prefix + " ") or line.startswith(prefix + "/go.mod ") for line in lock_lines):
            raise CandidateError(f"module is absent from dependency lock: {module['path']}")


def build_sbom(repository: str, version: str, main_module: str, modules: list[dict[str, str]]) -> bytes:
    components = []
    for module in modules:
        component: dict[str, Any] = {
            "bom-ref": f"pkg:golang/{quote(module['path'], safe='/')}@{quote(module['version'], safe='')}",
            "name": module["path"],
            "purl": f"pkg:golang/{quote(module['path'], safe='/')}@{quote(module['version'], safe='')}",
            "type": "library",
            "version": module["version"],
        }
        if module.get("sum"):
            component["properties"] = [{"name": "ao:go-module-sum", "value": module["sum"]}]
        components.append(component)
    return json_bytes(
        {
            "bomFormat": "CycloneDX",
            "components": components,
            "metadata": {
                "component": {
                    "bom-ref": f"pkg:golang/{quote(main_module, safe='/')}@{quote(version, safe='')}",
                    "name": repository,
                    "purl": f"pkg:golang/{quote(main_module, safe='/')}@{quote(version, safe='')}",
                    "type": "application",
                    "version": version,
                },
                "tools": {
                    "components": [
                        {
                            "name": GENERATOR_NAME,
                            "type": "application",
                            "version": GENERATOR_VERSION,
                        }
                    ]
                },
            },
            "specVersion": "1.5",
            "version": 1,
        }
    )


def add_tar_bytes(archive: tarfile.TarFile, name: str, value: bytes, mode: int) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(value)
    info.mode = mode
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    info.mtime = 0
    archive.addfile(info, io.BytesIO(value))


def build_archive(entries: list[tuple[str, bytes, int]]) -> bytes:
    raw = io.BytesIO()
    with gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0, compresslevel=9) as compressed:
        with tarfile.open(fileobj=compressed, mode="w", format=tarfile.USTAR_FORMAT) as archive:
            for name, value, mode in sorted(entries, key=lambda item: item[0]):
                add_tar_bytes(archive, name, value, mode)
    return raw.getvalue()


def run(args: argparse.Namespace) -> None:
    root = args.workspace_root.resolve(strict=True)
    if not IDENTIFIER.fullmatch(args.repository) or not IDENTIFIER.fullmatch(args.target):
        raise CandidateError("repository and target must be bounded identifiers")
    if len(args.source_sha) != 40 or any(character not in "0123456789abcdef" for character in args.source_sha):
        raise CandidateError("source SHA must be a lowercase 40-character Git SHA")
    if not args.version or len(args.version) > 128 or not args.version.isascii():
        raise CandidateError("version must be bounded ASCII")
    if Path(args.archive_name).name != args.archive_name or not args.archive_name.endswith(".tar.gz"):
        raise CandidateError("archive name must be a .tar.gz basename")
    generated_at = parse_timestamp(args.generated_at_utc)
    binary = resolve_regular(root, args.binary, "binary")
    module_json = resolve_regular(root, args.module_json, "module JSON")
    dependency_lock = resolve_regular(root, args.dependency_lock, "dependency lock")
    license_file = resolve_regular(root, args.license, "license")
    notice_file = resolve_regular(root, args.notice, "notice") if args.notice else None
    output = resolve_output(root, args.out)

    lock_bytes = dependency_lock.read_bytes()
    main_module, modules = parse_module_stream(module_json)
    if dependency_lock.name == "go.mod" and modules:
        raise CandidateError("go.mod is allowed as the dependency lock only for a zero-dependency graph")
    validate_modules_against_lock(modules, lock_bytes)
    sbom = build_sbom(args.repository, args.version, main_module, modules)
    if sbom != build_sbom(args.repository, args.version, main_module, modules):
        raise CandidateError("SBOM regeneration is not deterministic")
    archive_entries = [
        ("LICENSE", license_file.read_bytes(), 0o644),
        ("SBOM.cdx.json", sbom, 0o644),
        (binary.name, binary.read_bytes(), 0o755),
        (dependency_lock.name, lock_bytes, 0o644),
    ]
    if notice_file is not None:
        archive_entries.append(("NOTICE", notice_file.read_bytes(), 0o644))
    archive = build_archive(archive_entries)
    archive_path = output / args.archive_name
    sbom_path = output / "SBOM.cdx.json"
    lock_path = output / dependency_lock.name
    archive_path.write_bytes(archive)
    sbom_path.write_bytes(sbom)
    lock_path.write_bytes(lock_bytes)

    output_relative = output.relative_to(root)
    evidence = {
        "archive_path": portable_path(output_relative / args.archive_name),
        "archive_sha256": sha256_bytes(archive),
        "dependency_lock_path": portable_path(output_relative / dependency_lock.name),
        "dependency_lock_sha256": sha256_bytes(lock_bytes),
        "deterministic_regeneration": True,
        "expected_components": [module["path"] for module in modules],
        "generated_at_utc": generated_at,
        "generator": {"name": GENERATOR_NAME, "version": GENERATOR_VERSION},
        "publication_attempted": False,
        "regeneration_sha256": sha256_bytes(sbom),
        "repository": args.repository,
        "sbom_path": portable_path(output_relative / "SBOM.cdx.json"),
        "sbom_sha256": sha256_bytes(sbom),
        "schema": "ao.supply-chain.sbom-evidence.v1",
        "source_sha": args.source_sha,
        "target": args.target,
        "version": args.version,
    }
    evidence_path = output / "supply-chain-evidence.json"
    evidence_path.write_bytes(json_bytes(evidence))
    print(f"archive={archive_path}")
    print(f"archive_sha256={sha256_file(archive_path)}")
    print(f"sbom_sha256={sha256_file(sbom_path)}")
    print(f"evidence={evidence_path}")
    print("publication_attempted=false")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a deterministic Go archive and CycloneDX evidence")
    parser.add_argument("--workspace-root", type=Path, required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--binary", required=True)
    parser.add_argument("--module-json", required=True)
    parser.add_argument("--dependency-lock", required=True)
    parser.add_argument("--license", required=True)
    parser.add_argument("--notice")
    parser.add_argument("--archive-name", required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    try:
        run(args)
    except (CandidateError, OSError, UnicodeError) as exc:
        print(f"build_go_supply_chain_candidate.py: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
