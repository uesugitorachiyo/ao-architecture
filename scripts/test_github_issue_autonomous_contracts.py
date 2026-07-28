import copy
import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import github_issue_autonomous_contracts as contracts


ROOT = Path(__file__).resolve().parents[1]


class GitHubIssueAutonomousContractsTest(unittest.TestCase):
    def load_vector(self, name):
        vector = contracts.AUTONOMOUS_CONTRACTS[name][2]
        return json.loads((ROOT / vector).read_text())

    def coherent_action_family(self):
        envelope = self.load_vector("immutable_run_envelope")
        candidate = self.load_vector("candidate_decision")
        governance = self.load_vector("governance_decision")
        reviewer = self.load_vector("reviewer_independence")
        action = self.load_vector("github_action_digest")

        action["action"] = "open_upstream_draft_pr"
        action["branch"] = envelope["routing"]["repair_branch"]
        action["required_checks"] = [
            {
                "name": name,
                "conclusion": "success",
                "head_sha": action["head_sha"],
            }
            for name in envelope["routing"]["required_checks"]
        ]
        governance["required_checks"] = copy.deepcopy(action["required_checks"])
        governance["decision_digest"] = contracts._canonical_sha256(
            governance, "decision_digest"
        )
        reviewer["subject_digest"] = action["diff_digest"]
        reviewer["review_digest"] = contracts._canonical_sha256(
            reviewer, "review_digest"
        )
        action["governance_decision_digest"] = governance["decision_digest"]
        action["reviewer_independence_digest"] = reviewer["review_digest"]
        action["action_digest"] = contracts._canonical_sha256(
            action, "action_digest"
        )
        return action, envelope, candidate, governance, reviewer

    def test_autonomous_family_defines_bounded_github_write_semantics(self):
        document = json.loads(
            (ROOT / "stack/github-issue-workflow-contracts.json").read_text()
        )
        execution = document["autonomous_repair_contract_family"][
            "github_action_execution"
        ]

        self.assertEqual(
            execution["push_operator_fork"],
            {
                "fork_lookup": "required_before_write",
                "fork_absent": "create_then_exact_readback",
                "fork_present": "reuse_only_exact_owner_parent_and_default_branch",
                "branch_absent": "create_at_exact_approved_head",
                "branch_present": "reuse_only_at_exact_approved_head",
                "force_update_allowed": False,
                "upstream_push_allowed": False,
            },
        )
        self.assertEqual(
            execution["open_upstream_draft_pr"],
            {
                "lookup": "exact_base_head_open_pull_requests",
                "absent": "create_once_then_exact_readback",
                "present": "reuse_only_exact_draft_identity",
                "update_allowed": False,
                "ready_for_review_allowed": False,
                "review_allowed": False,
                "merge_allowed": False,
            },
        )
        self.assertEqual(
            execution["write_budget"],
            {
                "fork_creates": 1,
                "branch_creates": 1,
                "draft_pr_creates": 1,
            },
        )
        self.assertEqual(
            execution["credentials"],
            {
                "ambient_only": True,
                "serialized": False,
            },
        )

    def test_autonomous_family_rejects_github_write_semantic_drift(self):
        document = json.loads(
            (ROOT / "stack/github-issue-workflow-contracts.json").read_text()
        )
        document["autonomous_repair_contract_family"][
            "github_action_execution"
        ]["push_operator_fork"]["force_update_allowed"] = True

        errors = contracts.validate_autonomous_family(document)

        self.assertIn(
            "autonomous repair GitHub action execution semantics must remain bounded",
            errors,
        )

    def non_fork_action_family(self, ownership_class, action_name):
        action, envelope, candidate, governance, reviewer = (
            self.coherent_action_family()
        )
        envelope["governance"]["ownership_class"] = ownership_class
        envelope["governance"]["allowed_actions"] = [
            "read_public_metadata",
            "clone_public_repository",
            action_name,
        ]
        envelope["governance"]["denied_actions"] = [
            denied
            for denied in envelope["governance"]["denied_actions"]
            if denied not in {"open_ready_pr", "merge"}
        ]
        envelope["routing"]["fork_owner"] = None
        envelope["canonical_digest"] = contracts._canonical_sha256(
            envelope, "canonical_digest"
        )

        governance["governance_class"] = ownership_class
        governance["push_target"] = (
            "policy_authorized_branch"
            if ownership_class == "team"
            else "authorized_operator_repository"
        )
        governance["pull_request_mode"] = "draft_or_ready_by_policy"
        if action_name == "request_merge_queue":
            governance["merge"]["authorized"] = True
            governance["merge"]["mode"] = "merge_queue"
            governance["merge"]["approval_kind"] = "independent_human"
            governance["merge"]["approval_head_sha"] = governance["head_sha"]
            reviewer["status"] = "independent"
            reviewer["satisfies_team_merge_gate"] = True
        governance["decision_digest"] = contracts._canonical_sha256(
            governance, "decision_digest"
        )
        reviewer["review_digest"] = contracts._canonical_sha256(
            reviewer, "review_digest"
        )

        action["action"] = action_name
        action["fork"] = None
        action["run_envelope_digest"] = envelope["canonical_digest"]
        action["governance_decision_digest"] = governance["decision_digest"]
        action["reviewer_independence_digest"] = reviewer["review_digest"]
        action["action_digest"] = contracts._canonical_sha256(
            action, "action_digest"
        )
        return action, envelope, candidate, governance, reviewer

    def successor_envelope(self):
        predecessor = self.load_vector("immutable_run_envelope")
        successor = copy.deepcopy(predecessor)
        successor["run_id"] = "repair-run-successor"
        successor["predecessor_digest"] = predecessor["canonical_digest"]
        successor["lineage"] = {
            "kind": "narrower_successor",
            "predecessor_run_id": predecessor["run_id"],
            "predecessor_digest": predecessor["canonical_digest"],
        }
        return predecessor, successor

    def test_requires_all_eight_separately_versioned_strict_schemas(self):
        self.assertEqual(len(contracts.AUTONOMOUS_CONTRACTS), 8)
        for schema_id, schema_path, vector_path in contracts.AUTONOMOUS_CONTRACTS.values():
            schema_file = ROOT / schema_path
            vector_file = ROOT / vector_path
            self.assertTrue(schema_file.is_file(), schema_path)
            self.assertTrue(vector_file.is_file(), vector_path)
            schema = json.loads(schema_file.read_text())
            self.assertEqual(schema["$schema"], contracts.SCHEMA_DIALECT)
            self.assertEqual(schema["$id"], schema_id)
            self.assertFalse(schema["additionalProperties"])

    def test_rejects_unknown_authority_field(self):
        envelope = self.load_vector("immutable_run_envelope")
        envelope["authority_override"] = {"merge": True}
        errors = contracts.validate_contract_instance(
            "immutable_run_envelope", envelope
        )
        self.assertTrue(any("additional property" in error for error in errors), errors)

    def test_rejects_widened_successor_envelope(self):
        previous = self.load_vector("immutable_run_envelope")
        successor = copy.deepcopy(previous)
        successor["run_id"] = "repair-run-successor"
        successor["lineage"] = {
            "kind": "narrower_successor",
            "predecessor_run_id": previous["run_id"],
            "predecessor_digest": previous["canonical_digest"],
        }
        successor["predecessor_digest"] = previous["canonical_digest"]
        successor["budgets"]["publication_count"] += 1
        errors = contracts.validate_successor_envelope(previous, successor)
        self.assertIn(
            "successor budgets.publication_count must not exceed predecessor",
            errors,
        )

    def test_rejects_discovery_bounds_above_fifty_and_ten(self):
        discovery = self.load_vector("bounded_discovery_result")
        discovery["snapshot_limit"] = 51
        discovery["candidate_limit"] = 11
        errors = contracts.validate_contract_instance(
            "bounded_discovery_result", discovery
        )
        self.assertTrue(any("snapshot_limit" in error for error in errors), errors)
        self.assertTrue(any("candidate_limit" in error for error in errors), errors)

    def test_rejects_invalid_reviewer_status(self):
        review = self.load_vector("reviewer_independence")
        review["status"] = "trusted"
        errors = contracts.validate_contract_instance("reviewer_independence", review)
        self.assertTrue(any("status" in error for error in errors), errors)

    def test_rejects_unsafe_external_governance(self):
        governance = self.load_vector("governance_decision")
        governance["merge"]["authorized"] = True
        governance["merge"]["mode"] = "auto_merge"
        errors = contracts.validate_contract_instance(
            "governance_decision", governance
        )
        self.assertIn("external governance must deny merge", errors)

    def test_rejects_stale_or_mismatched_action_digest(self):
        action = self.load_vector("github_action_digest")
        action["head_sha"] = "c" * 40
        errors = contracts.validate_contract_instance(
            "github_action_digest",
            action,
            reference_time=datetime(2026, 7, 28, tzinfo=timezone.utc),
        )
        self.assertIn("github action digest does not match canonical action fields", errors)

        stale = self.load_vector("github_action_digest")
        errors = contracts.validate_contract_instance(
            "github_action_digest",
            stale,
            reference_time=datetime(2026, 7, 30, tzinfo=timezone.utc),
        )
        self.assertIn("github action digest approval is stale", errors)

    def test_rejects_malformed_checkpoint_event_linkage(self):
        event = self.load_vector("append_only_event")
        checkpoint = self.load_vector("checkpoint")
        checkpoint["last_event_digest"] = "f" * 64
        errors = contracts.validate_checkpoint_event_linkage(checkpoint, event)
        self.assertIn("checkpoint last_event_digest must match event digest", errors)

        event["sequence"] += 1
        errors = contracts.validate_checkpoint_event_linkage(
            self.load_vector("checkpoint"), event
        )
        self.assertIn("checkpoint last_event_sequence must match event sequence", errors)

    def test_checkpoint_active_lease_must_be_live_at_reference_time(self):
        checkpoint = self.load_vector("checkpoint")
        checkpoint["lease"]["expires_at"] = "2026-07-27T23:29:59Z"
        checkpoint["checkpoint_digest"] = contracts._canonical_sha256(
            checkpoint, "checkpoint_digest"
        )

        errors = contracts.validate_contract_instance(
            "checkpoint",
            checkpoint,
            reference_time=datetime(2026, 7, 27, 23, 30, tzinfo=timezone.utc),
        )

        self.assertIn(
            "active checkpoint lease must expire after reference time", errors
        )

    def test_checkpoint_expired_status_must_match_reference_time(self):
        checkpoint = self.load_vector("checkpoint")
        checkpoint["lease"]["status"] = "expired"
        checkpoint["lease"]["expires_at"] = "2026-07-27T23:31:00Z"
        checkpoint["checkpoint_digest"] = contracts._canonical_sha256(
            checkpoint, "checkpoint_digest"
        )

        errors = contracts.validate_contract_instance(
            "checkpoint",
            checkpoint,
            reference_time=datetime(2026, 7, 27, 23, 30, tzinfo=timezone.utc),
        )

        self.assertIn(
            "expired checkpoint lease must not outlive reference time", errors
        )

    def test_checkpoint_creation_and_lease_order_are_strict(self):
        checkpoint = self.load_vector("checkpoint")
        checkpoint["created_at"] = "2026-07-27T23:31:00Z"
        checkpoint["lease"]["expires_at"] = "2026-07-27T23:30:00Z"
        checkpoint["checkpoint_digest"] = contracts._canonical_sha256(
            checkpoint, "checkpoint_digest"
        )

        errors = contracts.validate_contract_instance(
            "checkpoint",
            checkpoint,
            reference_time=datetime(2026, 7, 27, 23, 30, tzinfo=timezone.utc),
        )

        self.assertIn("checkpoint creation is in the future", errors)
        self.assertIn("checkpoint lease expiry must follow creation", errors)

    def test_checkpoint_lease_cannot_outlive_envelope(self):
        checkpoint = self.load_vector("checkpoint")
        envelope = self.load_vector("immutable_run_envelope")
        checkpoint["lease"]["expires_at"] = "2026-07-28T00:00:01Z"
        checkpoint["checkpoint_digest"] = contracts._canonical_sha256(
            checkpoint, "checkpoint_digest"
        )

        errors = contracts.validate_checkpoint_envelope_linkage(
            checkpoint,
            envelope,
            reference_time=datetime(2026, 7, 27, 23, 30, tzinfo=timezone.utc),
        )

        self.assertIn("checkpoint lease must not outlive run envelope", errors)

    def test_checkpoint_creation_must_be_within_envelope_lifetime(self):
        for created_at in (
            "2026-07-27T15:59:59Z",
            "2026-07-28T00:00:00Z",
        ):
            with self.subTest(created_at=created_at):
                checkpoint = self.load_vector("checkpoint")
                envelope = self.load_vector("immutable_run_envelope")
                checkpoint["created_at"] = created_at
                checkpoint["checkpoint_digest"] = contracts._canonical_sha256(
                    checkpoint, "checkpoint_digest"
                )

                errors = contracts.validate_checkpoint_envelope_linkage(
                    checkpoint,
                    envelope,
                    reference_time=datetime(
                        2026, 7, 27, 23, 30, tzinfo=timezone.utc
                    ),
                )

                self.assertIn(
                    "checkpoint creation must be within run envelope lifetime",
                    errors,
                )

    def test_checkpoint_event_linkage_requires_exact_lease(self):
        checkpoint = self.load_vector("checkpoint")
        event = self.load_vector("append_only_event")
        event["lease_id"] = "lease-run-other"
        event["event_digest"] = contracts._canonical_sha256(
            event, "event_digest"
        )

        errors = contracts.validate_checkpoint_event_linkage(
            checkpoint,
            event,
            reference_time=datetime(2026, 7, 27, 23, 30, tzinfo=timezone.utc),
        )

        self.assertIn("checkpoint lease_id must match event lease_id", errors)

    def test_checkpoint_cannot_capture_a_future_event(self):
        checkpoint = self.load_vector("checkpoint")
        event = self.load_vector("append_only_event")
        event["timestamp"] = "2026-07-27T23:01:01Z"
        event["event_digest"] = contracts._canonical_sha256(
            event, "event_digest"
        )

        errors = contracts.validate_checkpoint_event_linkage(
            checkpoint,
            event,
            reference_time=datetime(2026, 7, 27, 23, 30, tzinfo=timezone.utc),
        )

        self.assertIn(
            "event timestamp must not follow checkpoint creation", errors
        )

    def test_checkpoint_lease_recovery_authorization_matrix(self):
        for status in ("active", "expired", "handed_off", "closed"):
            for previous_worker_active in (False, True):
                for successor_resume_authorized in (False, True):
                    resume_allowed = (
                        successor_resume_authorized is False
                        or (
                            status in {"expired", "handed_off"}
                            and previous_worker_active is False
                        )
                    )
                    with self.subTest(
                        status=status,
                        previous_worker_active=previous_worker_active,
                        successor_resume_authorized=successor_resume_authorized,
                    ):
                        checkpoint = self.load_vector("checkpoint")
                        checkpoint["lease"]["status"] = status
                        checkpoint["lease"]["previous_worker_active"] = (
                            previous_worker_active
                        )
                        checkpoint["lease"][
                            "successor_resume_authorized"
                        ] = successor_resume_authorized
                        checkpoint["lease"][
                            "ownership_verified_at"
                        ] = "2026-07-27T23:00:00Z"
                        if status == "expired":
                            checkpoint["lease"][
                                "expires_at"
                            ] = "2026-07-27T23:00:00Z"
                        checkpoint[
                            "checkpoint_digest"
                        ] = contracts._canonical_sha256(
                            checkpoint, "checkpoint_digest"
                        )

                        errors = contracts.validate_contract_instance(
                            "checkpoint",
                            checkpoint,
                            reference_time=datetime(
                                2026, 7, 27, 23, 30, tzinfo=timezone.utc
                            ),
                        )
                        if resume_allowed:
                            self.assertEqual(errors, [])
                        else:
                            self.assertTrue(
                                any(
                                    "successor resume" in error
                                    for error in errors
                                ),
                                errors,
                            )

    def test_checkpoint_event_linkage_fails_closed_for_malformed_documents(self):
        checkpoint = self.load_vector("checkpoint")
        event = self.load_vector("append_only_event")
        cases = (
            (None, event, "checkpoint:"),
            ("not-an-object", event, "checkpoint:"),
            ({}, event, "checkpoint:"),
            (checkpoint, None, "append_only_event:"),
            (checkpoint, 7, "append_only_event:"),
            (checkpoint, {}, "append_only_event:"),
        )
        for malformed_checkpoint, malformed_event, expected_prefix in cases:
            with self.subTest(
                checkpoint=malformed_checkpoint, event=malformed_event
            ):
                errors = contracts.validate_checkpoint_event_linkage(
                    malformed_checkpoint,
                    malformed_event,
                    reference_time=datetime(
                        2026, 7, 27, 23, 30, tzinfo=timezone.utc
                    ),
                )
                self.assertTrue(
                    any(
                        error.startswith(expected_prefix) for error in errors
                    ),
                    errors,
                )

        for malformed_lease in (None, "not-an-object", 7):
            with self.subTest(lease=malformed_lease):
                malformed_checkpoint = self.load_vector("checkpoint")
                malformed_checkpoint["lease"] = malformed_lease
                errors = contracts.validate_checkpoint_event_linkage(
                    malformed_checkpoint,
                    event,
                    reference_time=datetime(
                        2026, 7, 27, 23, 30, tzinfo=timezone.utc
                    ),
                )
                self.assertTrue(
                    any(
                        error.startswith("checkpoint: $.lease")
                        for error in errors
                    ),
                    errors,
                )

    def test_canonical_active_lease_denies_resume_and_names_event_actor(self):
        checkpoint = self.load_vector("checkpoint")

        self.assertIs(
            checkpoint["lease"].get("successor_resume_authorized"), False
        )
        self.assertEqual(
            checkpoint["lease"].get("authorized_event_actors"), ["ao-forge"]
        )
        ownership_verified_at = contracts._parse_timestamp(
            checkpoint["lease"].get("ownership_verified_at")
        )
        created_at = contracts._parse_timestamp(checkpoint["created_at"])
        self.assertIsNotNone(ownership_verified_at)
        self.assertLessEqual(ownership_verified_at, created_at)

    def test_expired_resume_rejects_stale_pre_expiry_ownership_observation(self):
        checkpoint = self.load_vector("checkpoint")
        checkpoint["lease"]["status"] = "expired"
        checkpoint["lease"]["expires_at"] = "2026-07-27T23:00:00Z"
        checkpoint["lease"]["previous_worker_active"] = False
        checkpoint["lease"]["successor_resume_authorized"] = True
        checkpoint["lease"][
            "ownership_verified_at"
        ] = "2026-07-27T22:59:59Z"
        checkpoint["checkpoint_digest"] = contracts._canonical_sha256(
            checkpoint, "checkpoint_digest"
        )

        errors = contracts.validate_contract_instance(
            "checkpoint",
            checkpoint,
            reference_time=datetime(2026, 7, 27, 23, 30, tzinfo=timezone.utc),
        )

        self.assertIn(
            "expired recovery requires post-expiry ownership verification",
            errors,
        )

    def test_expired_resume_accepts_post_expiry_ownership_observation(self):
        checkpoint = self.load_vector("checkpoint")
        checkpoint["lease"]["status"] = "expired"
        checkpoint["lease"]["expires_at"] = "2026-07-27T23:00:00Z"
        checkpoint["lease"]["previous_worker_active"] = False
        checkpoint["lease"]["successor_resume_authorized"] = True
        checkpoint["lease"][
            "ownership_verified_at"
        ] = "2026-07-27T23:00:00Z"
        checkpoint["checkpoint_digest"] = contracts._canonical_sha256(
            checkpoint, "checkpoint_digest"
        )

        errors = contracts.validate_contract_instance(
            "checkpoint",
            checkpoint,
            reference_time=datetime(2026, 7, 27, 23, 30, tzinfo=timezone.utc),
        )

        self.assertEqual(errors, [])

    def test_ownership_verification_must_precede_checkpoint_creation(self):
        checkpoint = self.load_vector("checkpoint")
        checkpoint["lease"][
            "ownership_verified_at"
        ] = "2026-07-27T23:01:01Z"
        checkpoint["checkpoint_digest"] = contracts._canonical_sha256(
            checkpoint, "checkpoint_digest"
        )

        errors = contracts.validate_contract_instance(
            "checkpoint",
            checkpoint,
            reference_time=datetime(2026, 7, 27, 23, 30, tzinfo=timezone.utc),
        )

        self.assertIn(
            "lease ownership verification must not follow checkpoint creation",
            errors,
        )

    def test_ownership_verification_must_be_within_envelope_lifetime(self):
        for ownership_verified_at in (
            "2026-07-27T15:59:59Z",
            "2026-07-28T00:00:00Z",
        ):
            with self.subTest(ownership_verified_at=ownership_verified_at):
                checkpoint = self.load_vector("checkpoint")
                envelope = self.load_vector("immutable_run_envelope")
                checkpoint["lease"][
                    "ownership_verified_at"
                ] = ownership_verified_at
                checkpoint["checkpoint_digest"] = contracts._canonical_sha256(
                    checkpoint, "checkpoint_digest"
                )

                errors = contracts.validate_checkpoint_envelope_linkage(
                    checkpoint,
                    envelope,
                    reference_time=datetime(
                        2026, 7, 27, 23, 30, tzinfo=timezone.utc
                    ),
                )

                self.assertIn(
                    "lease ownership verification must be within run envelope lifetime",
                    errors,
                )

    def test_handed_off_resume_requires_completed_handoff_event(self):
        checkpoint = self.load_vector("checkpoint")
        checkpoint["lease"]["status"] = "handed_off"
        checkpoint["lease"]["previous_worker_active"] = False
        checkpoint["lease"]["successor_resume_authorized"] = True
        checkpoint["lease"][
            "ownership_verified_at"
        ] = "2026-07-27T23:00:00Z"
        checkpoint["checkpoint_digest"] = contracts._canonical_sha256(
            checkpoint, "checkpoint_digest"
        )
        event = self.load_vector("append_only_event")

        errors = contracts.validate_checkpoint_event_linkage(
            checkpoint,
            event,
            reference_time=datetime(2026, 7, 27, 23, 30, tzinfo=timezone.utc),
        )

        self.assertIn(
            "handed-off resume requires a handoff_completed event", errors
        )

    def test_handed_off_resume_accepts_completed_handoff_event(self):
        checkpoint = self.load_vector("checkpoint")
        checkpoint["lease"]["status"] = "handed_off"
        checkpoint["lease"]["previous_worker_active"] = False
        checkpoint["lease"]["successor_resume_authorized"] = True
        checkpoint["lease"][
            "ownership_verified_at"
        ] = "2026-07-27T23:00:00Z"
        event = self.load_vector("append_only_event")
        event["event_type"] = "handoff_completed"
        event["event_digest"] = contracts._canonical_sha256(
            event, "event_digest"
        )
        checkpoint["last_event_digest"] = event["event_digest"]
        checkpoint["checkpoint_digest"] = contracts._canonical_sha256(
            checkpoint, "checkpoint_digest"
        )

        errors = contracts.validate_checkpoint_event_linkage(
            checkpoint,
            event,
            reference_time=datetime(2026, 7, 27, 23, 30, tzinfo=timezone.utc),
        )

        self.assertEqual(errors, [])

    def test_checkpoint_event_rejects_unrelated_actor(self):
        checkpoint = self.load_vector("checkpoint")
        checkpoint["lease"]["successor_resume_authorized"] = False
        checkpoint["lease"]["authorized_event_actors"] = ["ao-forge"]
        checkpoint["checkpoint_digest"] = contracts._canonical_sha256(
            checkpoint, "checkpoint_digest"
        )
        event = self.load_vector("append_only_event")
        event["actor"] = "unrelated-worker"
        event["event_digest"] = contracts._canonical_sha256(
            event, "event_digest"
        )

        errors = contracts.validate_checkpoint_event_linkage(
            checkpoint,
            event,
            reference_time=datetime(2026, 7, 27, 23, 30, tzinfo=timezone.utc),
        )

        self.assertIn(
            "event actor must be authorized by checkpoint lease", errors
        )

    def test_event_timestamp_must_be_within_envelope_lifetime(self):
        for timestamp in (
            "2026-07-27T15:59:59Z",
            "2026-07-28T00:00:00Z",
        ):
            with self.subTest(timestamp=timestamp):
                event = self.load_vector("append_only_event")
                envelope = self.load_vector("immutable_run_envelope")
                event["timestamp"] = timestamp
                event["event_digest"] = contracts._canonical_sha256(
                    event, "event_digest"
                )

                errors = contracts.validate_event_envelope_linkage(
                    event,
                    envelope,
                    reference_time=datetime(
                        2026, 7, 27, 23, 30, tzinfo=timezone.utc
                    ),
                )

                self.assertIn(
                    "event timestamp must be within run envelope lifetime",
                    errors,
                )

    def test_event_envelope_linkage_requires_exact_identity(self):
        event = self.load_vector("append_only_event")
        envelope = self.load_vector("immutable_run_envelope")
        event["run_id"] = "repair-run-other"
        event["run_envelope_digest"] = "0" * 64
        event["event_digest"] = contracts._canonical_sha256(
            event, "event_digest"
        )

        errors = contracts.validate_event_envelope_linkage(
            event,
            envelope,
            reference_time=datetime(2026, 7, 27, 23, 30, tzinfo=timezone.utc),
        )

        self.assertIn("event run_id must match run envelope", errors)
        self.assertIn("event digest must match canonical run envelope", errors)

    def test_candidate_selected_requires_all_authenticity_predicates(self):
        for field in (
            "open_bug",
            "target_in_repository",
            "no_existing_fix",
            "current_head_unfixed",
            "public_reproduction_feasible",
            "deterministic_local_reproduction",
            "expected_behavior_grounded",
            "bounded_policy_compatible",
        ):
            candidate = self.load_vector("candidate_decision")
            candidate["eligibility"][field] = False
            errors = contracts.validate_contract_instance(
                "candidate_decision", candidate
            )
            self.assertIn(
                f"selected candidate requires eligibility.{field}=true", errors
            )

        candidate = self.load_vector("candidate_decision")
        candidate["eligibility"]["security_sensitive"] = True
        errors = contracts.validate_contract_instance("candidate_decision", candidate)
        self.assertIn(
            "selected candidate requires eligibility.security_sensitive=false",
            errors,
        )

    def test_candidate_selected_requires_grounded_expected_behavior(self):
        candidate = self.load_vector("candidate_decision")
        candidate["expected_behavior_source"] = "unavailable"
        errors = contracts.validate_contract_instance("candidate_decision", candidate)
        self.assertIn(
            "selected candidate requires a grounded expected_behavior_source",
            errors,
        )

    def test_candidate_excluded_requires_a_failing_predicate(self):
        candidate = self.load_vector("candidate_decision")
        candidate["decision"] = "excluded"
        errors = contracts.validate_contract_instance("candidate_decision", candidate)
        self.assertIn("excluded candidate requires a failing predicate", errors)

    def test_candidate_decision_has_a_bound_canonical_digest(self):
        candidate = self.load_vector("candidate_decision")
        self.assertRegex(candidate.get("decision_digest", ""), r"^[0-9a-f]{64}$")
        candidate["rank"] = 2
        errors = contracts.validate_contract_instance("candidate_decision", candidate)
        self.assertIn(
            "candidate decision digest does not match canonical fields", errors
        )

    def test_discovery_rejects_duplicate_or_unlinked_issue_numbers(self):
        discovery = self.load_vector("bounded_discovery_result")
        discovery["issues"][1]["number"] = discovery["issues"][0]["number"]
        errors = contracts.validate_contract_instance(
            "bounded_discovery_result", discovery
        )
        self.assertIn("discovery issue numbers must be unique", errors)

        discovery = self.load_vector("bounded_discovery_result")
        discovery["candidates"][0]["issue_number"] = 999
        errors = contracts.validate_contract_instance(
            "bounded_discovery_result", discovery
        )
        self.assertIn("discovery candidates must be a subset of snapshot issues", errors)

    def test_discovery_rejects_duplicate_candidate_numbers_or_ranks(self):
        discovery = self.load_vector("bounded_discovery_result")
        duplicate = copy.deepcopy(discovery["candidates"][0])
        duplicate["decision_digest"] = "1" * 64
        discovery["candidates"].append(duplicate)
        errors = contracts.validate_contract_instance(
            "bounded_discovery_result", discovery
        )
        self.assertIn("discovery candidate numbers must be unique", errors)
        self.assertIn("discovery candidate ranks must be unique", errors)

    def test_discovery_requires_contiguous_deterministic_ranks(self):
        discovery = self.load_vector("bounded_discovery_result")
        discovery["candidates"][0]["rank"] = 2
        errors = contracts.validate_contract_instance(
            "bounded_discovery_result", discovery
        )
        self.assertIn("discovery candidate ranks must be contiguous from one", errors)

    def test_discovery_exclusion_ledger_exactly_covers_unselected_snapshot(self):
        discovery = self.load_vector("bounded_discovery_result")
        discovery["exclusion_ledger"] = []
        errors = contracts.validate_contract_instance(
            "bounded_discovery_result", discovery
        )
        self.assertIn(
            "discovery exclusion ledger must exactly cover unselected snapshot issues",
            errors,
        )

        discovery = self.load_vector("bounded_discovery_result")
        duplicate = copy.deepcopy(discovery["exclusion_ledger"][0])
        duplicate["reason_codes"] = ["different_reason"]
        discovery["exclusion_ledger"].append(duplicate)
        errors = contracts.validate_contract_instance(
            "bounded_discovery_result", discovery
        )
        self.assertIn("discovery exclusion issue numbers must be unique", errors)

    def test_discovery_zero_selection_excludes_every_snapshot_issue(self):
        discovery = self.load_vector("bounded_discovery_result")
        discovery["selected_issue_number"] = None
        errors = contracts.validate_contract_instance(
            "bounded_discovery_result", discovery
        )
        self.assertIn(
            "zero-selection discovery must exclude every snapshot issue", errors
        )

    def test_discovery_cross_links_canonical_candidate_decision(self):
        discovery = self.load_vector("bounded_discovery_result")
        candidate = self.load_vector("candidate_decision")
        discovery["candidates"][0]["decision_digest"] = "0" * 64
        errors = contracts.validate_discovery_candidate_link(discovery, candidate)
        self.assertIn(
            "discovery candidate digest must match canonical candidate decision",
            errors,
        )

    def test_envelope_requires_created_at_and_bounded_future_expiry(self):
        envelope = self.load_vector("immutable_run_envelope")
        self.assertRegex(envelope.get("created_at", ""), r".+Z$")

        envelope["created_at"] = "2026-07-27T20:00:00Z"
        envelope["expires_at"] = "2026-07-27T19:59:59Z"
        errors = contracts.validate_contract_instance(
            "immutable_run_envelope",
            envelope,
            reference_time=datetime(2026, 7, 27, 19, tzinfo=timezone.utc),
        )
        self.assertIn("run envelope expiry must follow creation", errors)

        envelope = self.load_vector("immutable_run_envelope")
        envelope["created_at"] = "2026-07-27T20:00:00Z"
        envelope["expires_at"] = "2026-07-28T04:00:01Z"
        errors = contracts.validate_contract_instance(
            "immutable_run_envelope",
            envelope,
            reference_time=datetime(2026, 7, 27, 19, tzinfo=timezone.utc),
        )
        self.assertIn("run envelope expiry exceeds wall_clock_seconds", errors)

        envelope = self.load_vector("immutable_run_envelope")
        envelope["created_at"] = "2026-07-27T20:00:00Z"
        envelope["expires_at"] = "2026-07-27T20:00:00Z"
        errors = contracts.validate_contract_instance(
            "immutable_run_envelope",
            envelope,
            reference_time=datetime(2026, 7, 27, 20, tzinfo=timezone.utc),
        )
        self.assertIn("run envelope is expired", errors)

    def test_envelope_rejects_expiry_against_default_current_time(self):
        envelope = self.load_vector("immutable_run_envelope")
        now = datetime.now(timezone.utc)
        envelope["created_at"] = (now - timedelta(hours=2)).isoformat().replace(
            "+00:00", "Z"
        )
        envelope["expires_at"] = (now - timedelta(hours=1)).isoformat().replace(
            "+00:00", "Z"
        )
        envelope["canonical_digest"] = contracts._canonical_sha256(
            envelope, "canonical_digest"
        )

        errors = contracts.validate_contract_instance(
            "immutable_run_envelope", envelope
        )

        self.assertIn("run envelope is expired", errors)

    def test_envelope_rejects_future_creation_against_current_time(self):
        envelope = self.load_vector("immutable_run_envelope")
        now = datetime.now(timezone.utc)
        envelope["created_at"] = (now + timedelta(hours=1)).isoformat().replace(
            "+00:00", "Z"
        )
        envelope["expires_at"] = (now + timedelta(hours=2)).isoformat().replace(
            "+00:00", "Z"
        )
        envelope["canonical_digest"] = contracts._canonical_sha256(
            envelope, "canonical_digest"
        )

        errors = contracts.validate_contract_instance(
            "immutable_run_envelope", envelope
        )

        self.assertIn("run envelope creation is in the future", errors)

    def test_envelope_binds_url_repository_and_trigger_mode(self):
        envelope = self.load_vector("immutable_run_envelope")
        envelope["trigger"]["repository"] = "other/repository"
        errors = contracts.validate_contract_instance(
            "immutable_run_envelope", envelope
        )
        self.assertIn("run envelope URL repository must match trigger repository", errors)

        envelope = self.load_vector("immutable_run_envelope")
        envelope["trigger"]["mode"] = "explicit_issue"
        errors = contracts.validate_contract_instance(
            "immutable_run_envelope", envelope
        )
        self.assertIn("explicit_issue mode requires a numbered issue URL", errors)

        envelope = self.load_vector("immutable_run_envelope")
        envelope["trigger"]["canonical_url"] += "/101"
        errors = contracts.validate_contract_instance(
            "immutable_run_envelope", envelope
        )
        self.assertIn("issue_list mode requires an issue-list URL", errors)

    def test_envelope_lineage_is_strict_for_origin_and_successor(self):
        envelope = self.load_vector("immutable_run_envelope")
        envelope["predecessor_digest"] = "a" * 64
        envelope["lineage"]["predecessor_digest"] = "a" * 64
        envelope["lineage"]["predecessor_run_id"] = "repair-run-previous"
        errors = contracts.validate_contract_instance(
            "immutable_run_envelope", envelope
        )
        self.assertIn("origin envelope predecessor fields must be null", errors)

        envelope = self.load_vector("immutable_run_envelope")
        envelope["lineage"]["kind"] = "same_envelope_resume"
        errors = contracts.validate_contract_instance(
            "immutable_run_envelope", envelope
        )
        self.assertTrue(
            any("lineage.kind" in error or "one of" in error for error in errors),
            errors,
        )

        envelope = self.load_vector("immutable_run_envelope")
        envelope["lineage"]["kind"] = "narrower_successor"
        errors = contracts.validate_contract_instance(
            "immutable_run_envelope", envelope
        )
        self.assertIn(
            "narrower successor lineage requires bound predecessor fields", errors
        )

    def test_envelope_auto_merge_requires_explicit_sole_control_opt_in(self):
        envelope = self.load_vector("immutable_run_envelope")
        self.assertFalse(
            envelope["governance"].get("sole_control_auto_merge_opt_in")
        )

        envelope["governance"]["allowed_actions"].append("auto_merge")
        errors = contracts.validate_contract_instance(
            "immutable_run_envelope", envelope
        )
        self.assertIn("auto_merge requires sole-control explicit opt-in", errors)

        envelope = self.load_vector("immutable_run_envelope")
        envelope["governance"]["sole_control_auto_merge_opt_in"] = True
        errors = contracts.validate_contract_instance(
            "immutable_run_envelope", envelope
        )
        self.assertIn(
            "auto-merge opt-in is only valid for sole_control governance", errors
        )

    def test_successor_requires_exact_trigger_loop_and_routing_identity(self):
        mutations = (
            ("trigger", "mode", "explicit_issue", "successor trigger must exactly match predecessor"),
            ("loop", "goal", "widened goal", "successor loop must exactly match predecessor"),
            ("routing", "fork_owner", "other", "successor routing.fork_owner must match predecessor"),
            ("routing", "repair_branch", "codex/other", "successor routing.repair_branch must match predecessor"),
        )
        for owner, field, value, expected in mutations:
            predecessor, successor = self.successor_envelope()
            successor[owner][field] = value
            errors = contracts.validate_successor_envelope(predecessor, successor)
            self.assertIn(expected, errors)

    def test_successor_cannot_drop_guards_or_change_terminal_statuses(self):
        predecessor, successor = self.successor_envelope()
        successor["routing"]["protected_path_classes"].pop()
        errors = contracts.validate_successor_envelope(predecessor, successor)
        self.assertIn(
            "successor protected_path_classes must include predecessor guards",
            errors,
        )

        predecessor, successor = self.successor_envelope()
        successor["routing"]["required_checks"].pop()
        errors = contracts.validate_successor_envelope(predecessor, successor)
        self.assertIn(
            "successor required_checks must include predecessor checks", errors
        )

        predecessor, successor = self.successor_envelope()
        successor["stop_conditions"].pop()
        errors = contracts.validate_successor_envelope(predecessor, successor)
        self.assertIn(
            "successor stop_conditions must include predecessor conditions", errors
        )

        predecessor, successor = self.successor_envelope()
        successor["terminal_statuses"].pop()
        errors = contracts.validate_successor_envelope(predecessor, successor)
        self.assertIn(
            "successor terminal_statuses must exactly match predecessor", errors
        )

    def test_successor_cannot_move_creation_backward_or_extend_expiry(self):
        predecessor, successor = self.successor_envelope()
        predecessor["created_at"] = "2026-07-27T20:00:00Z"
        successor["created_at"] = "2026-07-27T19:59:59Z"
        errors = contracts.validate_successor_envelope(predecessor, successor)
        self.assertIn("successor created_at must not move backward", errors)

        predecessor, successor = self.successor_envelope()
        successor["expires_at"] = "2026-07-30T00:00:00Z"
        errors = contracts.validate_successor_envelope(predecessor, successor)
        self.assertIn("successor expires_at must not extend predecessor", errors)

    def test_governance_decision_has_a_bound_canonical_digest(self):
        governance = self.load_vector("governance_decision")
        self.assertRegex(governance.get("decision_digest", ""), r"^[0-9a-f]{64}$")
        governance["head_sha"] = "c" * 40
        errors = contracts.validate_contract_instance(
            "governance_decision", governance
        )
        self.assertIn(
            "governance decision digest does not match canonical fields", errors
        )

    def test_governance_unauthorized_merge_requires_never_mode(self):
        governance = self.load_vector("governance_decision")
        governance["merge"]["mode"] = "manual"
        errors = contracts.validate_contract_instance(
            "governance_decision", governance
        )
        self.assertIn("unauthorized governance merge mode must be never", errors)

    def test_any_authorized_merge_requires_safe_exact_head_checks(self):
        governance = self.load_vector("governance_decision")
        governance["governance_class"] = "sole_control"
        governance["push_target"] = "authorized_operator_repository"
        governance["pull_request_mode"] = "draft_or_ready_by_policy"
        governance["merge"]["authorized"] = True
        governance["merge"]["mode"] = "manual"
        governance["merge"]["auto_merge_opt_in"] = False

        governance["protected_path_touched"] = True
        governance["required_checks"] = []
        errors = contracts.validate_contract_instance(
            "governance_decision", governance
        )
        self.assertIn("authorized merge must not touch protected paths", errors)
        self.assertIn(
            "authorized merge requires nonempty all-success exact-head checks", errors
        )

        governance["protected_path_touched"] = False
        governance["required_checks"] = [
            {
                "name": "test",
                "conclusion": "pending",
                "head_sha": governance["head_sha"],
            }
        ]
        errors = contracts.validate_contract_instance(
            "governance_decision", governance
        )
        self.assertIn(
            "authorized merge requires nonempty all-success exact-head checks", errors
        )

    def test_sole_control_auto_merge_requires_explicit_opt_in(self):
        governance = self.load_vector("governance_decision")
        governance["governance_class"] = "sole_control"
        governance["push_target"] = "authorized_operator_repository"
        governance["pull_request_mode"] = "draft_or_ready_by_policy"
        governance["merge"]["authorized"] = True
        governance["merge"]["mode"] = "auto_merge"
        governance["merge"]["auto_merge_opt_in"] = False
        errors = contracts.validate_contract_instance(
            "governance_decision", governance
        )
        self.assertIn("sole-control auto_merge requires explicit opt-in", errors)

    def test_team_merge_requires_merge_queue_and_exact_independent_approval(self):
        governance = self.load_vector("governance_decision")
        governance["governance_class"] = "team"
        governance["push_target"] = "policy_authorized_branch"
        governance["pull_request_mode"] = "draft_or_ready_by_policy"
        governance["merge"]["authorized"] = True
        governance["merge"]["mode"] = "manual"
        governance["merge"]["approval_kind"] = "independent_human"
        governance["merge"]["approval_head_sha"] = governance["head_sha"]
        errors = contracts.validate_contract_instance(
            "governance_decision", governance
        )
        self.assertIn("team merge must use merge_queue", errors)

        governance["merge"]["mode"] = "merge_queue"
        governance["merge"]["approval_head_sha"] = "c" * 40
        errors = contracts.validate_contract_instance(
            "governance_decision", governance
        )
        self.assertIn(
            "team merge requires independent approval on the exact head SHA",
            errors,
        )

    def test_external_and_unknown_governance_have_permanent_denials(self):
        for governance_class in ("external", "unknown"):
            governance = self.load_vector("governance_decision")
            governance["governance_class"] = governance_class
            governance["merge"]["approval_kind"] = "independent_human"
            governance["merge"]["approval_head_sha"] = governance["head_sha"]
            governance["merge"]["auto_merge_opt_in"] = True
            errors = contracts.validate_contract_instance(
                "governance_decision", governance
            )
            self.assertIn(
                f"{governance_class} governance must not carry merge approval",
                errors,
            )
            self.assertIn(
                f"{governance_class} governance must not opt into auto-merge",
                errors,
            )

    def test_reviewer_result_has_a_bound_canonical_digest(self):
        review = self.load_vector("reviewer_independence")
        self.assertRegex(review.get("review_digest", ""), r"^[0-9a-f]{64}$")
        review["reviewer_id"] = "different-reviewer"
        errors = contracts.validate_contract_instance(
            "reviewer_independence", review
        )
        self.assertIn(
            "reviewer independence digest does not match canonical fields", errors
        )

    def test_action_digest_requires_nonempty_write_checks(self):
        action = self.load_vector("github_action_digest")
        action["required_checks"] = []
        errors = contracts.validate_contract_instance(
            "github_action_digest",
            action,
            reference_time=datetime(2026, 7, 28, tzinfo=timezone.utc),
        )
        self.assertTrue(
            any("required_checks" in error for error in errors),
            errors,
        )

    def test_action_digest_binds_all_upstream_decision_digests(self):
        action = self.load_vector("github_action_digest")
        expected_fields = (
            "run_envelope_digest",
            "candidate_decision_digest",
            "governance_decision_digest",
            "reviewer_independence_digest",
        )
        for field in expected_fields:
            self.assertRegex(action.get(field, ""), r"^[0-9a-f]{64}$", field)

        expected_errors = {
            "run_envelope_digest": (
                "action run_envelope_digest must match canonical envelope"
            ),
            "candidate_decision_digest": (
                "action candidate_decision_digest must match canonical candidate"
            ),
            "governance_decision_digest": (
                "action governance_decision_digest must match canonical governance"
            ),
            "reviewer_independence_digest": (
                "action reviewer_independence_digest must match canonical review"
            ),
        }
        for field, expected in expected_errors.items():
            mutated = copy.deepcopy(action)
            mutated[field] = "0" * 64
            errors = contracts.validate_action_digest_links(
                mutated,
                self.load_vector("immutable_run_envelope"),
                self.load_vector("candidate_decision"),
                self.load_vector("governance_decision"),
                self.load_vector("reviewer_independence"),
            )
            self.assertIn(expected, errors)

    def test_action_links_reject_reviewer_subject_substitution_exploit(self):
        action, envelope, candidate, governance, reviewer = (
            self.coherent_action_family()
        )
        reviewer["subject_digest"] = "c" * 64
        reviewer["review_digest"] = contracts._canonical_sha256(
            reviewer, "review_digest"
        )
        action["reviewer_independence_digest"] = reviewer["review_digest"]
        action["action_digest"] = contracts._canonical_sha256(
            action, "action_digest"
        )

        errors = contracts.validate_action_digest_links(
            action, envelope, candidate, governance, reviewer
        )

        self.assertIn("reviewer subject must match action diff digest", errors)

    def test_action_links_reject_unrelated_auto_merge_exploit(self):
        action, envelope, candidate, governance, reviewer = (
            self.coherent_action_family()
        )
        action["action"] = "auto_merge"
        action["action_digest"] = contracts._canonical_sha256(
            action, "action_digest"
        )

        errors = contracts.validate_action_digest_links(
            action, envelope, candidate, governance, reviewer
        )

        self.assertIn("action must be allowed by the run envelope", errors)
        self.assertIn(
            "auto_merge requires governance authorization in auto_merge mode",
            errors,
        )

    def test_action_expiry_cannot_outlive_envelope(self):
        action, envelope, candidate, governance, reviewer = (
            self.coherent_action_family()
        )
        action["expires_at"] = "2026-07-28T00:00:01Z"
        action["action_digest"] = contracts._canonical_sha256(
            action, "action_digest"
        )

        errors = contracts.validate_action_digest_links(
            action,
            envelope,
            candidate,
            governance,
            reviewer,
            reference_time=datetime(2026, 7, 27, 23, 30, tzinfo=timezone.utc),
        )

        self.assertIn("action expiry must not outlive run envelope", errors)

    def test_action_family_rejects_execution_after_envelope_expiry(self):
        action, envelope, candidate, governance, reviewer = (
            self.coherent_action_family()
        )
        action["expires_at"] = "2026-07-28T01:00:00Z"
        action["action_digest"] = contracts._canonical_sha256(
            action, "action_digest"
        )

        errors = contracts.validate_action_digest_links(
            action,
            envelope,
            candidate,
            governance,
            reviewer,
            reference_time=datetime(2026, 7, 28, 0, 1, tzinfo=timezone.utc),
        )

        self.assertIn(
            "immutable_run_envelope: run envelope is expired", errors
        )

    def test_action_links_reconcile_identity_destination_and_checks(self):
        mutations = (
            ("run_id", "other-repair-run", "action run_id must match all authority documents"),
            ("repository", "other/repository", "action repository must match all authority documents"),
            ("issue_number", 999, "action issue_number must match selected candidate"),
            ("base_sha", "2" * 40, "action base_sha must match all authority documents"),
            ("head_sha", "3" * 40, "action head_sha must match governance"),
            ("fork", "other/repair-fixture", "operator-owned fork governance requires a nonnull exact fork"),
            ("branch", "codex/other", "action branch must match envelope repair branch"),
        )
        for field, value, expected in mutations:
            with self.subTest(field=field):
                action, envelope, candidate, governance, reviewer = (
                    self.coherent_action_family()
                )
                action[field] = value
                action["action_digest"] = contracts._canonical_sha256(
                    action, "action_digest"
                )
                errors = contracts.validate_action_digest_links(
                    action, envelope, candidate, governance, reviewer
                )
                self.assertIn(expected, errors)

        action, envelope, candidate, governance, reviewer = (
            self.coherent_action_family()
        )
        candidate["decision"] = "eligible"
        candidate["decision_digest"] = contracts._canonical_sha256(
            candidate, "decision_digest"
        )
        action["candidate_decision_digest"] = candidate["decision_digest"]
        action["action_digest"] = contracts._canonical_sha256(
            action, "action_digest"
        )
        errors = contracts.validate_action_digest_links(
            action, envelope, candidate, governance, reviewer
        )
        self.assertIn("action candidate must be selected", errors)

        action, envelope, candidate, governance, reviewer = (
            self.coherent_action_family()
        )
        action["required_checks"][0]["name"] = "other"
        action["action_digest"] = contracts._canonical_sha256(
            action, "action_digest"
        )
        errors = contracts.validate_action_digest_links(
            action, envelope, candidate, governance, reviewer
        )
        self.assertIn(
            "action checks must exactly match successful governance and envelope checks",
            errors,
        )

    def test_action_names_are_direct_envelope_permissions(self):
        schema_path = contracts.AUTONOMOUS_CONTRACTS["github_action_digest"][1]
        schema = json.loads((ROOT / schema_path).read_text())
        self.assertEqual(
            schema["properties"]["action"]["enum"],
            [
                "push_operator_fork",
                "open_upstream_draft_pr",
                "open_ready_pr",
                "request_merge_queue",
                "auto_merge",
            ],
        )

    def test_canonical_external_action_is_bound_to_draft_only_governance(self):
        action, envelope, candidate, governance, reviewer = (
            self.coherent_action_family()
        )
        errors = contracts.validate_action_digest_links(
            action,
            envelope,
            candidate,
            governance,
            reviewer,
            reference_time=datetime(2026, 7, 27, 23, 30, tzinfo=timezone.utc),
        )
        self.assertEqual(errors, [])
        self.assertEqual(action["action"], "open_upstream_draft_pr")
        self.assertIn(action["action"], envelope["governance"]["allowed_actions"])
        self.assertEqual(governance["governance_class"], "external")
        self.assertEqual(governance["push_target"], "operator_owned_fork")
        self.assertEqual(governance["pull_request_mode"], "upstream_draft_only")
        self.assertFalse(governance["merge"]["authorized"])
        self.assertEqual(governance["merge"]["mode"], "never")

    def test_action_links_enforce_action_specific_governance(self):
        action, envelope, candidate, governance, reviewer = (
            self.coherent_action_family()
        )
        action["action"] = "push_operator_fork"
        governance["push_target"] = "policy_authorized_branch"
        governance["decision_digest"] = contracts._canonical_sha256(
            governance, "decision_digest"
        )
        action["governance_decision_digest"] = governance["decision_digest"]
        action["action_digest"] = contracts._canonical_sha256(
            action, "action_digest"
        )
        errors = contracts.validate_action_digest_links(
            action, envelope, candidate, governance, reviewer
        )
        self.assertIn(
            "push_operator_fork requires operator-owned fork governance", errors
        )

        action, envelope, candidate, governance, reviewer = (
            self.coherent_action_family()
        )
        action["action"] = "open_ready_pr"
        envelope["governance"]["ownership_class"] = "team"
        envelope["governance"]["allowed_actions"].append("open_ready_pr")
        envelope["canonical_digest"] = contracts._canonical_sha256(
            envelope, "canonical_digest"
        )
        governance["governance_class"] = "team"
        governance["pull_request_mode"] = "upstream_draft_only"
        governance["decision_digest"] = contracts._canonical_sha256(
            governance, "decision_digest"
        )
        action["run_envelope_digest"] = envelope["canonical_digest"]
        action["governance_decision_digest"] = governance["decision_digest"]
        action["action_digest"] = contracts._canonical_sha256(
            action, "action_digest"
        )
        errors = contracts.validate_action_digest_links(
            action, envelope, candidate, governance, reviewer
        )
        self.assertIn(
            "open_ready_pr requires non-external policy-ready governance", errors
        )

        for action_name, governance_mode in (
            ("request_merge_queue", "merge_queue"),
            ("auto_merge", "auto_merge"),
        ):
            with self.subTest(action=action_name):
                action, envelope, candidate, governance, reviewer = (
                    self.coherent_action_family()
                )
                envelope["governance"]["ownership_class"] = "sole_control"
                envelope["governance"]["allowed_actions"].append(action_name)
                if action_name == "auto_merge":
                    envelope["governance"][
                        "sole_control_auto_merge_opt_in"
                    ] = True
                envelope["canonical_digest"] = contracts._canonical_sha256(
                    envelope, "canonical_digest"
                )
                governance["governance_class"] = "sole_control"
                governance["push_target"] = "authorized_operator_repository"
                governance["pull_request_mode"] = "draft_or_ready_by_policy"
                governance["merge"]["authorized"] = False
                governance["merge"]["mode"] = "never"
                governance["decision_digest"] = contracts._canonical_sha256(
                    governance, "decision_digest"
                )
                action["action"] = action_name
                action["run_envelope_digest"] = envelope["canonical_digest"]
                action["governance_decision_digest"] = governance["decision_digest"]
                action["action_digest"] = contracts._canonical_sha256(
                    action, "action_digest"
                )
                errors = contracts.validate_action_digest_links(
                    action, envelope, candidate, governance, reviewer
                )
                self.assertIn(
                    f"{action_name} requires governance authorization in "
                    f"{governance_mode} mode",
                    errors,
                )

    def test_team_merge_queue_requires_linked_independent_reviewer_gate(self):
        for status, satisfies_gate in (
            ("unverified", False),
            ("independent", False),
        ):
            with self.subTest(status=status, satisfies_gate=satisfies_gate):
                action, envelope, candidate, governance, reviewer = (
                    self.non_fork_action_family("team", "request_merge_queue")
                )
                envelope["routing"]["fork_owner"] = "operator"
                envelope["canonical_digest"] = contracts._canonical_sha256(
                    envelope, "canonical_digest"
                )
                governance["push_target"] = "operator_owned_fork"
                governance["decision_digest"] = contracts._canonical_sha256(
                    governance, "decision_digest"
                )
                action["fork"] = "operator/repair-fixture"
                action["run_envelope_digest"] = envelope["canonical_digest"]
                action["governance_decision_digest"] = governance["decision_digest"]
                reviewer["status"] = status
                reviewer["satisfies_team_merge_gate"] = satisfies_gate
                reviewer["review_digest"] = contracts._canonical_sha256(
                    reviewer, "review_digest"
                )
                action["reviewer_independence_digest"] = reviewer["review_digest"]
                action["action_digest"] = contracts._canonical_sha256(
                    action, "action_digest"
                )

                errors = contracts.validate_action_digest_links(
                    action,
                    envelope,
                    candidate,
                    governance,
                    reviewer,
                    reference_time=datetime(
                        2026, 7, 27, 23, 30, tzinfo=timezone.utc
                    ),
                )

                self.assertIn(
                    "team request_merge_queue requires a linked independent "
                    "reviewer satisfying the team merge gate",
                    errors,
                )

    def test_required_check_names_are_unique_in_action_and_governance(self):
        action = self.load_vector("github_action_digest")
        action["required_checks"].append(copy.deepcopy(action["required_checks"][0]))
        action["action_digest"] = contracts._canonical_sha256(
            action, "action_digest"
        )
        errors = contracts.validate_contract_instance(
            "github_action_digest",
            action,
            reference_time=datetime(2026, 7, 27, 23, 30, tzinfo=timezone.utc),
        )
        self.assertIn("github action required check names must be unique", errors)

        governance = self.load_vector("governance_decision")
        governance["required_checks"].append(
            copy.deepcopy(governance["required_checks"][0])
        )
        governance["decision_digest"] = contracts._canonical_sha256(
            governance, "decision_digest"
        )
        errors = contracts.validate_contract_instance(
            "governance_decision", governance
        )
        self.assertIn("governance required check names must be unique", errors)

    def test_required_check_cross_link_is_an_order_independent_exact_set(self):
        action, envelope, candidate, governance, reviewer = (
            self.coherent_action_family()
        )
        action["required_checks"].reverse()
        governance["required_checks"].reverse()
        governance["decision_digest"] = contracts._canonical_sha256(
            governance, "decision_digest"
        )
        action["governance_decision_digest"] = governance["decision_digest"]
        action["action_digest"] = contracts._canonical_sha256(
            action, "action_digest"
        )

        errors = contracts.validate_action_digest_links(
            action,
            envelope,
            candidate,
            governance,
            reviewer,
            reference_time=datetime(2026, 7, 27, 23, 30, tzinfo=timezone.utc),
        )

        self.assertEqual(errors, [])

    def test_sole_and_team_non_fork_actions_require_null_fork(self):
        for ownership_class, action_name in (
            ("sole_control", "open_ready_pr"),
            ("team", "request_merge_queue"),
        ):
            with self.subTest(
                ownership_class=ownership_class, action_name=action_name
            ):
                action, envelope, candidate, governance, reviewer = (
                    self.non_fork_action_family(ownership_class, action_name)
                )
                errors = contracts.validate_action_digest_links(
                    action,
                    envelope,
                    candidate,
                    governance,
                    reviewer,
                    reference_time=datetime(
                        2026, 7, 27, 23, 30, tzinfo=timezone.utc
                    ),
                )
                self.assertEqual(errors, [])

    def test_non_fork_action_rejects_literal_none_repository(self):
        action, envelope, candidate, governance, reviewer = (
            self.non_fork_action_family("team", "request_merge_queue")
        )
        action["fork"] = "None/repair-fixture"
        action["action_digest"] = contracts._canonical_sha256(
            action, "action_digest"
        )

        errors = contracts.validate_action_digest_links(
            action,
            envelope,
            candidate,
            governance,
            reviewer,
            reference_time=datetime(2026, 7, 27, 23, 30, tzinfo=timezone.utc),
        )

        self.assertIn(
            "non-fork governance requires null envelope and action fork", errors
        )

    def test_operator_owned_fork_requires_nonnull_exact_fork(self):
        action, envelope, candidate, governance, reviewer = (
            self.coherent_action_family()
        )
        envelope["routing"]["fork_owner"] = None
        envelope["canonical_digest"] = contracts._canonical_sha256(
            envelope, "canonical_digest"
        )
        action["fork"] = None
        action["run_envelope_digest"] = envelope["canonical_digest"]
        action["action_digest"] = contracts._canonical_sha256(
            action, "action_digest"
        )

        errors = contracts.validate_action_digest_links(
            action,
            envelope,
            candidate,
            governance,
            reviewer,
            reference_time=datetime(2026, 7, 27, 23, 30, tzinfo=timezone.utc),
        )

        self.assertIn(
            "operator-owned fork governance requires a nonnull exact fork",
            errors,
        )

    def test_action_links_validate_all_five_documents(self):
        action, envelope, candidate, governance, reviewer = (
            self.coherent_action_family()
        )
        envelope["unknown_authority"] = True
        candidate["decision_digest"] = "0" * 64
        governance["required_checks"][0]["conclusion"] = "pending"
        reviewer["deterministic_tests_primary"] = False
        action["expires_at"] = action["approved_at"]

        errors = contracts.validate_action_digest_links(
            action,
            envelope,
            candidate,
            governance,
            reviewer,
            reference_time=datetime(2026, 7, 27, 23, 30, tzinfo=timezone.utc),
        )

        for prefix in (
            "immutable_run_envelope:",
            "candidate_decision:",
            "governance_decision:",
            "reviewer_independence:",
            "github_action_digest:",
        ):
            self.assertTrue(
                any(error.startswith(prefix) for error in errors),
                (prefix, errors),
            )

    def test_action_links_fail_closed_for_malformed_document(self):
        action, envelope, candidate, governance, reviewer = (
            self.coherent_action_family()
        )
        del action["repository"]

        errors = contracts.validate_action_digest_links(
            action,
            envelope,
            candidate,
            governance,
            reviewer,
            reference_time=datetime(2026, 7, 27, 23, 30, tzinfo=timezone.utc),
        )

        self.assertTrue(
            any(
                error.startswith("github_action_digest:")
                and "repository" in error
                for error in errors
            ),
            errors,
        )

    def test_action_rejects_future_approval_against_current_time(self):
        action = self.load_vector("github_action_digest")
        now = datetime.now(timezone.utc)
        action["approved_at"] = (now + timedelta(hours=1)).isoformat().replace(
            "+00:00", "Z"
        )
        action["expires_at"] = (now + timedelta(hours=2)).isoformat().replace(
            "+00:00", "Z"
        )
        action["action_digest"] = contracts._canonical_sha256(
            action, "action_digest"
        )

        errors = contracts.validate_contract_instance(
            "github_action_digest", action
        )

        self.assertIn("github action approval is in the future", errors)

    def test_action_approval_must_follow_each_authority_source(self):
        cases = (
            (
                "envelope",
                "2026-07-27T15:59:00Z",
                "2026-07-28T15:59:00Z",
                "action approval must not predate envelope creation",
            ),
            (
                "candidate",
                "2026-07-27T21:59:00Z",
                "2026-07-28T21:59:00Z",
                "action approval must not predate candidate decision",
            ),
            (
                "governance",
                "2026-07-27T23:09:00Z",
                "2026-07-28T23:09:00Z",
                "action approval must not predate governance decision",
            ),
            (
                "reviewer",
                "2026-07-27T23:14:00Z",
                "2026-07-28T23:14:00Z",
                "action approval must not predate reviewer decision",
            ),
        )
        for source, approved_at, expires_at, expected in cases:
            with self.subTest(source=source):
                action, envelope, candidate, governance, reviewer = (
                    self.coherent_action_family()
                )
                action["approved_at"] = approved_at
                action["expires_at"] = expires_at
                action["action_digest"] = contracts._canonical_sha256(
                    action, "action_digest"
                )

                errors = contracts.validate_action_digest_links(
                    action,
                    envelope,
                    candidate,
                    governance,
                    reviewer,
                    reference_time=datetime(
                        2026, 7, 27, 23, 30, tzinfo=timezone.utc
                    ),
                )

                self.assertIn(expected, errors)

    def test_authority_evidence_must_not_predate_envelope_creation(self):
        cases = (
            (
                "candidate",
                "decided_at",
                "candidate decision must not predate envelope creation",
            ),
            (
                "governance",
                "decided_at",
                "governance decision must not predate envelope creation",
            ),
            (
                "reviewer",
                "reviewed_at",
                "reviewer decision must not predate envelope creation",
            ),
        )
        for source, field, expected in cases:
            with self.subTest(source=source):
                action, envelope, candidate, governance, reviewer = (
                    self.coherent_action_family()
                )
                documents = {
                    "candidate": (candidate, "decision_digest"),
                    "governance": (governance, "decision_digest"),
                    "reviewer": (reviewer, "review_digest"),
                }
                document, digest_field = documents[source]
                document[field] = "2026-07-27T15:59:00Z"
                document[digest_field] = contracts._canonical_sha256(
                    document, digest_field
                )
                action[
                    {
                        "candidate": "candidate_decision_digest",
                        "governance": "governance_decision_digest",
                        "reviewer": "reviewer_independence_digest",
                    }[source]
                ] = document[digest_field]
                action["action_digest"] = contracts._canonical_sha256(
                    action, "action_digest"
                )

                errors = contracts.validate_action_digest_links(
                    action,
                    envelope,
                    candidate,
                    governance,
                    reviewer,
                    reference_time=datetime(
                        2026, 7, 27, 23, 30, tzinfo=timezone.utc
                    ),
                )

                self.assertIn(expected, errors)

    def test_valid_authority_chronology_accepts_reference_at_approval(self):
        action, envelope, candidate, governance, reviewer = (
            self.coherent_action_family()
        )

        errors = contracts.validate_action_digest_links(
            action,
            envelope,
            candidate,
            governance,
            reviewer,
            reference_time=datetime(2026, 7, 27, 23, 20, tzinfo=timezone.utc),
        )

        self.assertEqual(errors, [])

    def test_action_approval_lifetime_is_at_most_twenty_four_hours(self):
        action = self.load_vector("github_action_digest")
        action["expires_at"] = "2026-07-29T23:20:01Z"
        errors = contracts.validate_contract_instance(
            "github_action_digest",
            action,
            reference_time=datetime(2026, 7, 28, tzinfo=timezone.utc),
        )
        self.assertIn("github action approval lifetime must not exceed 24 hours", errors)

    def test_strict_rfc3339_rejects_spaces_and_second_offsets(self):
        self.assertIsNone(contracts._parse_timestamp("2026-07-27 23:20:00Z"))
        self.assertIsNone(
            contracts._parse_timestamp("2026-07-27T23:20:00+00:00:30")
        )


if __name__ == "__main__":
    unittest.main()
