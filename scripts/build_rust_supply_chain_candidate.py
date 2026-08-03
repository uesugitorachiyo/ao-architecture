#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.9/3.10 compatibility.
    try:
        import tomli as tomllib
    except ModuleNotFoundError:
        tomllib = None  # type: ignore[assignment]

try:
    from scripts.build_go_supply_chain_candidate import (
        CandidateError,
        IDENTIFIER,
        build_archive,
        json_bytes,
        parse_timestamp,
        resolve_output,
        resolve_regular,
        sha256_bytes,
        sha256_file,
        strict_object,
    )
    from scripts.rust_binary_provenance import (
        RustProvenanceError,
        normalize_rust_metadata,
        read_rust_binary_metadata,
        validate_rust_provenance,
    )
except ModuleNotFoundError:
    from build_go_supply_chain_candidate import (
        CandidateError,
        IDENTIFIER,
        build_archive,
        json_bytes,
        parse_timestamp,
        resolve_output,
        resolve_regular,
        sha256_bytes,
        sha256_file,
        strict_object,
    )
    from rust_binary_provenance import (
        RustProvenanceError,
        normalize_rust_metadata,
        read_rust_binary_metadata,
        validate_rust_provenance,
    )


GENERATOR_NAME = "ao-architecture-rust-supply-chain-candidate"
GENERATOR_VERSION = "1.0.0"
MAX_METADATA_BYTES = 4096


def load_metadata(path: Path) -> dict[str, Any]:
    if path.stat().st_size > MAX_METADATA_BYTES:
        raise CandidateError("Rust binary metadata exceeds size limit")
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_object)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise CandidateError(f"Rust binary metadata is malformed: {exc}") from exc
    try:
        return normalize_rust_metadata(value)
    except RustProvenanceError as exc:
        raise CandidateError(str(exc)) from exc


def cargo_packages(lock_bytes: bytes) -> list[dict[str, str]]:
    if tomllib is None:
        raise CandidateError("Rust evidence requires Python 3.11 tomllib or the tomli compatibility package")
    try:
        text = lock_bytes.decode("utf-8")
        document = tomllib.loads(text)
    except (UnicodeError, ValueError) as exc:
        raise CandidateError(f"Cargo.lock is malformed: {exc}") from exc
    if document.get("version") not in (3, 4) or not isinstance(document.get("package"), list) or not document["package"]:
        raise CandidateError("Cargo.lock must contain a supported package list")
    packages: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in document["package"]:
        if not isinstance(item, dict):
            raise CandidateError("Cargo.lock package entries must be objects")
        name = item.get("name")
        version = item.get("version")
        source = item.get("source", "workspace")
        checksum = item.get("checksum", "")
        if not all(isinstance(value, str) and value for value in (name, version, source)):
            raise CandidateError("Cargo.lock package identity is invalid")
        if checksum and (not isinstance(checksum, str) or len(checksum) != 64 or any(c not in "0123456789abcdef" for c in checksum)):
            raise CandidateError(f"Cargo.lock checksum is invalid: {name}")
        identity = (name, version, source)
        if identity in seen:
            raise CandidateError(f"Cargo.lock package identity is duplicated: {name}")
        seen.add(identity)
        packages.append({"checksum": checksum, "name": name, "source": source, "version": version})
    return sorted(packages, key=lambda item: (item["name"], item["version"], item["source"]))


def component_purl(package: dict[str, str]) -> str:
    base = f"pkg:cargo/{quote(package['name'], safe='')}@{quote(package['version'], safe='')}"
    if package["source"] == "workspace":
        return base
    return f"{base}?source={quote(package['source'], safe='')}"


def component_packages(repository: str, version: str, packages: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        package
        for package in packages
        if not (
            package["name"] == repository
            and package["version"] == version
            and package["source"] == "workspace"
        )
    ]


def build_sbom(repository: str, version: str, packages: list[dict[str, str]]) -> bytes:
    components: list[dict[str, Any]] = []
    for package in component_packages(repository, version, packages):
        purl = component_purl(package)
        properties = [{"name": "ao:cargo-source", "value": package["source"]}]
        if package["checksum"]:
            properties.append({"name": "ao:cargo-checksum", "value": package["checksum"]})
        components.append(
            {
                "bom-ref": purl,
                "name": package["name"],
                "properties": properties,
                "purl": purl,
                "type": "library",
                "version": package["version"],
            }
        )
    application_purl = f"pkg:cargo/{quote(repository, safe='')}@{quote(version, safe='')}"
    return json_bytes(
        {
            "bomFormat": "CycloneDX",
            "components": components,
            "metadata": {
                "component": {
                    "bom-ref": application_purl,
                    "name": repository,
                    "purl": application_purl,
                    "type": "application",
                    "version": version,
                },
                "tools": {
                    "components": [
                        {"name": GENERATOR_NAME, "type": "application", "version": GENERATOR_VERSION}
                    ]
                },
            },
            "specVersion": "1.5",
            "version": 1,
        }
    )


