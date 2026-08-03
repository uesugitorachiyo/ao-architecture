#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote

try:
    from scripts.go_binary_provenance import (
        BinaryProvenanceError,
        read_binary_metadata,
        validate_binary_provenance,
    )
except ModuleNotFoundError:
    from go_binary_provenance import (
        BinaryProvenanceError,
        read_binary_metadata,
        validate_binary_provenance,
    )


DEFAULT_MAX_BYTES = 1 << 20
MAX_ARCHIVE_BYTES = 320 << 20
MAX_ARCHIVE_EXPANDED_BYTES = 320 << 20
MAX_BINARY_BYTES = 256 << 20
MAX_MODULE_METADATA_BYTES = 8 << 20
MAX_DEPENDENCY_LOCK_BYTES = 16 << 20
EXPECTED_HOSTED = {
    "ao-architecture",
    "ao-arena",
    "ao-atlas",
    "ao-blueprint",
    "ao-command",
    "ao-covenant",
    "ao-crucible",
    "ao-forge",
    "ao-foundry",
    "ao-mission",
    "ao-promoter",
    "ao-sentinel",
    "ao2",
    "ao2-control-plane",
}
EXPECTED_LOCAL_ONLY = {"ao-hardening-runner", "ao-stack-evaluation"}
REQUIRED_BINDINGS = [
    "repository",
    "source_sha",
    "version",
    "target",
    "archive_sha256",
    "binary_name",
    "binary_sha256",
    "cryptographic_source_attestation",
    "module_metadata_sha256",
    "binary_provenance",
    "provenance_strength",
    "sbom_sha256",
    "generator_name",
    "generator_version",
    "dependency_lock_sha256",
    "generated_at_utc",
    "regeneration_sha256",
]


class PolicyError(ValueError):
    pass


