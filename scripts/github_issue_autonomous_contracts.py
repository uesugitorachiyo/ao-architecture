from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"
AUTONOMOUS_CONTRACTS = {
    "immutable_run_envelope": (
        "ao.architecture.autonomous-issue-repair.run-envelope.v1",
        "stack/schemas/github-issue-repair/immutable-run-envelope-v1.schema.json",
        "stack/fixtures/github-issue-repair/v1/immutable-run-envelope.valid.json",
    ),
    "bounded_discovery_result": (
        "ao.architecture.autonomous-issue-repair.discovery-result.v1",
        "stack/schemas/github-issue-repair/bounded-discovery-result-v1.schema.json",
        "stack/fixtures/github-issue-repair/v1/bounded-discovery-result.valid.json",
    ),
    "candidate_decision": (
        "ao.architecture.autonomous-issue-repair.candidate-decision.v1",
        "stack/schemas/github-issue-repair/candidate-decision-v1.schema.json",
        "stack/fixtures/github-issue-repair/v1/candidate-decision.valid.json",
    ),
    "append_only_event": (
        "ao.architecture.autonomous-issue-repair.event.v1",
        "stack/schemas/github-issue-repair/append-only-event-v1.schema.json",
        "stack/fixtures/github-issue-repair/v1/append-only-event.valid.json",
    ),
    "checkpoint": (
        "ao.architecture.autonomous-issue-repair.checkpoint.v1",
        "stack/schemas/github-issue-repair/checkpoint-v1.schema.json",
        "stack/fixtures/github-issue-repair/v1/checkpoint.valid.json",
    ),
    "governance_decision": (
        "ao.architecture.autonomous-issue-repair.governance-decision.v1",
        "stack/schemas/github-issue-repair/governance-decision-v1.schema.json",
        "stack/fixtures/github-issue-repair/v1/governance-decision.valid.json",
    ),
    "reviewer_independence": (
        "ao.architecture.autonomous-issue-repair.reviewer-independence.v1",
        "stack/schemas/github-issue-repair/reviewer-independence-v1.schema.json",
        "stack/fixtures/github-issue-repair/v1/reviewer-independence.valid.json",
    ),
    "github_action_digest": (
        "ao.architecture.autonomous-issue-repair.github-action-digest.v1",
        "stack/schemas/github-issue-repair/github-action-digest-v1.schema.json",
        "stack/fixtures/github-issue-repair/v1/github-action-digest.valid.json",
    ),
}


