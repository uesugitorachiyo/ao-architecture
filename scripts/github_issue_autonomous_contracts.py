from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"
RFC3339_PATTERN = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T"
    r"[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?"
    r"(?:Z|[+-][0-9]{2}:[0-9]{2})$"
)
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
    if not isinstance(value, str) or RFC3339_PATTERN.fullmatch(value) is None:
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
        "candidate_decision": (
            "decision_digest",
            "candidate decision digest does not match canonical fields",
        ),
        "governance_decision": (
            "decision_digest",
            "governance decision digest does not match canonical fields",
        ),
        "reviewer_independence": (
            "review_digest",
            "reviewer independence digest does not match canonical fields",
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
        if (
            approved_at is not None
            and expires_at is not None
            and (expires_at - approved_at).total_seconds() > 24 * 60 * 60
        ):
            errors.append(
                "github action approval lifetime must not exceed 24 hours"
            )
        if expires_at is not None and expires_at <= now.astimezone(timezone.utc):
            errors.append("github action digest approval is stale")
        if any(
            check["head_sha"] != instance["head_sha"]
            for check in instance["required_checks"]
        ):
            errors.append("github action digest checks must bind the exact head SHA")
        if not instance["required_checks"] or any(
            check["conclusion"] != "success"
            or check["head_sha"] != instance["head_sha"]
            for check in instance["required_checks"]
        ):
            errors.append(
                "GitHub write action requires nonempty all-success exact-head checks"
            )
    elif name == "governance_decision":
        governance_class = instance["governance_class"]
        merge = instance["merge"]
        if not merge["authorized"] and merge["mode"] != "never":
            errors.append("unauthorized governance merge mode must be never")
        if merge["authorized"]:
            checks = instance["required_checks"]
            checks_pass = bool(checks) and all(
                check["conclusion"] == "success"
                and check["head_sha"] == instance["head_sha"]
                for check in checks
            )
            if instance["protected_path_touched"]:
                errors.append("authorized merge must not touch protected paths")
            if not checks_pass:
                errors.append(
                    "authorized merge requires nonempty all-success exact-head checks"
                )
        if (
            governance_class == "sole_control"
            and merge["mode"] == "auto_merge"
            and not merge["auto_merge_opt_in"]
        ):
            errors.append("sole-control auto_merge requires explicit opt-in")
        if governance_class in {"external", "unknown"}:
            if (
                merge["authorized"] is not False
                or merge["mode"] != "never"
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
                merge["approval_kind"] != "none"
                or merge["approval_head_sha"] is not None
            ):
                errors.append(
                    f"{governance_class} governance must not carry merge approval"
                )
            if merge["auto_merge_opt_in"]:
                errors.append(
                    f"{governance_class} governance must not opt into auto-merge"
                )
        if (
            governance_class == "team"
            and merge["authorized"]
            and (
                merge["approval_kind"]
                not in {"independent_human", "codeowner"}
                or merge["approval_head_sha"] != instance["head_sha"]
            )
        ):
            errors.append("team merge requires independent approval on the exact head SHA")
        if (
            governance_class == "team"
            and merge["authorized"]
            and merge["mode"] != "merge_queue"
        ):
            errors.append("team merge must use merge_queue")
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
        issue_numbers = [issue["number"] for issue in instance["issues"]]
        if len(issue_numbers) != len(set(issue_numbers)):
            errors.append("discovery issue numbers must be unique")
        candidate_number_list = [
            candidate["issue_number"] for candidate in instance["candidates"]
        ]
        if len(candidate_number_list) != len(set(candidate_number_list)):
            errors.append("discovery candidate numbers must be unique")
        if not candidate_numbers.issubset(set(issue_numbers)):
            errors.append("discovery candidates must be a subset of snapshot issues")
        ranks = [candidate["rank"] for candidate in instance["candidates"]]
        if len(ranks) != len(set(ranks)):
            errors.append("discovery candidate ranks must be unique")
        if ranks != list(range(1, len(ranks) + 1)):
            errors.append("discovery candidate ranks must be contiguous from one")
        selected = instance["selected_issue_number"]
        if selected is not None and selected not in candidate_numbers:
            errors.append("selected issue must be present in candidates")
        excluded = [
            entry["issue_number"] for entry in instance["exclusion_ledger"]
        ]
        if len(excluded) != len(set(excluded)):
            errors.append("discovery exclusion issue numbers must be unique")
        expected_excluded = set(issue_numbers)
        if selected is not None:
            expected_excluded.discard(selected)
        if set(excluded) != expected_excluded:
            errors.append(
                "discovery exclusion ledger must exactly cover unselected snapshot issues"
            )
        if selected is None and set(excluded) != set(issue_numbers):
            errors.append("zero-selection discovery must exclude every snapshot issue")
    elif name == "candidate_decision":
        eligibility = instance["eligibility"]
        positive_fields = (
            "open_bug",
            "target_in_repository",
            "no_existing_fix",
            "current_head_unfixed",
            "public_reproduction_feasible",
            "deterministic_local_reproduction",
            "expected_behavior_grounded",
            "bounded_policy_compatible",
        )
        failing_predicate = any(
            eligibility[field] is not True for field in positive_fields
        ) or eligibility["security_sensitive"] is True
        grounded_source = instance["expected_behavior_source"] != "unavailable"
        if instance["decision"] in {"eligible", "selected"}:
            for field in positive_fields:
                if eligibility[field] is not True:
                    errors.append(
                        f"{instance['decision']} candidate requires "
                        f"eligibility.{field}=true"
                    )
            if eligibility["security_sensitive"] is not False:
                errors.append(
                    f"{instance['decision']} candidate requires "
                    "eligibility.security_sensitive=false"
                )
            if not grounded_source:
                errors.append(
                    f"{instance['decision']} candidate requires a grounded "
                    "expected_behavior_source"
                )
        elif not failing_predicate and grounded_source:
            errors.append("excluded candidate requires a failing predicate")
    elif name == "immutable_run_envelope":
        match = re.fullmatch(
            r"https://github\.com/([A-Za-z0-9_.-]+)/"
            r"([A-Za-z0-9_.-]+)/issues(?:/([1-9][0-9]*))?",
            instance["trigger"]["canonical_url"],
        )
        if (
            match is None
            or f"{match.group(1)}/{match.group(2)}"
            != instance["trigger"]["repository"]
        ):
            errors.append(
                "run envelope URL repository must match trigger repository"
            )
        issue_number = match.group(3) if match is not None else None
        if (
            instance["trigger"]["mode"] == "explicit_issue"
            and issue_number is None
        ):
            errors.append("explicit_issue mode requires a numbered issue URL")
        if instance["trigger"]["mode"] == "issue_list" and issue_number is not None:
            errors.append("issue_list mode requires an issue-list URL")
        created_at = _parse_timestamp(instance["created_at"])
        expires_at = _parse_timestamp(instance["expires_at"])
        if (
            created_at is not None
            and expires_at is not None
            and expires_at <= created_at
        ):
            errors.append("run envelope expiry must follow creation")
        if (
            created_at is not None
            and expires_at is not None
            and (expires_at - created_at).total_seconds()
            > instance["budgets"]["wall_clock_seconds"]
        ):
            errors.append("run envelope expiry exceeds wall_clock_seconds")
        if (
            reference_time is not None
            and expires_at is not None
            and expires_at <= reference_time.astimezone(timezone.utc)
        ):
            errors.append("run envelope is expired")
        lineage = instance["lineage"]
        if lineage["kind"] == "origin" and (
            instance["predecessor_digest"] is not None
            or lineage["predecessor_run_id"] is not None
            or lineage["predecessor_digest"] is not None
        ):
            errors.append("origin envelope predecessor fields must be null")
        if lineage["kind"] == "narrower_successor" and (
            instance["predecessor_digest"] is None
            or lineage["predecessor_run_id"] is None
            or lineage["predecessor_digest"] is None
            or lineage["predecessor_digest"] != instance["predecessor_digest"]
        ):
            errors.append(
                "narrower successor lineage requires bound predecessor fields"
            )
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
        opt_in = instance["governance"]["sole_control_auto_merge_opt_in"]
        if (
            opt_in
            and instance["governance"]["ownership_class"] != "sole_control"
        ):
            errors.append(
                "auto-merge opt-in is only valid for sole_control governance"
            )
        if (
            "auto_merge" in instance["governance"]["allowed_actions"]
            and (
                instance["governance"]["ownership_class"] != "sole_control"
                or not opt_in
            )
        ):
            errors.append("auto_merge requires sole-control explicit opt-in")
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
    if successor["trigger"] != predecessor["trigger"]:
        errors.append("successor trigger must exactly match predecessor")
    if successor["loop"] != predecessor["loop"]:
        errors.append("successor loop must exactly match predecessor")
    if (
        successor["governance"]["ownership_class"]
        != predecessor["governance"]["ownership_class"]
    ):
        errors.append("successor governance.ownership_class must match predecessor")
    if (
        successor["governance"]["sole_control_auto_merge_opt_in"]
        and not predecessor["governance"]["sole_control_auto_merge_opt_in"]
    ):
        errors.append("successor auto-merge opt-in must not widen predecessor")
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
    for field in (
        "default_branch",
        "pinned_base_commit",
        "fork_owner",
        "repair_branch",
    ):
        if successor["routing"][field] != predecessor["routing"][field]:
            errors.append(f"successor routing.{field} must match predecessor")
    if not set(successor["routing"]["protected_path_classes"]).issuperset(
        predecessor["routing"]["protected_path_classes"]
    ):
        errors.append(
            "successor protected_path_classes must include predecessor guards"
        )
    if not set(successor["routing"]["required_checks"]).issuperset(
        predecessor["routing"]["required_checks"]
    ):
        errors.append("successor required_checks must include predecessor checks")
    if not set(successor["stop_conditions"]).issuperset(
        predecessor["stop_conditions"]
    ):
        errors.append(
            "successor stop_conditions must include predecessor conditions"
        )
    if successor["terminal_statuses"] != predecessor["terminal_statuses"]:
        errors.append(
            "successor terminal_statuses must exactly match predecessor"
        )
    predecessor_created = _parse_timestamp(predecessor.get("created_at"))
    successor_created = _parse_timestamp(successor.get("created_at"))
    if (
        predecessor_created is not None
        and successor_created is not None
        and successor_created < predecessor_created
    ):
        errors.append("successor created_at must not move backward")
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


def validate_discovery_candidate_link(
    discovery: dict[str, Any], candidate: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    matching = [
        entry
        for entry in discovery.get("candidates", [])
        if entry.get("issue_number") == candidate.get("issue_number")
    ]
    if len(matching) != 1:
        errors.append(
            "canonical candidate decision must appear exactly once in discovery"
        )
        return errors
    if matching[0].get("decision_digest") != candidate.get("decision_digest"):
        errors.append(
            "discovery candidate digest must match canonical candidate decision"
        )
    if (
        candidate.get("decision") == "selected"
        and discovery.get("selected_issue_number") != candidate.get("issue_number")
    ):
        errors.append(
            "selected canonical candidate must match discovery selected issue"
        )
    return errors


def validate_action_digest_links(
    action: dict[str, Any],
    envelope: dict[str, Any],
    candidate: dict[str, Any],
    governance: dict[str, Any],
    reviewer: dict[str, Any],
) -> list[str]:
    expected = {
        "run_envelope_digest": (
            envelope.get("canonical_digest"),
            "action run_envelope_digest must match canonical envelope",
        ),
        "candidate_decision_digest": (
            candidate.get("decision_digest"),
            "action candidate_decision_digest must match canonical candidate",
        ),
        "governance_decision_digest": (
            governance.get("decision_digest"),
            "action governance_decision_digest must match canonical governance",
        ),
        "reviewer_independence_digest": (
            reviewer.get("review_digest"),
            "action reviewer_independence_digest must match canonical review",
        ),
    }
    errors: list[str] = []
    for field, (digest, error) in expected.items():
        if action.get(field) != digest:
            errors.append(error)
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
    discovery = instances.get("bounded_discovery_result")
    candidate = instances.get("candidate_decision")
    if discovery is not None and candidate is not None:
        errors.extend(
            f"discovery_candidate_link: {error}"
            for error in validate_discovery_candidate_link(discovery, candidate)
        )
    action = instances.get("github_action_digest")
    envelope = instances.get("immutable_run_envelope")
    governance = instances.get("governance_decision")
    reviewer = instances.get("reviewer_independence")
    if all(
        item is not None
        for item in (action, envelope, candidate, governance, reviewer)
    ):
        errors.extend(
            f"action_digest_link: {error}"
            for error in validate_action_digest_links(
                action, envelope, candidate, governance, reviewer
            )
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
