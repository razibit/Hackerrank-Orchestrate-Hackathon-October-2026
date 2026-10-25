import json
import os
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATASET_ROOT = Path(os.environ.get("GHOST_DATASET_PATH", ROOT / "dataset")).resolve()
sys.path.insert(0, str(ROOT / "code"))
sys.path.insert(0, str(ROOT / "code" / "tools"))

from audit_agent.engine import AuditBlocked, CandidateIndex, audit_case
from audit_agent.identity import IdentityResolver
from audit_agent.policy import load_policy, required_treatment
from audit_agent.types import Observation
from contract import instant, validate


AUDIT_AT = "2026-09-01T00:00:00Z"
REQUESTED_AT = "2026-04-01T00:00:00Z"
NOW = datetime.fromisoformat("2026-08-20T12:00:00+00:00")


class StructuredFixtureModel:
    """Test-only structured-output fixture; never used by the production CLI."""

    def __init__(self, corrupt=False):
        self.calls = 0
        self.corrupt = corrupt

    def chat_json(self, purpose, system_prompt, payload, schema, max_tokens=3000):
        self.calls += 1
        if self.corrupt:
            return {"observations": []}
        answers = []
        for item in payload["observations"]:
            fields = item["fields"]
            answers.append({
                "observation_id": item["observation_id"],
                "system_id": item["system_id"] or fields.get("fixture_system_id", ""),
                "resource_id": item["resource_id"] or fields.get("fixture_resource_id", ""),
                "relevant_to_subject": "YES",
                "category": fields.get("fixture_category", item["category_hint"]),
                "state": fields.get("fixture_state", item["state_hint"]),
                "identifiers_exposed": fields.get("fixture_exposed", "NO"),
                "policy_condition": fields.get("fixture_condition", "NOT_APPLICABLE"),
                "scope_complete": "TRUE" if item["scope_complete"] is True else "FALSE",
                "reason": "Synthetic grounded fixture classification.",
            })
        return {"observations": answers}


class UnresolvedRelevanceFixtureModel(StructuredFixtureModel):
    def chat_json(self, purpose, system_prompt, payload, schema, max_tokens=3000):
        result = super().chat_json(purpose, system_prompt, payload, schema, max_tokens)
        for item in result.get("observations", []):
            item["relevant_to_subject"] = "UNRESOLVED"
        return result


class SupportPolicyFixtureModel(StructuredFixtureModel):
    def __init__(self, condition="TRUE"):
        super().__init__()
        self.policy_calls = 0
        self.condition = condition

    def chat_json(self, purpose, system_prompt, payload, schema, max_tokens=3000):
        if purpose == "policy_condition_resolution":
            self.policy_calls += 1
            return {"policy_conditions": [
                {"observation_id": item["observation_id"], "condition": self.condition,
                 "reason": "Synthetic direct message context was reviewed."}
                for item in payload["observations"]
            ]}
        result = super().chat_json(purpose, system_prompt, payload, schema, max_tokens)
        for item in result.get("observations", []):
            if item.get("category") == "SUPPORT_MESSAGE":
                item["policy_condition"] = "UNRESOLVED"
        return result


class AlteredIdentifierFixtureModel(StructuredFixtureModel):
    def chat_json(self, purpose, system_prompt, payload, schema, max_tokens=3000):
        result = super().chat_json(purpose, system_prompt, payload, schema, max_tokens)
        for item in result.get("observations", []):
            item["system_id"] = "model-invented-system"
            item["resource_id"] = "model-invented-resource"
        return result


def evidence(
    evidence_id,
    system_id,
    resource_id,
    category,
    state,
    proof_kind="snapshot",
    *,
    user_id="user_1",
    scope="",
    observed_at=NOW,
    available_at=NOW,
    exposed="NO",
    condition="NOT_APPLICABLE",
    source_kind="sql",
):
    return Observation(
        evidence_id=evidence_id,
        locator="synthetic:1",
        available_at=available_at,
        observed_at=observed_at,
        system_id=system_id,
        resource_id=resource_id,
        scope_id=scope,
        category=category,
        state=state,
        fields={
            "user_id": user_id,
            "fixture_category": category,
            "fixture_state": state,
            "fixture_exposed": exposed,
            "fixture_condition": condition,
            "scope_id": scope,
        },
        source_kind=source_kind,
        proof_kind=proof_kind,
        scope_complete=True,
        raw_text="",
    )