def _canonical_sha256(document: dict[str, Any], excluded_field: str) -> str:
    canonical = {
        key: value for key, value in document.items() if key != excluded_field
    }
    payload = json.dumps(
        canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def _resolve_local_ref(root_schema: dict[str, Any], reference: str) -> Any:
    if not reference.startswith("#/"):
        raise ValueError(f"unsupported non-local schema reference: {reference}")
    value: Any = root_schema
    for token in reference[2:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        value = value[token]
    return value


def _matches_type(value: Any, expected: str) -> bool:
    matchers = {
        "object": lambda item: isinstance(item, dict),
        "array": lambda item: isinstance(item, list),
        "string": lambda item: isinstance(item, str),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "number": lambda item: isinstance(item, (int, float))
        and not isinstance(item, bool),
        "boolean": lambda item: isinstance(item, bool),
        "null": lambda item: item is None,
    }
    matcher = matchers.get(expected)
    return matcher(value) if matcher else False


def _validate_schema_value(
    schema: dict[str, Any],
    value: Any,
    path: str,
    root_schema: dict[str, Any],
) -> list[str]:
    if "$ref" in schema:
        try:
            resolved = _resolve_local_ref(root_schema, schema["$ref"])
        except (KeyError, TypeError, ValueError) as exc:
            return [f"{path}: {exc}"]
        return _validate_schema_value(resolved, value, path, root_schema)

    errors: list[str] = []
    expected_type = schema.get("type")
    if isinstance(expected_type, list):
        type_ok = any(_matches_type(value, item) for item in expected_type)
    elif isinstance(expected_type, str):
        type_ok = _matches_type(value, expected_type)
    else:
        type_ok = True
    if not type_ok:
        return [f"{path}: expected {expected_type}"]
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: must be one of {schema['enum']}")

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        for field in schema.get("required", []):
            if field not in value:
                errors.append(f"{path}.{field}: required property is missing")
        if schema.get("additionalProperties") is False:
            for field in value:
                if field not in properties:
                    errors.append(f"{path}.{field}: additional property is not allowed")
        for field, item in value.items():
            child_schema = properties.get(field)
            if isinstance(child_schema, dict):
                errors.extend(
                    _validate_schema_value(
                        child_schema, item, f"{path}.{field}", root_schema
                    )
                )

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path}: must contain at least {schema['minItems']} items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{path}: must contain at most {schema['maxItems']} items")
        if schema.get("uniqueItems"):
            encoded = [
                json.dumps(item, sort_keys=True, separators=(",", ":"))
                for item in value
            ]
            if len(encoded) != len(set(encoded)):
                errors.append(f"{path}: items must be unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(
                    _validate_schema_value(
                        item_schema, item, f"{path}[{index}]", root_schema
                    )
                )

    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{path}: must contain at least {schema['minLength']} characters")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(f"{path}: must contain at most {schema['maxLength']} characters")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.fullmatch(pattern, value) is None:
            errors.append(f"{path}: does not match required pattern")
        if schema.get("format") == "date-time" and _parse_timestamp(value) is None:
            errors.append(f"{path}: must be an RFC 3339 timestamp")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: must be at least {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: must be at most {schema['maximum']}")
    return errors


def validate_contract_instance(
    name: str,
    instance: dict[str, Any],
    *,
    reference_time: datetime | None = None,
    root: Path = ROOT,
) -> list[str]:
    metadata = AUTONOMOUS_CONTRACTS.get(name)
    if metadata is None:
        return [f"unknown autonomous repair contract: {name}"]
    try:
        schema = json.loads((root / metadata[1]).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{name} schema could not be loaded: {exc}"]
    errors = _validate_schema_value(schema, instance, "$", schema)
    if errors:
        return errors

    digest_fields = {
        "immutable_run_envelope": (
            "canonical_digest",
            "run envelope canonical_digest does not match canonical fields",
        ),
        "append_only_event": (
            "event_digest",
            "event_digest does not match canonical event fields",
        ),
        "checkpoint": (
            "checkpoint_digest",
            "checkpoint_digest does not match canonical checkpoint fields",
        ),
        "github_action_digest": (
            "action_digest",
            "github action digest does not match canonical action fields",
        ),
    }
    if name in digest_fields:
        field, error = digest_fields[name]
        if instance[field] != _canonical_sha256(instance, field):
            errors.append(error)

    if name == "github_action_digest":
        approved_at = _parse_timestamp(instance["approved_at"])
        expires_at = _parse_timestamp(instance["expires_at"])
        now = reference_time or datetime.now(timezone.utc)
        if (
            approved_at is not None
            and expires_at is not None
            and approved_at >= expires_at
        ):
            errors.append("github action digest expiry must follow approval")
        if expires_at is not None and expires_at <= now.astimezone(timezone.utc):
            errors.append("github action digest approval is stale")
        if any(
            check["head_sha"] != instance["head_sha"]
            for check in instance["required_checks"]
        ):
            errors.append("github action digest checks must bind the exact head SHA")
    elif name == "governance_decision":
        governance_class = instance["governance_class"]
        if governance_class in {"external", "unknown"}:
            if (
                instance["merge"]["authorized"] is not False
                or instance["merge"]["mode"] != "never"
            ):
                errors.append(f"{governance_class} governance must deny merge")
            if instance["push_target"] != "operator_owned_fork":
                errors.append(
                    f"{governance_class} governance must use an operator-owned fork"
                )
            if instance["pull_request_mode"] != "upstream_draft_only":
                errors.append(
                    f"{governance_class} governance must remain upstream draft only"
                )
        if (
            governance_class == "team"
            and instance["merge"]["authorized"]
            and (
                instance["merge"]["approval_kind"]
                not in {"independent_human", "codeowner"}
                or instance["merge"]["approval_head_sha"] != instance["head_sha"]
            )
        ):
            errors.append("team merge requires independent approval on the exact head SHA")
        if any(
            check["head_sha"] != instance["head_sha"]
            for check in instance["required_checks"]
        ):
            errors.append("governance checks must bind the exact head SHA")
    elif name == "reviewer_independence":
        if (
            instance["status"] != "independent"
            and instance["satisfies_team_merge_gate"]
        ):
            errors.append(
                "only an independent reviewer may satisfy the team merge gate"
            )
    elif name == "bounded_discovery_result":
        if len(instance["issues"]) > instance["snapshot_limit"]:
            errors.append("discovery issues must not exceed snapshot_limit")
        if len(instance["candidates"]) > instance["candidate_limit"]:
            errors.append("discovery candidates must not exceed candidate_limit")
        if len(instance["response_digests"]) != instance["page_count"]:
            errors.append("discovery response digests must match page_count")
        candidate_numbers = {
            candidate["issue_number"] for candidate in instance["candidates"]
        }
        selected = instance["selected_issue_number"]
        if selected is not None and selected not in candidate_numbers:
            errors.append("selected issue must be present in candidates")
    elif name == "immutable_run_envelope":
        if (
            instance["routing"]["default_branch"]
            != instance["trigger"]["default_branch"]
            or instance["routing"]["pinned_base_commit"]
            != instance["trigger"]["pinned_base_commit"]
        ):
            errors.append("run envelope routing must bind the trigger revision")
        if instance["governance"]["ownership_class"] in {"external", "unknown"}:
            forbidden = {"open_ready_pr", "request_merge_queue", "auto_merge"}
            if forbidden.intersection(instance["governance"]["allowed_actions"]):
                errors.append(
                    "external or unknown run envelope must remain draft-only"
                )
    elif name == "append_only_event":
        if instance["sequence"] == 1 and instance["previous_event_digest"] is not None:
            errors.append("first event must not declare a predecessor")
        if instance["sequence"] > 1 and instance["previous_event_digest"] is None:
            errors.append("non-initial event must bind its predecessor")
    return errors


def validate_successor_envelope(
    predecessor: dict[str, Any], successor: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    for field in ("repository", "canonical_url", "pinned_base_commit"):
        if successor["trigger"].get(field) != predecessor["trigger"].get(field):
            errors.append(f"successor trigger.{field} must match predecessor")
    if (
        successor["governance"]["ownership_class"]
        != predecessor["governance"]["ownership_class"]
    ):
        errors.append("successor governance.ownership_class must match predecessor")
    for field in ("snapshot_limit", "candidate_limit", "selected_limit"):
        if successor["discovery"][field] > predecessor["discovery"][field]:
            errors.append(f"successor discovery.{field} must not exceed predecessor")
    for field, value in predecessor["budgets"].items():
        if successor["budgets"][field] > value:
            errors.append(f"successor budgets.{field} must not exceed predecessor")
    predecessor_allowed = set(predecessor["governance"]["allowed_actions"])
    successor_allowed = set(successor["governance"]["allowed_actions"])
    if not successor_allowed.issubset(predecessor_allowed):
        errors.append("successor allowed_actions must be a subset of predecessor")
    predecessor_denied = set(predecessor["governance"]["denied_actions"])
    successor_denied = set(successor["governance"]["denied_actions"])
    if not successor_denied.issuperset(predecessor_denied):
        errors.append("successor denied_actions must include predecessor denials")
    previous_expiry = _parse_timestamp(predecessor["expires_at"])
    successor_expiry = _parse_timestamp(successor["expires_at"])
    if (
        previous_expiry is not None
        and successor_expiry is not None
        and successor_expiry > previous_expiry
    ):
        errors.append("successor expires_at must not extend predecessor")
    if successor.get("predecessor_digest") != predecessor.get("canonical_digest"):
        errors.append("successor predecessor_digest must match predecessor")
    lineage = successor.get("lineage", {})
    if (
        lineage.get("kind") != "narrower_successor"
        or lineage.get("predecessor_run_id") != predecessor.get("run_id")
        or lineage.get("predecessor_digest") != predecessor.get("canonical_digest")
    ):
        errors.append("successor lineage must bind the predecessor")
    return errors


def validate_checkpoint_event_linkage(
    checkpoint: dict[str, Any], event: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    if checkpoint.get("run_id") != event.get("run_id"):
        errors.append("checkpoint run_id must match event run_id")
    if checkpoint.get("run_envelope_digest") != event.get("run_envelope_digest"):
        errors.append("checkpoint run_envelope_digest must match event")
    if checkpoint.get("last_event_sequence") != event.get("sequence"):
        errors.append("checkpoint last_event_sequence must match event sequence")
    if checkpoint.get("last_event_digest") != event.get("event_digest"):
        errors.append("checkpoint last_event_digest must match event digest")
    return errors


def validate_autonomous_family(
    document: dict[str, Any], *, root: Path = ROOT
) -> list[str]:
    errors: list[str] = []
    family = document.get("autonomous_repair_contract_family")
    if not isinstance(family, dict):
        return ["autonomous_repair_contract_family is required"]
    expected_fields = {
        "status",
        "predecessor",
        "validation_reference_time",
        "contracts",
        "bounds",
        "safety",
    }
    if set(family) != expected_fields:
        errors.append(
            "autonomous_repair_contract_family fields must exactly match the strict schema"
        )
    if family.get("status") != "current_pair_only":
        errors.append("autonomous_repair_contract_family.status must be current_pair_only")
    if family.get("predecessor") != "not_applicable_no_predecessor":
        errors.append(
            "autonomous_repair_contract_family.predecessor must not invent a predecessor"
        )
    reference_time = _parse_timestamp(family.get("validation_reference_time"))
    if reference_time is None:
        errors.append(
            "autonomous_repair_contract_family.validation_reference_time must be an RFC 3339 timestamp"
        )

    contracts = family.get("contracts")
    entries = (
        {
            entry.get("name"): entry
            for entry in contracts
            if isinstance(entry, dict) and isinstance(entry.get("name"), str)
        }
        if isinstance(contracts, list)
        else {}
    )
    if isinstance(contracts, list) and len(entries) != len(contracts):
        errors.append("autonomous repair contracts must be unique objects")
    instances: dict[str, dict[str, Any]] = {}
    for name, (schema_id, path, vector) in AUTONOMOUS_CONTRACTS.items():
        entry = entries.get(name)
        if entry is None:
            errors.append(f"missing autonomous repair contract: {name}")
            continue
        if set(entry) != {
            "name",
            "schema_id",
            "path",
            "canonical_vector",
            "owner",
            "consumers",
        }:
            errors.append(f"autonomous repair contract {name} fields must be strict")
        if (
            entry.get("schema_id") != schema_id
            or entry.get("path") != path
            or entry.get("canonical_vector") != vector
        ):
            errors.append(f"autonomous repair contract {name} identity must match")
        if entry.get("owner") != "ao-architecture":
            errors.append(f"autonomous repair contract {name} owner must be ao-architecture")
        if not isinstance(entry.get("consumers"), list) or not entry["consumers"]:
            errors.append(f"autonomous repair contract {name} consumers are required")

        try:
            schema = json.loads((root / path).read_text())
            instance = json.loads((root / vector).read_text())
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"autonomous repair contract {name} artifact error: {exc}")
            continue
        instances[name] = instance
        if schema.get("$schema") != SCHEMA_DIALECT:
            errors.append(f"autonomous repair contract {name} must use JSON Schema 2020-12")
        if schema.get("$id") != schema_id:
            errors.append(f"autonomous repair contract {name} schema ID must match")
        if schema.get("additionalProperties") is not False:
            errors.append(f"autonomous repair contract {name} must reject unknown fields")
        errors.extend(
            f"{name}: {error}"
            for error in validate_contract_instance(
                name, instance, reference_time=reference_time, root=root
            )
        )

    event = instances.get("append_only_event")
    checkpoint = instances.get("checkpoint")
    if event is not None and checkpoint is not None:
        errors.extend(
            f"checkpoint_event_linkage: {error}"
            for error in validate_checkpoint_event_linkage(checkpoint, event)
        )

    if family.get("bounds") != {
        "issue_snapshot_limit": 50,
        "reproduction_candidate_limit": 10,
        "selected_candidate_limit": 1,
    }:
        errors.append("autonomous_repair_contract_family.bounds must remain 50/10/1")
    expected_safety = {
        "issue_list_grants_mutation_authority": False,
        "successor_may_widen_authority": False,
        "unknown_governance_defaults_to_external_draft_only": True,
        "external_merge_authorized": False,
    }
    safety = family.get("safety")
    if isinstance(safety, dict):
        for field, expected in expected_safety.items():
            if safety.get(field) is not expected:
                errors.append(
                    "autonomous_repair_contract_family.safety."
                    f"{field} must be {str(expected).lower()}"
                )
    else:
        errors.append("autonomous_repair_contract_family.safety is required")
    return errors