def strict_object(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PolicyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path, label: str, maximum_bytes: int = DEFAULT_MAX_BYTES) -> dict[str, Any]:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise PolicyError(f"{label} cannot be read: {exc}") from exc
    if size > maximum_bytes:
        raise PolicyError(f"{label} exceeds size limit")
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_object)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PolicyError(f"{label} is malformed JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise PolicyError(f"{label} must be a JSON object")
    return value


def require_fields(value: dict[str, Any], fields: Iterable[str], label: str) -> None:
    for field in fields:
        if field not in value:
            raise PolicyError(f"{label}.{field} is required")


def parse_utc(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise PolicyError(f"{label} must be a UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise PolicyError(f"{label} must be a UTC timestamp") from exc
    return parsed.astimezone(timezone.utc)


def validate_digest(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise PolicyError(f"{label} must be a lowercase SHA-256")
    return value


def resolve_regular_file(root: Path, relative: Any, label: str) -> Path:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise PolicyError(f"{label} has unsafe path")
    parts = Path(relative).parts
    if any(part in ("", ".", "..") for part in parts):
        raise PolicyError(f"{label} has unsafe path")
    root = root.resolve(strict=True)
    candidate = root.joinpath(*parts)
    current = root
    for part in parts:
        current = current / part
        try:
            mode = current.lstat().st_mode
        except OSError as exc:
            raise PolicyError(f"{label} must reference a regular file: {exc}") from exc
        if stat.S_ISLNK(mode):
            raise PolicyError(f"{label} must reference a regular file")
    if not stat.S_ISREG(candidate.stat().st_mode):
        raise PolicyError(f"{label} must reference a regular file")
    try:
        candidate.resolve(strict=True).relative_to(root)
    except (OSError, ValueError) as exc:
        raise PolicyError(f"{label} has unsafe path") from exc
    return candidate


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_digest_match(path: Path, expected: Any, label: str) -> str:
    expected_digest = validate_digest(expected, label)
    if sha256(path) != expected_digest:
        raise PolicyError(f"{label} mismatch")
    return expected_digest


def repository_entry(inventory: dict[str, Any], repository: Any) -> dict[str, Any]:
    entries = inventory.get("repositories")
    if not isinstance(entries, list):
        raise PolicyError("inventory.repositories must be a list")
    matches = [entry for entry in entries if isinstance(entry, dict) and entry.get("repository") == repository]
    if len(matches) != 1:
        raise PolicyError("evidence repository must match exactly one inventory entry")
    return matches[0]


def binary_modules(metadata: dict[str, Any]) -> list[dict[str, str]]:
    dependencies = metadata.get("Deps", [])
    if not isinstance(dependencies, list):
        raise PolicyError("binary module dependencies must be a list")
    modules: list[dict[str, str]] = []
    seen: set[str] = set()
    for dependency in dependencies:
        if not isinstance(dependency, dict):
            raise PolicyError("binary module dependencies must be objects")
        if dependency.get("Replace") is not None:
            raise PolicyError("binary module replacements are unsupported")
        path = dependency.get("Path")
        version = dependency.get("Version")
        module_sum = dependency.get("Sum")
        if (
            not isinstance(path, str)
            or not path
            or path in seen
            or not isinstance(version, str)
            or not version
            or not isinstance(module_sum, str)
            or not module_sum
        ):
            raise PolicyError("binary module dependency metadata is invalid")
        seen.add(path)
        modules.append({"path": path, "version": version, "sum": module_sum})
    return sorted(modules, key=lambda item: (item["path"], item["version"]))


def validate_modules_against_lock(
    modules: list[dict[str, str]], lock: Path
) -> None:
    try:
        lines = lock.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise PolicyError("dependency lock must be UTF-8") from exc
    if lock.name == "go.mod" and modules:
        raise PolicyError("go.mod cannot bind a non-empty dependency graph")
    for module in modules:
        expected = f"{module['path']} {module['version']} {module['sum']}"
        if expected not in lines:
            raise PolicyError(
                f"binary module is absent from dependency lock: {module['path']}"
            )


def validate_sbom_identity(
    sbom: dict[str, Any],
    repository: str,
    version: str,
    metadata: dict[str, Any],
    modules: list[dict[str, str]],
    expected_components: Any,
    generator: dict[str, Any],
) -> None:
    main = metadata.get("Main")
    if not isinstance(main, dict) or not isinstance(main.get("Path"), str):
        raise PolicyError("binary main module metadata is invalid")
    main_purl = (
        f"pkg:golang/{quote(main['Path'], safe='/')}@{quote(version, safe='')}"
    )
    component = sbom.get("metadata", {}).get("component", {})
    expected_main = {
        "bom-ref": main_purl,
        "name": repository,
        "purl": main_purl,
        "type": "application",
        "version": version,
    }
    if not isinstance(component, dict) or any(
        component.get(key) != value for key, value in expected_main.items()
    ):
        raise PolicyError("SBOM application identity does not match binary metadata")
    tools = sbom.get("metadata", {}).get("tools", {}).get("components")
    expected_tool = {
        "name": generator["name"],
        "type": "application",
        "version": generator["version"],
    }
    if tools != [expected_tool]:
        raise PolicyError("SBOM generator identity does not match evidence")

    components = sbom.get("components")
    if not isinstance(components, list):
        raise PolicyError("component lists are required")
    if any(
        not isinstance(item, dict) or not isinstance(item.get("name"), str)
        for item in components
    ):
        raise PolicyError("SBOM component names must be unique strings")
    actual_names = [item["name"] for item in components]
    if len(set(actual_names)) != len(actual_names):
        raise PolicyError("SBOM component names must be unique strings")
    if actual_names != expected_components:
        raise PolicyError("SBOM component set does not match expected components")
    by_path = {module["path"]: module for module in modules}
    for component_entry in components:
        module = by_path[component_entry["name"]]
        module_purl = (
            f"pkg:golang/{quote(module['path'], safe='/')}@"
            f"{quote(module['version'], safe='')}"
        )
        expected_identity = {
            "bom-ref": module_purl,
            "name": module["path"],
            "purl": module_purl,
            "type": "library",
            "version": module["version"],
        }
        if any(
            component_entry.get(key) != value
            for key, value in expected_identity.items()
        ):
            raise PolicyError("SBOM component identity does not match binary metadata")
        properties = component_entry.get("properties")
        if properties != [{"name": "ao:go-module-sum", "value": module["sum"]}]:
            raise PolicyError("SBOM component sum does not match binary metadata")


def validate_contract_headers(inventory: dict[str, Any], policy: dict[str, Any]) -> list[str]:
    if inventory.get("schema") != "ao.architecture.distributable-inventory.v1":
        raise PolicyError("inventory schema mismatch")
    if inventory.get("status") != "active":
        raise PolicyError("inventory status must be active")
    if policy.get("schema") != "ao.architecture.sbom-policy.v1" or policy.get("status") != "active":
        raise PolicyError("policy schema or status mismatch")
    required_policy = {
        "format": "CycloneDX",
        "spec_version": "1.5",
        "require_archive_sha256": True,
        "require_dependency_lock_sha256": True,
        "require_deterministic_regeneration": True,
        "reject_unexpected_components": True,
        "release_or_publication_authorized": False,
    }
    for field, expected in required_policy.items():
        if policy.get(field) != expected:
            raise PolicyError(f"policy.{field} must be {expected!r}")
    if policy.get("required_bindings") != REQUIRED_BINDINGS:
        raise PolicyError("policy.required_bindings mismatch")
    required_classes = policy.get("required_for_classes")
    if required_classes != ["archive", "container", "public_release"]:
        raise PolicyError("policy required_for_classes mismatch")
    maximum = policy.get("maximum_evidence_bytes")
    freshness = policy.get("freshness_window_seconds")
    if not isinstance(maximum, int) or maximum < 1 or maximum > DEFAULT_MAX_BYTES:
        raise PolicyError("policy maximum_evidence_bytes is invalid")
    if not isinstance(freshness, int) or freshness < 1:
        raise PolicyError("policy freshness_window_seconds must be positive")
    boundaries = inventory.get("boundaries")
    if not isinstance(boundaries, dict) or any(
        boundaries.get(field) is not False
        for field in (
            "excluded_repositories_included",
            "lifecycle_reclassification_allowed",
            "release_or_publication_authorized",
        )
    ):
        raise PolicyError("inventory boundaries must remain false")
    return required_classes


def validate_contracts(inventory: dict[str, Any], policy: dict[str, Any]) -> None:
    required_classes = validate_contract_headers(inventory, policy)
    entries = inventory.get("repositories")
    if not isinstance(entries, list) or len(entries) != 16:
        raise PolicyError("inventory must classify 16 maintained repositories")
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise PolicyError("inventory repository entry must be an object")
        require_fields(
            entry,
            (
                "repository",
                "lifecycle",
                "distributable_classes",
                "executable",
                "archive_distributable",
                "container_distributable",
                "public_release_class",
                "artifact_names",
                "supported_targets",
                "root_license_policy",
                "sbom_policy_applicable",
            ),
            "inventory repository",
        )
        repository = entry.get("repository")
        if not isinstance(repository, str) or repository in seen:
            raise PolicyError("inventory repository names must be unique")
        seen.add(repository)
        expected_lifecycle = "active_hosted" if repository in EXPECTED_HOSTED else "active_local_only"
        if repository not in EXPECTED_HOSTED | EXPECTED_LOCAL_ONLY or entry.get("lifecycle") != expected_lifecycle:
            raise PolicyError(f"{repository} lifecycle mismatch")
        classes = entry.get("distributable_classes")
        if not isinstance(classes, list) or len(classes) != len(set(classes)):
            raise PolicyError(f"{repository} distributable_classes must be unique")
        if entry.get("root_license_policy") != "required":
            raise PolicyError(f"{repository} root_license_policy must be required")
        if bool(entry.get("executable")) != ("executable" in classes):
            raise PolicyError(f"{repository} executable classification mismatch")
        if bool(entry.get("archive_distributable")) != ("archive" in classes):
            raise PolicyError(f"{repository} archive classification mismatch")
        if bool(entry.get("container_distributable")) != ("container" in classes):
            raise PolicyError(f"{repository} container classification mismatch")
        applicable = bool(set(required_classes) & set(classes))
        if entry.get("sbom_policy_applicable") is not applicable:
            raise PolicyError(f"{repository} SBOM applicability mismatch")
        targets = entry.get("supported_targets")
        artifacts = entry.get("artifact_names")
        if not isinstance(targets, list) or not isinstance(artifacts, list):
            raise PolicyError(f"{repository} targets and artifacts must be lists")
        if entry.get("archive_distributable") and (not targets or not artifacts):
            raise PolicyError(f"{repository} archive targets and names are required")
        if repository == "ao-architecture" and (
            classes != ["source_only"] or entry.get("executable") or applicable
        ):
            raise PolicyError("ao-architecture must remain source-only")
        if repository in EXPECTED_LOCAL_ONLY and "local_only" not in classes:
            raise PolicyError(f"{repository} must remain local-only")
    if seen != EXPECTED_HOSTED | EXPECTED_LOCAL_ONLY:
        raise PolicyError("inventory maintained repository set mismatch")


def validate_release_alignment(inventory: dict[str, Any], classification: dict[str, Any]) -> None:
    if (
        classification.get("schema") != "ao.architecture.component-release-classification.v0.1"
        or classification.get("status") != "active"
    ):
        raise PolicyError("component release classification schema or status mismatch")
    entries = classification.get("repositories")
    if not isinstance(entries, list):
        raise PolicyError("component release classification repositories must be a list")
    by_repository: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("repository"), str):
            raise PolicyError("component release classification entry is invalid")
        repository = entry["repository"]
        if repository in by_repository:
            raise PolicyError("component release classification repository names must be unique")
        by_repository[repository] = entry
    if set(by_repository) != EXPECTED_HOSTED:
        raise PolicyError("component release classification repository set mismatch")
    inventory_entries = inventory.get("repositories")
    if not isinstance(inventory_entries, list):
        raise PolicyError("inventory.repositories must be a list")
    for entry in inventory_entries:
        if not isinstance(entry, dict) or entry.get("repository") not in EXPECTED_HOSTED:
            continue
        repository = entry["repository"]
        publication_allowed = by_repository[repository].get("publication_allowed")
        expected = "allowed" if publication_allowed is True else "conditional" if publication_allowed == "conditional" else "denied"
        if entry.get("public_release_class") != expected:
            raise PolicyError(f"{repository} public release classification mismatch")
        classes = entry.get("distributable_classes")
        if not isinstance(classes, list):
            raise PolicyError(f"{repository} distributable_classes must be a list")
        if ("public_release" in classes) != (publication_allowed is True or publication_allowed == "conditional"):
            raise PolicyError(f"{repository} public release applicability mismatch")


def verify(
    inventory: dict[str, Any],
    policy: dict[str, Any],
    evidence: dict[str, Any],
    root: Path,
    now: datetime,
    expected_source_sha: str,
    expected_version: str,
    expected_target: str,
) -> None:
    validate_contract_headers(inventory, policy)
    require_fields(
        evidence,
        (
            "schema",
            "repository",
            "source_sha",
            "version",
            "target",
            "archive_path",
            "archive_sha256",
            "binary_name",
            "binary_sha256",
            "binary_provenance",
            "cryptographic_source_attestation",
            "module_metadata_path",
            "module_metadata_sha256",
            "provenance_strength",
            "sbom_path",
            "sbom_sha256",
            "dependency_lock_path",
            "dependency_lock_sha256",
            "expected_components",
            "generator",
            "generated_at_utc",
            "regeneration_sha256",
            "deterministic_regeneration",
            "publication_attempted",
        ),
        "evidence",
    )
    if evidence.get("schema") != "ao.supply-chain.sbom-evidence.v2":
        raise PolicyError("evidence schema mismatch")
    entry = repository_entry(inventory, evidence.get("repository"))
    required_classes = policy.get("required_for_classes")
    classes = entry.get("distributable_classes")
    if not isinstance(required_classes, list) or not isinstance(classes, list):
        raise PolicyError("inventory and policy distributable classes must be lists")
    applicable = bool(set(required_classes) & set(classes))
    if entry.get("sbom_policy_applicable") is not applicable or not applicable:
        raise PolicyError("inventory SBOM applicability mismatch")
    if (
        len(expected_source_sha) != 40
        or any(character not in "0123456789abcdef" for character in expected_source_sha)
    ):
        raise PolicyError("expected source SHA must be a lowercase 40-character Git SHA")
    if not expected_version or len(expected_version) > 128 or not expected_version.isascii():
        raise PolicyError("expected version must be bounded ASCII")
    if evidence.get("source_sha") != expected_source_sha:
        raise PolicyError("source_sha does not match expected source")
    if evidence.get("version") != expected_version:
        raise PolicyError("version does not match expected version")
    if evidence.get("target") != expected_target:
        raise PolicyError("target does not match expected target")
    targets = entry.get("supported_targets")
    if not isinstance(targets, list) or evidence.get("target") not in targets:
        raise PolicyError("target is not supported by inventory")
    if evidence.get("publication_attempted") is not False:
        raise PolicyError("publication_attempted must be false")
    if evidence.get("cryptographic_source_attestation") is not False:
        raise PolicyError("cryptographic_source_attestation must be false")
    if evidence.get("provenance_strength") != "embedded_build_metadata":
        raise PolicyError("provenance_strength mismatch")
    generator = evidence.get("generator")
    if not isinstance(generator, dict) or not generator.get("name") or not generator.get("version"):
        raise PolicyError("generator name and version are required")
    generated = parse_utc(evidence.get("generated_at_utc"), "generated_at_utc")
    age = (now - generated).total_seconds()
    freshness = policy.get("freshness_window_seconds")
    if not isinstance(freshness, int) or freshness < 1:
        raise PolicyError("policy freshness_window_seconds must be positive")
    if age < 0 or age > freshness:
        raise PolicyError("evidence is stale")

    if policy.get("require_archive_sha256") is not True or not evidence.get("archive_sha256"):
        raise PolicyError("archive_sha256 is required")
    archive = resolve_regular_file(root, evidence.get("archive_path"), "archive_path")
    if archive.stat().st_size > MAX_ARCHIVE_BYTES:
        raise PolicyError("archive exceeds compressed size limit")
    require_digest_match(archive, evidence.get("archive_sha256"), "archive_sha256")
    binary_name = evidence.get("binary_name")
    if not isinstance(binary_name, str) or Path(binary_name).name != binary_name:
        raise PolicyError("binary_name must be a basename")
    module_metadata_path = resolve_regular_file(
        root, evidence.get("module_metadata_path"), "module_metadata_path"
    )
    if module_metadata_path.stat().st_size > MAX_MODULE_METADATA_BYTES:
        raise PolicyError("module metadata exceeds size limit")
    module_metadata_digest = require_digest_match(
        module_metadata_path,
        evidence.get("module_metadata_sha256"),
        "module_metadata_sha256",
    )
    module_metadata = load_json(module_metadata_path, "module metadata", 8 << 20)
    sbom_path = resolve_regular_file(root, evidence.get("sbom_path"), "sbom_path")
    maximum_evidence_bytes = int(
        policy.get("maximum_evidence_bytes", DEFAULT_MAX_BYTES)
    )
    if sbom_path.stat().st_size > maximum_evidence_bytes:
        raise PolicyError("SBOM exceeds size limit")
    sbom_digest = require_digest_match(sbom_path, evidence.get("sbom_sha256"), "sbom_sha256")
    if sbom_path.name != "SBOM.cdx.json":
        raise PolicyError("sbom_path must name SBOM.cdx.json")
    if policy.get("require_dependency_lock_sha256") is not True:
        raise PolicyError("policy must require dependency lock SHA-256")
    lock = resolve_regular_file(root, evidence.get("dependency_lock_path"), "dependency_lock_path")
    if lock.stat().st_size > MAX_DEPENDENCY_LOCK_BYTES:
        raise PolicyError("dependency lock exceeds size limit")
    require_digest_match(lock, evidence.get("dependency_lock_sha256"), "dependency_lock_sha256")
    required_archive_names = {
        binary_name,
        "go-modules.json",
        "SBOM.cdx.json",
        lock.name,
        "LICENSE",
    }
    if len(required_archive_names) != 5:
        raise PolicyError("archive member identities conflict")
    try:
        with tempfile.TemporaryDirectory() as temporary:
            extracted_binary = Path(temporary) / binary_name
            binary_digest = hashlib.sha256()
            archive_metadata_bytes: bytes | None = None
            archive_sbom_bytes: bytes | None = None
            archive_lock_bytes: bytes | None = None
            binary_found = False
            metadata_found = False
            seen: set[str] = set()
            aggregate_size = 0
            try:
                with tarfile.open(archive, "r:gz") as candidate_archive:
                    for count, member in enumerate(candidate_archive, start=1):
                        if count > 16:
                            raise PolicyError("archive member count exceeds limit")
                        if member.name in seen:
                            raise PolicyError("archive member names must be unique")
                        seen.add(member.name)
                        if not member.isfile() or Path(member.name).name != member.name:
                            raise PolicyError(
                                "archive members must be regular basenames"
                            )
                        aggregate_size += member.size
                        if aggregate_size > MAX_ARCHIVE_EXPANDED_BYTES:
                            raise PolicyError("archive exceeds expanded size limit")
                        limit = (
                            MAX_BINARY_BYTES
                            if member.name == binary_name
                            else MAX_MODULE_METADATA_BYTES
                            if member.name == "go-modules.json"
                            else DEFAULT_MAX_BYTES
                            if member.name in ("SBOM.cdx.json", "LICENSE", "NOTICE")
                            else MAX_DEPENDENCY_LOCK_BYTES
                            if member.name == lock.name
                            else DEFAULT_MAX_BYTES
                        )
                        if member.size < 0 or member.size > limit:
                            if member.name == "go-modules.json":
                                raise PolicyError(
                                    "archive module metadata exceeds size limit"
                                )
                            raise PolicyError("archive member exceeds size limit")
                        if member.name not in required_archive_names | {"NOTICE"}:
                            continue
                        source = candidate_archive.extractfile(member)
                        if source is None:
                            raise PolicyError("archive member cannot be read")
                        if member.name == binary_name:
                            with extracted_binary.open("wb") as destination:
                                total = 0
                                for chunk in iter(lambda: source.read(1024 * 1024), b""):
                                    total += len(chunk)
                                    if total > limit:
                                        raise PolicyError(
                                            "archive member exceeds size limit"
                                        )
                                    binary_digest.update(chunk)
                                    destination.write(chunk)
                            if total != member.size:
                                raise PolicyError("archive binary size mismatch")
                            binary_found = True
                        else:
                            value = source.read(limit + 1)
                            if len(value) != member.size:
                                raise PolicyError(
                                    f"archive {member.name} size mismatch"
                                )
                            if member.name == "go-modules.json":
                                archive_metadata_bytes = value
                                metadata_found = True
                            elif member.name == "SBOM.cdx.json":
                                archive_sbom_bytes = value
                            elif member.name == lock.name:
                                archive_lock_bytes = value
            except (tarfile.TarError, OSError) as exc:
                raise PolicyError(f"archive is malformed: {exc}") from exc
            if seen not in (required_archive_names, required_archive_names | {"NOTICE"}):
                raise PolicyError("archive member set is invalid")
            if not binary_found or not metadata_found or archive_metadata_bytes is None:
                raise PolicyError("archive binary and module metadata are required")
            if binary_digest.hexdigest() != validate_digest(
                evidence.get("binary_sha256"), "binary_sha256"
            ):
                raise PolicyError("binary_sha256 mismatch")
            if hashlib.sha256(archive_metadata_bytes).hexdigest() != module_metadata_digest:
                raise PolicyError("archive module metadata digest mismatch")
            if archive_metadata_bytes != module_metadata_path.read_bytes():
                raise PolicyError("archive module metadata does not match evidence")
            if archive_sbom_bytes != sbom_path.read_bytes():
                raise PolicyError("archive SBOM does not match evidence")
            if archive_lock_bytes != lock.read_bytes():
                raise PolicyError("archive dependency lock does not match evidence")
            extracted_binary.chmod(0o755)
            extracted_metadata = read_binary_metadata(extracted_binary)
        if extracted_metadata != module_metadata:
            raise PolicyError("module metadata does not match binary")
        binary_provenance = validate_binary_provenance(
            extracted_metadata, expected_source_sha, expected_target
        )
    except BinaryProvenanceError as exc:
        raise PolicyError(str(exc)) from exc
    if evidence.get("binary_provenance") != binary_provenance:
        raise PolicyError("binary_provenance does not match module metadata")
    modules = binary_modules(extracted_metadata)
    expected_module_paths = [module["path"] for module in modules]
    if evidence.get("expected_components") != expected_module_paths:
        raise PolicyError("expected components do not match binary metadata")
    validate_modules_against_lock(modules, lock)

    sbom = load_json(sbom_path, "SBOM", maximum_evidence_bytes)
    if sbom.get("bomFormat") != "CycloneDX" or sbom.get("specVersion") != "1.5":
        raise PolicyError("SBOM must be CycloneDX 1.5")
    expected_components = evidence.get("expected_components")
    if not isinstance(expected_components, list):
        raise PolicyError("component lists are required")
    if policy.get("reject_unexpected_components") is not True:
        raise PolicyError("unexpected SBOM components must be rejected")
    validate_sbom_identity(
        sbom,
        evidence["repository"],
        evidence["version"],
        extracted_metadata,
        modules,
        expected_components,
        generator,
    )
    if policy.get("require_deterministic_regeneration") is not True or evidence.get("deterministic_regeneration") is not True:
        raise PolicyError("deterministic regeneration is required")
    regeneration = validate_digest(evidence.get("regeneration_sha256"), "regeneration_sha256")
    if regeneration != sbom_digest:
        raise PolicyError("regeneration_sha256 does not match SBOM")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify an AO distributable SBOM against stack policy")
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--release-classification", type=Path)
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--workspace-root", type=Path)
    parser.add_argument("--expected-source-sha")
    parser.add_argument("--expected-version")
    parser.add_argument("--expected-target")
    parser.add_argument("--now")
    parser.add_argument("--validate-contracts", action="store_true")
    args = parser.parse_args()
    try:
        inventory = load_json(args.inventory, "inventory")
        policy = load_json(args.policy, "policy")
        policy_limit = policy.get("maximum_evidence_bytes", DEFAULT_MAX_BYTES)
        if not isinstance(policy_limit, int) or policy_limit < 1 or policy_limit > DEFAULT_MAX_BYTES:
            raise PolicyError("policy maximum_evidence_bytes is invalid")
        if args.validate_contracts:
            validate_contracts(inventory, policy)
            if args.release_classification is None:
                raise PolicyError("--release-classification is required for contract validation")
            validate_release_alignment(
                inventory,
                load_json(args.release_classification, "component release classification"),
            )
            print("verify_supply_chain_policy.py: supply-chain contracts verified")
            return 0
        if args.evidence is None or args.workspace_root is None or args.now is None:
            raise PolicyError("--evidence, --workspace-root, and --now are required for evidence verification")
        if not args.expected_source_sha or not args.expected_version or not args.expected_target:
            raise PolicyError("exact source, version, and target bindings are required")
        workspace_root = args.workspace_root.resolve(strict=True)
        evidence_input = (
            args.evidence
            if args.evidence.is_absolute()
            else Path(os.path.abspath(args.evidence))
        )
        evidence_candidate = evidence_input.parent.resolve(strict=True) / evidence_input.name
        try:
            evidence_relative = evidence_candidate.relative_to(workspace_root)
        except ValueError as exc:
            raise PolicyError("evidence must be inside workspace root") from exc
        evidence_path = resolve_regular_file(
            workspace_root, str(evidence_relative), "evidence"
        )
        evidence = load_json(evidence_path, "evidence", policy_limit)
        verify(
            inventory,
            policy,
            evidence,
            evidence_path.parent,
            parse_utc(args.now, "now"),
            args.expected_source_sha,
            args.expected_version,
            args.expected_target,
        )
    except (OSError, PolicyError) as exc:
        print(f"verify_supply_chain_policy.py: {exc}", file=sys.stderr)
        return 1
    print("verify_supply_chain_policy.py: supply-chain policy verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