def fixture_context():
    identities = [{
        "user_id": "user_1", "name": "Synthetic Person", "email": "new@example.test",
        "phone": "+1 555 010 0001", "email_hash": "hash-new", "updated_at": "2026-05-01T00:00:00Z",
    }]
    audit = [{
        "audit_id": "audit-old-email", "user_id": "user_1", "event_time": "2026-05-01T00:00:00Z",
        "field_name": "email", "old_value": "old@example.test", "new_value": "new@example.test",
    }]
    requests = [{
        "case_id": "synthetic_case", "email": "old@example.test", "requested_at": REQUESTED_AT,
        "audit_at": AUDIT_AT, "reported_status": "COMPLETE", "reported_at": AUDIT_AT,
        "request_text": "Please erase my account and personal information.",
    }]
    return requests[0], IdentityResolver(identities, audit)


def rules():
    rows = []
    with (DATASET_ROOT / "deletion_rules.csv").open(encoding="utf-8-sig", newline="") as stream:
        import csv
        rows = list(csv.DictReader(stream))
    return load_policy(rows)


def run_case(request, resolver, records, activity=None, model=None):
    return audit_case(
        request,
        {"intent": "DELETE", "confidence": "HIGH", "reason": "Synthetic request"},
        resolver,
        records,
        activity or [],
        rules(),
        model or StructuredFixtureModel(),
        "Synthetic test prompt.",
    )