def run(args: argparse.Namespace) -> None:
    root = args.workspace_root.resolve(strict=True)
    if not IDENTIFIER.fullmatch(args.repository) or not IDENTIFIER.fullmatch(args.target):
        raise CandidateError("repository and target must be bounded identifiers")
    if len(args.source_sha) != 40 or any(c not in "0123456789abcdef" for c in args.source_sha):
        raise CandidateError("source SHA must be a lowercase 40-character Git SHA")
    if not args.version or len(args.version) > 128 or not args.version.isascii():
        raise CandidateError("version must be bounded ASCII")
    if Path(args.archive_name).name != args.archive_name or not args.archive_name.endswith(".tar.gz"):
        raise CandidateError("archive name must be a .tar.gz basename")
    generated_at = parse_timestamp(args.generated_at_utc)
    binary = resolve_regular(root, args.binary, "binary")
    metadata_input = resolve_regular(root, args.metadata_json, "Rust binary metadata")
    dependency_lock = resolve_regular(root, args.dependency_lock, "dependency lock")
    if dependency_lock.name != "Cargo.lock":
        raise CandidateError("Rust dependency lock must be Cargo.lock")
    license_file = resolve_regular(root, args.license, "license")
    notice_file = resolve_regular(root, args.notice, "notice") if args.notice else None
    output = resolve_output(root, args.out)

    metadata = load_metadata(metadata_input)
    embedded = read_rust_binary_metadata(binary)
    if metadata != embedded:
        raise CandidateError("Rust metadata does not match binary")
    lock_bytes = dependency_lock.read_bytes()
    if len(lock_bytes) > 16 << 20:
        raise CandidateError("Cargo.lock exceeds size limit")
    packages = cargo_packages(lock_bytes)
    lock_digest = sha256_bytes(lock_bytes)
    if embedded["cargo_lock_sha256"] != lock_digest:
        raise CandidateError("Rust binary Cargo.lock digest does not match dependency lock")
    provenance = validate_rust_provenance(
        embedded,
        args.repository,
        args.source_sha,
        args.version,
        args.target,
        lock_digest,
    )
    sbom = build_sbom(args.repository, args.version, packages)
    if sbom != build_sbom(args.repository, args.version, packages):
        raise CandidateError("SBOM regeneration is not deterministic")
    metadata_bytes = json_bytes(metadata)
    archive_entries = [
        ("Cargo.lock", lock_bytes, 0o644),
        ("LICENSE", license_file.read_bytes(), 0o644),
        ("SBOM.cdx.json", sbom, 0o644),
        (binary.name, binary.read_bytes(), 0o755),
        ("rust-binary-metadata.json", metadata_bytes, 0o644),
    ]
    if notice_file is not None:
        archive_entries.append(("NOTICE", notice_file.read_bytes(), 0o644))
    archive = build_archive(archive_entries)
    archive_path = output / args.archive_name
    archive_path.write_bytes(archive)
    (output / "Cargo.lock").write_bytes(lock_bytes)
    (output / "SBOM.cdx.json").write_bytes(sbom)
    (output / "rust-binary-metadata.json").write_bytes(metadata_bytes)
    evidence = {
        "archive_path": args.archive_name,
        "archive_sha256": sha256_bytes(archive),
        "binary_name": binary.name,
        "binary_provenance": provenance,
        "binary_sha256": sha256_file(binary),
        "cryptographic_source_attestation": False,
        "dependency_lock_path": "Cargo.lock",
        "dependency_lock_sha256": sha256_bytes(lock_bytes),
        "deterministic_regeneration": True,
        "expected_components": [
            component_purl(package)
            for package in component_packages(args.repository, args.version, packages)
        ],
        "generated_at_utc": generated_at,
        "generator": {"name": GENERATOR_NAME, "version": GENERATOR_VERSION},
        "module_metadata_path": "rust-binary-metadata.json",
        "module_metadata_sha256": sha256_bytes(metadata_bytes),
        "publication_attempted": False,
        "provenance_strength": "embedded_build_metadata",
        "regeneration_sha256": sha256_bytes(sbom),
        "repository": args.repository,
        "sbom_path": "SBOM.cdx.json",
        "sbom_sha256": sha256_bytes(sbom),
        "schema": "ao.supply-chain.sbom-evidence.v2",
        "source_sha": args.source_sha,
        "target": args.target,
        "version": args.version,
    }
    (output / "supply-chain-evidence.json").write_bytes(json_bytes(evidence))
    print(f"archive={archive_path}")
    print(f"archive_sha256={sha256_file(archive_path)}")
    print(f"sbom_sha256={sha256_bytes(sbom)}")
    print(f"evidence={output / 'supply-chain-evidence.json'}")
    print("publication_attempted=false")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build deterministic Rust CycloneDX evidence")
    parser.add_argument("--workspace-root", type=Path, required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--binary", required=True)
    parser.add_argument("--metadata-json", required=True)
    parser.add_argument("--dependency-lock", required=True)
    parser.add_argument("--license", required=True)
    parser.add_argument("--notice")
    parser.add_argument("--archive-name", required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    try:
        run(args)
    except (CandidateError, RustProvenanceError, OSError, UnicodeError) as exc:
        print(f"build_rust_supply_chain_candidate.py: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