class AuditAgentTests(unittest.TestCase):
    def test_direct_identity_match_expands_to_same_resource_readbacks(self):
        request, resolver = fixture_context()
        cutoff = datetime.fromisoformat(AUDIT_AT.replace("Z", "+00:00"))
        linked = evidence("evidence-linked", "account_service", "account-1", "USER_PROFILE", "PRESENT")
        linked.fields.pop("fixture_category")
        linked.fields["email"] = "old@example.test"
        readback = Observation(
            evidence_id="evidence-readback", locator="row:2", available_at=NOW, observed_at=NOW,
            system_id="account_service", resource_id="account-1", scope_id="primary", category="USER_PROFILE",
            state="ABSENT", fields={}, source_kind="json", proof_kind="readback",
        )
        candidates, _ = CandidateIndex([linked, readback], []).candidates(
            resolver.resolve(request["email"], datetime.fromisoformat(REQUESTED_AT.replace("Z", "+00:00")), cutoff),
            resolver,
            cutoff,
        )
        self.assertEqual({item.evidence_id for item in candidates}, {"evidence-linked", "evidence-readback"})

    def test_source_grounded_ids_override_model_mutations(self):
        request, resolver = fixture_context()
        record = evidence("evidence-profile", "profile_service", "profile-1", "USER_PROFILE", "PRESENT")
        result = run_case(request, resolver, [record], model=AlteredIdentifierFixtureModel())
        self.assertEqual(result.deletion_status, "INCOMPLETE")
        self.assertTrue(result.steps)
        self.assertTrue(all(step["system_id"] == "profile_service" for step in result.steps))
        self.assertTrue(all(step["resource_id"] == "profile-1" for step in result.steps))

    def test_explicit_logical_system_precedes_collector_service(self):
        request, resolver = fixture_context()
        record = evidence(
            "evidence-security", "search_index_service", "audit_record-1",
            "SECURITY_AUDIT_LOG", "PRESENT",
        )
        record.fields["service"] = "search_index_service"
        record.fields["system"] = "security_service"
        record.fields["retention_until"] = "2026-01-01"
        result = run_case(request, resolver, [record], model=AlteredIdentifierFixtureModel())
        self.assertTrue(result.steps)
        self.assertTrue(all(step["system_id"] == "security_service" for step in result.steps))
        self.assertTrue(all(step["resource_id"] == "audit_record-1" for step in result.steps))
    def test_identity_alias_ownership_is_time_valid_and_unique(self):
        identities = [
            {"user_id": "user_1", "email": "new@example.test", "updated_at": "2026-06-01T00:00:00Z"},
            {"user_id": "user_2", "email": "old@example.test", "updated_at": "2026-07-01T00:00:00Z"},
        ]
        audit = [{
            "audit_id": "audit-reassigned", "user_id": "user_1", "event_time": "2026-06-01T00:00:00Z",
            "field_name": "email", "old_value": "old@example.test", "new_value": "new@example.test",
        }]
        resolver = IdentityResolver(identities, audit)
        before_reassignment = datetime.fromisoformat("2026-05-15T00:00:00+00:00")
        after_reassignment = datetime.fromisoformat("2026-07-15T00:00:00+00:00")
        audit_cutoff = datetime.fromisoformat("2026-09-01T00:00:00+00:00")
        self.assertTrue(resolver.matches_as_of("user_1", "email", "old@example.test", before_reassignment, audit_cutoff))
        self.assertFalse(resolver.matches_as_of("user_1", "email", "old@example.test", after_reassignment, audit_cutoff))
        self.assertTrue(resolver.matches_as_of("user_2", "email", "old@example.test", after_reassignment, audit_cutoff))

    def test_expired_alias_can_link_residual_evidence_when_unreassigned(self):
        identities = [{"user_id": "user_1", "email": "new@example.test", "updated_at": "2026-06-01T00:00:00Z"}]
        audit = [{
            "audit_id": "audit-old-to-new", "user_id": "user_1", "event_time": "2026-06-01T00:00:00Z",
            "field_name": "email", "old_value": "old@example.test", "new_value": "new@example.test",
        }]
        resolver = IdentityResolver(identities, audit)
        observed_at = datetime.fromisoformat("2026-08-01T00:00:00+00:00")
        evidence_cutoff = datetime.fromisoformat("2026-09-01T00:00:00+00:00")
        self.assertTrue(resolver.matches_for_evidence(
            "user_1", "email", "old@example.test", observed_at, evidence_cutoff,
        ))

    def test_expired_alias_does_not_link_evidence_after_reassignment(self):
        identities = [
            {"user_id": "user_1", "email": "new@example.test", "updated_at": "2026-06-01T00:00:00Z"},
            {"user_id": "user_2", "email": "old@example.test", "updated_at": "2026-07-01T00:00:00Z"},
        ]
        audit = [{
            "audit_id": "audit-old-to-new", "user_id": "user_1", "event_time": "2026-06-01T00:00:00Z",
            "field_name": "email", "old_value": "old@example.test", "new_value": "new@example.test",
        }]
        resolver = IdentityResolver(identities, audit)
        observed_at = datetime.fromisoformat("2026-08-01T00:00:00+00:00")
        evidence_cutoff = datetime.fromisoformat("2026-09-01T00:00:00+00:00")
        self.assertFalse(resolver.matches_for_evidence(
            "user_1", "email", "old@example.test", observed_at, evidence_cutoff,
        ))
        self.assertTrue(resolver.matches_for_evidence(
            "user_2", "email", "old@example.test", observed_at, evidence_cutoff,
        ))

    def test_exact_historical_alias_link_resolves_model_uncertainty(self):
        request, resolver = fixture_context()
        at_alias_time = datetime.fromisoformat("2026-04-30T12:00:00+00:00")
        record = evidence(
            "evidence-alias", "account_service", "account-alias", "USER_PROFILE", "PRESENT", exposed="YES",
            user_id="user_2", observed_at=at_alias_time, available_at=at_alias_time,
        )
        record.fields.pop("user_id")
        record.fields["subject_reference"] = "OLD@EXAMPLE.TEST"
        record.raw_text = "subject_reference=OLD@EXAMPLE.TEST"
        result = audit_case(
            request, {"intent": "DELETE", "confidence": "HIGH"}, resolver, [record], [], rules(),
            UnresolvedRelevanceFixtureModel(), "Synthetic test prompt.",
        )
        self.assertEqual(result.deletion_status, "INCOMPLETE")
        self.assertIn("REPORT_REMAINING_RECORD", [step["operation"] for step in result.steps])

    def test_conflicting_stable_reference_is_not_joined_by_alias(self):
        request, resolver = fixture_context()
        at_alias_time = datetime.fromisoformat("2026-04-30T12:00:00+00:00")
        record = evidence(
            "evidence-conflict", "account_service", "account-conflict", "USER_PROFILE", "PRESENT",
            user_id="user_2", observed_at=at_alias_time, available_at=at_alias_time,
        )
        record.fields["email"] = "old@example.test"
        with self.assertRaisesRegex(AuditBlocked, "conflicting stable subject reference"):
            run_case(request, resolver, [record])

    def test_empty_stable_reference_placeholder_is_not_a_conflict(self):
        request, resolver = fixture_context()
        record = evidence(
            "evidence-null-reference", "account_service", "account-null-reference", "USER_PROFILE", "PRESENT",
            exposed="YES",
        )
        record.fields["customer_reference"] = "null"
        result = run_case(request, resolver, [record])
        self.assertEqual(result.deletion_status, "INCOMPLETE")
        self.assertIn("REPORT_REMAINING_RECORD", [step["operation"] for step in result.steps])

    def test_support_policy_second_pass_uses_explicit_message_context(self):
        request, resolver = fixture_context()
        message = evidence(
            "evidence-support-context", "support_platform", "support-context", "SUPPORT_MESSAGE", "PRESENT",
            exposed="YES", condition="UNRESOLVED",
        )
        message.fields["message_excerpt"] = "A customer asked the help desk to update an order address."
        model = SupportPolicyFixtureModel()
        result = audit_case(
            request, {"intent": "DELETE", "confidence": "HIGH"}, resolver, [message], [], rules(), model,
            "Synthetic evidence prompt.", policy_condition_prompt="Synthetic policy recheck prompt.",
        )
        self.assertEqual(result.deletion_status, "INCOMPLETE")
        self.assertEqual(model.policy_calls, 1)
        self.assertIn("REDACT_RECORD", [step["operation"] for step in result.steps])

    def test_support_policy_without_record_content_stays_unresolved(self):
        request, resolver = fixture_context()
        message = evidence(
            "evidence-support-no-content", "support_platform", "support-no-content", "SUPPORT_MESSAGE", "PRESENT",
            exposed="UNRESOLVED", condition="UNRESOLVED",
        )
        model = SupportPolicyFixtureModel()
        with self.assertRaisesRegex(AuditBlocked, "conditional policy is unresolved"):
            audit_case(
                request, {"intent": "DELETE", "confidence": "HIGH"}, resolver, [message], [], rules(), model,
                "Synthetic evidence prompt.", policy_condition_prompt="Synthetic policy recheck prompt.",
            )
        self.assertEqual(model.policy_calls, 0)

    def test_explicit_no_deletion_request_is_not_applicable(self):
        request, resolver = fixture_context()
        request["request_text"] = "Do not delete my account or my personal data."
        result = audit_case(
            request,
            {"intent": "NOT_DELETE", "confidence": "HIGH", "reason": "Explicitly forbids deletion."},
            resolver,
            [],
            [],
            rules(),
            StructuredFixtureModel(),
            "Synthetic test prompt.",
        )
        self.assertEqual(result.deletion_status, "NOT_APPLICABLE")
        self.assertEqual(result.steps, [])

    def test_historical_alias_replica_flow_and_primary_absence(self):
        request, resolver = fixture_context()
        primary = evidence("activity-primary", "profile_primary", "profile-1", "USER_PROFILE", "ABSENT", "readback", scope="primary", source_kind="activity")
        replica = evidence("evidence-replica", "profile_replica", "profile-1", "USER_PROFILE", "PRESENT", scope="replica-ap-south")
        connector = evidence("evidence-flow", "integration_service", "flow-9", "DATA_FLOW", "ACTIVE", "readback", source_kind="activity")
        link = Observation(
            evidence_id="activity-link", locator="activity:link", available_at=NOW, observed_at=NOW,
            system_id="profile_replica", resource_id="profile-1", scope_id="", category="",
            state="UNKNOWN", fields={"event_type": "LINK_RESOURCE_IDENTITY", "user_id": "user_1"},
            source_kind="activity", proof_kind="identity_link", raw_text="",
        )
        result = run_case(request, resolver, [replica], [primary, connector, link])
        self.assertEqual(result.deletion_status, "INCOMPLETE")
        operations = [step["operation"] for step in result.steps]
        self.assertIn("REPORT_REMAINING_RECORD", operations)
        self.assertIn("REPORT_ACTIVE_DATA_FLOW", operations)
        self.assertIn("DISABLE_DATA_FLOW", operations)
        self.assertLess(operations.index("DISABLE_DATA_FLOW"), operations.index("DELETE_RECORD"))
        self.assertTrue(all(step["evidence_id"] for step in result.steps if step["phase"] == "FINDING"))

    def test_compliant_tombstone_and_required_retained_record(self):
        request, resolver = fixture_context()
        tombstone = evidence("evidence-tombstone", "account_service", "tombstone-1", "ACCOUNT_TOMBSTONE", "REDACTED", "readback", condition="TRUE")
        security = evidence("evidence-security", "security_service", "audit-1", "SECURITY_AUDIT_LOG", "PRESENT", condition="TRUE")
        result = run_case(request, resolver, [tombstone, security])
        self.assertEqual(result.deletion_status, "COMPLETE")
        self.assertEqual({step["operation"] for step in result.steps}, {"VERIFY_RECORD_REDACTED", "VERIFY_RECORD_PRESENT"})
        self.assertTrue(all(step["phase"] == "VERIFICATION" and step["evidence_id"] for step in result.steps))

    def test_exposed_tombstone_identifiers_are_redacted(self):
        request, resolver = fixture_context()
        tombstone = evidence("evidence-exposed", "account_service", "tombstone-2", "ACCOUNT_TOMBSTONE", "PRESENT", "snapshot", exposed="YES", condition="TRUE")
        result = run_case(request, resolver, [tombstone])
        self.assertEqual(result.deletion_status, "INCOMPLETE")
        self.assertEqual([step["operation"] for step in result.steps], ["REPORT_EXPOSED_PII", "REDACT_RECORD", "VERIFY_RECORD_REDACTED"])

    def test_tombstone_with_only_permitted_stable_id_is_already_redacted(self):
        request, resolver = fixture_context()
        tombstone = evidence("evidence-tombstone", "identity_service", "tombstone-3", "ACCOUNT_TOMBSTONE", "PRESENT", exposed="YES", condition="TRUE")
        tombstone.fields.update({
            "subject_reference": "user_1", "account_status": "DELETED",
            "name": None, "email": None, "phone": None, "email_hash": None,
        })
        result = run_case(request, resolver, [tombstone])
        self.assertEqual(result.deletion_status, "COMPLETE")
        self.assertEqual([step["operation"] for step in result.steps], ["VERIFY_RECORD_REDACTED"])

    def test_structured_deleted_tombstone_resolves_policy_condition(self):
        request, resolver = fixture_context()
        tombstone = evidence(
            "evidence-tombstone", "identity_service", "tombstone-4", "ACCOUNT_TOMBSTONE", "PRESENT",
            exposed="YES", condition="UNRESOLVED",
        )
        tombstone.fields.update({
            "subject_reference": "user_1", "account_status": "DELETED",
            "name": None, "email": None, "phone": None, "email_hash": None,
        })
        result = run_case(request, resolver, [tombstone])
        self.assertEqual(result.deletion_status, "COMPLETE")
        self.assertEqual([step["operation"] for step in result.steps], ["VERIFY_RECORD_REDACTED"])

    def test_future_observation_is_excluded(self):
        request, resolver = fixture_context()
        future = evidence(
            "evidence-future", "account_service", "account-future", "USER_PROFILE", "PRESENT",
            observed_at=datetime.fromisoformat("2026-09-02T00:00:00+00:00"),
            available_at=datetime.fromisoformat("2026-09-02T00:00:00+00:00"),
        )
        with self.assertRaisesRegex(AuditBlocked, "no subject-linked evidence"):
            run_case(request, resolver, [future])

    def test_unscoped_claim_does_not_prove_absence(self):
        request, resolver = fixture_context()
        claim = evidence("activity-claim", "account_service", "account-claim", "USER_PROFILE", "ABSENT", "claim", source_kind="activity")
        with self.assertRaisesRegex(AuditBlocked, "only workflow claims"):
            run_case(request, resolver, [claim])

    def test_scoped_absence_readback_resolves_exposure_to_no(self):
        request, resolver = fixture_context()
        absent = evidence("evidence-absent", "account_service", "account-absent", "USER_PROFILE", "ABSENT", "readback", exposed="UNRESOLVED")
        result = run_case(request, resolver, [absent])
        self.assertEqual(result.deletion_status, "COMPLETE")
        self.assertEqual([step["operation"] for step in result.steps], ["VERIFY_RECORD_ABSENT"])

    def test_required_retained_record_does_not_need_delete_exposure_classification(self):
        request, resolver = fixture_context()
        retained = evidence(
            "evidence-retained", "security_service", "security-1", "SECURITY_AUDIT_LOG", "PRESENT",
            exposed="UNRESOLVED", condition="TRUE",
        )
        result = run_case(request, resolver, [retained])
        self.assertEqual(result.deletion_status, "COMPLETE")
        self.assertEqual([step["operation"] for step in result.steps], ["VERIFY_RECORD_PRESENT"])

    def test_explicit_data_flow_readback_cannot_be_downgraded_by_model(self):
        request, resolver = fixture_context()
        flow = evidence("evidence-flow", "integration_service", "flow-1", "DATA_FLOW", "ACTIVE", "readback")
        flow.fields["fixture_state"] = "PRESENT"
        result = run_case(request, resolver, [flow])
        self.assertEqual(result.deletion_status, "INCOMPLETE")
        self.assertEqual(
            [step["operation"] for step in result.steps],
            ["REPORT_ACTIVE_DATA_FLOW", "DISABLE_DATA_FLOW", "VERIFY_DATA_FLOW_DISABLED"],
        )

    def test_explicit_data_flow_enabled_flag_resolves_generic_present_row(self):
        request, resolver = fixture_context()
        flow = evidence("evidence-flow-config", "integration_service", "flow-config-1", "DATA_FLOW", "PRESENT")
        flow.fields["enabled"] = True
        result = run_case(request, resolver, [flow])
        self.assertEqual(result.deletion_status, "INCOMPLETE")
        self.assertEqual(
            [step["operation"] for step in result.steps],
            ["REPORT_ACTIVE_DATA_FLOW", "DISABLE_DATA_FLOW", "VERIFY_DATA_FLOW_DISABLED"],
        )

    def test_incomplete_snapshot_does_not_prove_absence(self):
        request, resolver = fixture_context()
        partial = evidence(
            "evidence-partial", "account_service", "account-partial", "USER_PROFILE", "ABSENT",
            "readback", source_kind="sql",
        )
        partial.scope_complete = False
        with self.assertRaisesRegex(AuditBlocked, "no scoped state proof"):
            run_case(request, resolver, [partial])

    def test_same_time_readback_takes_precedence_over_snapshot(self):
        request, resolver = fixture_context()
        snapshot = evidence("evidence-snapshot", "account_service", "account-1", "USER_PROFILE", "PRESENT", "snapshot")
        readback = evidence("evidence-readback", "account_service", "account-1", "USER_PROFILE", "ABSENT", "readback")
        result = run_case(request, resolver, [snapshot, readback])
        self.assertEqual(result.deletion_status, "COMPLETE")
        self.assertEqual([step["operation"] for step in result.steps], ["VERIFY_RECORD_ABSENT"])

    def test_restore_risk_is_blocked_and_verified(self):
        request, resolver = fixture_context()
        backup = evidence("evidence-backup", "backup_service", "backup-1", "BACKUP_ARCHIVE", "ACTIVE", "readback", condition="TRUE")
        backup.fields["can_block_restore"] = True
        result = run_case(request, resolver, [backup])
        self.assertEqual(result.deletion_status, "INCOMPLETE")
        self.assertEqual([step["operation"] for step in result.steps], ["REPORT_RESTORE_RISK", "BLOCK_RESTORE", "VERIFY_RESTORE_BLOCKED"])

    def test_explicit_backup_restore_flags_resolve_present_archive_snapshot(self):
        request, resolver = fixture_context()
        backup = evidence("evidence-backup-snapshot", "backup_service", "backup-snapshot-1", "BACKUP_ARCHIVE", "PRESENT")
        backup.fields["eligible"] = True
        backup.fields["deletion_block"] = False
        result = run_case(request, resolver, [backup])
        self.assertEqual(result.deletion_status, "INCOMPLETE")
        self.assertEqual(
            [step["operation"] for step in result.steps],
            ["REPORT_RESTORE_RISK", "BLOCK_RESTORE", "VERIFY_RESTORE_BLOCKED"],
        )

    def test_restore_allowed_does_not_prove_blocking_capability(self):
        request, resolver = fixture_context()
        backup = evidence("evidence-backup", "backup_service", "backup-2", "BACKUP_ARCHIVE", "ACTIVE", "readback", condition="TRUE")
        backup.fields["restore_allowed"] = True
        with self.assertRaisesRegex(AuditBlocked, "conditional policy is unresolved"):
            run_case(request, resolver, [backup])

    def test_explicit_deletion_block_control_supports_block_plan(self):
        request, resolver = fixture_context()
        backup = evidence("evidence-backup", "backup_service", "backup-3", "BACKUP_ARCHIVE", "ACTIVE", "readback", condition="FALSE")
        backup.fields["deletion_block"] = False
        result = run_case(request, resolver, [backup])
        self.assertEqual(result.deletion_status, "INCOMPLETE")
        self.assertIn("BLOCK_RESTORE", [step["operation"] for step in result.steps])

    def test_security_retention_date_is_compared_at_audit_cutoff(self):
        request, resolver = fixture_context()
        record = evidence("evidence-security", "security_service", "audit-2", "SECURITY_AUDIT_LOG", "PRESENT", condition="UNRESOLVED")
        record.fields["retention_until"] = "2033-12-31T23:59:59Z"
        result = run_case(request, resolver, [record])
        self.assertEqual(result.deletion_status, "COMPLETE")
        self.assertEqual([step["operation"] for step in result.steps], ["VERIFY_RECORD_PRESENT"])

    def test_structured_snapshot_state_cannot_be_downgraded_to_unknown(self):
        request, resolver = fixture_context()
        record = evidence("evidence-profile", "account_service", "account-2", "USER_PROFILE", "PRESENT")
        record.fields["fixture_state"] = "UNKNOWN"
        result = run_case(request, resolver, [record])
        self.assertEqual(result.deletion_status, "INCOMPLETE")
        self.assertEqual([step["operation"] for step in result.steps], ["REPORT_REMAINING_RECORD", "DELETE_RECORD", "VERIFY_RECORD_ABSENT"])

    def test_model_omission_fails_closed(self):
        request, resolver = fixture_context()
        record = evidence("evidence-profile", "account_service", "account-1", "USER_PROFILE", "PRESENT")
        with self.assertRaisesRegex(ValueError, "omitted or invented observation IDs"):
            run_case(request, resolver, [record], model=StructuredFixtureModel(corrupt=True))

    def test_policy_loader_covers_all_fifteen_supplied_categories(self):
        loaded = rules()
        self.assertEqual(len(loaded), 15)
        self.assertEqual({rule.action for rule in loaded.values()}, {"DELETE", "REDACT", "ANONYMIZE", "RETAIN"})
        for category, rule in loaded.items():
            condition = "NOT_APPLICABLE" if rule.condition == "Always" else "TRUE"
            state = "BLOCKED" if category == "BACKUP_ARCHIVE" else "PRESENT"
            self.assertEqual(required_treatment(rule, condition, state), rule.action, category)

    def test_incomplete_result_satisfies_structural_contract(self):
        request, resolver = fixture_context()
        record = evidence("evidence-profile", "account_service", "account-1", "USER_PROFILE", "PRESENT")
        result = run_case(request, resolver, [record])
        row = {"case_id": request["case_id"], "deletion_status": result.deletion_status, "steps_json": json.dumps(result.steps)}
        times = {"evidence-profile": instant("2026-08-20T12:00:00Z")}
        self.assertEqual(validate([row], [request], times), [])


if __name__ == "__main__":
    unittest.main()
