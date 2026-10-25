from __future__ import annotations

import csv
import os
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path


CODE_ROOT = Path(__file__).resolve().parents[1]
DATASET_ROOT = Path(os.environ.get("GHOST_DATASET_PATH", CODE_ROOT.parent / "dataset")).resolve()
sys.path.insert(0, str(CODE_ROOT))

from audit_agent.engine import ClassifiedFact, CurrentFact, plan_case
from audit_agent.policy import PolicyResolutionError, PolicyRule, load_policy, required_treatment
from audit_agent.policy_conditions import (
    resolve_policy_condition_from_fields,
    support_message_has_content,
    tombstone_has_only_stable_reference,
)
from audit_agent.types import Observation


AUDIT_AT = datetime.fromisoformat("2026-09-01T00:00:00+00:00")
OBSERVED_AT = datetime.fromisoformat("2026-08-20T12:00:00+00:00")


def supplied_rules() -> dict[str, PolicyRule]:
    with (DATASET_ROOT / "deletion_rules.csv").open(encoding="utf-8-sig", newline="") as stream:
        return load_policy(list(csv.DictReader(stream)))


def observation(
    evidence_id: str,
    category: str,
    state: str,
    fields: dict[str, object],
    *,
    system_id: str = "synthetic_service",
    resource_id: str = "synthetic-resource",
    source_kind: str = "json",
    raw_text: str = "",
) -> Observation:
    return Observation(
        evidence_id=evidence_id,
        locator="synthetic:1",
        available_at=OBSERVED_AT,
        observed_at=OBSERVED_AT,
        system_id=system_id,
        resource_id=resource_id,
        scope_id="primary",
        category=category,
        state=state,
        fields=fields,
        source_kind=source_kind,
        proof_kind="readback",
        scope_complete=True,
        raw_text=raw_text,
    )


def current_fact(
    evidence_id: str,
    category: str,
    state: str,
    condition: str,
    *,
    exposed: str = "NO",
    system_id: str = "synthetic_service",
    resource_id: str = "synthetic-resource",
) -> CurrentFact:
    source = observation(
        evidence_id, category, state, {}, system_id=system_id, resource_id=resource_id,
    )
    classification = {
        "category": category,
        "state": state,
        "relevant_to_subject": "YES",
        "identifiers_exposed": exposed,
        "policy_condition": condition,
    }
    classified = ClassifiedFact(source, classification, system_id, resource_id)
    return CurrentFact(classified, state, exposed, condition, evidence_id)


class Agent3PolicyConditionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rules = supplied_rules()

    def test_legal_hold_requires_explicit_active_hold_evidence(self):
        ordinary_retention_row = {
            "record_state": "PRESENT",
            "retention_until": "2033-12-31T23:59:59Z",
        }
        self.assertEqual(
            resolve_policy_condition_from_fields(
                "LEGAL_HOLD_RECORD", ordinary_retention_row, "PRESENT", AUDIT_AT,
            ),
            "UNRESOLVED",
        )
        self.assertEqual(
            resolve_policy_condition_from_fields(
                "LEGAL_HOLD_RECORD",
                {**ordinary_retention_row, "legal_hold_status": "ACTIVE"},
                "PRESENT",
                AUDIT_AT,
            ),
            "TRUE",
        )
        self.assertEqual(
            resolve_policy_condition_from_fields(
                "LEGAL_HOLD_RECORD", {"hold_status": "RELEASED"}, "PRESENT", AUDIT_AT,
            ),
            "FALSE",
        )
        self.assertEqual(
            resolve_policy_condition_from_fields(
                "LEGAL_HOLD_RECORD",
                {"hold_status": "ACTIVE", "legal_hold_active": False},
                "PRESENT",
                AUDIT_AT,
            ),
            "UNRESOLVED",
        )
        self.assertEqual(required_treatment(self.rules["LEGAL_HOLD_RECORD"], "TRUE", "PRESENT"), "RETAIN")
        self.assertEqual(required_treatment(self.rules["LEGAL_HOLD_RECORD"], "FALSE", "PRESENT"), "DELETE")

    def test_security_log_uses_supplied_deadline_at_audit_time(self):
        before_deadline = {"retention_until": "2026-09-30T23:59:59Z"}
        after_deadline = {"retention_until": "2026-08-31T23:59:59Z"}
        self.assertEqual(
            resolve_policy_condition_from_fields(
                "SECURITY_AUDIT_LOG", before_deadline, "PRESENT", AUDIT_AT,
            ),
            "TRUE",
        )
        self.assertEqual(
            resolve_policy_condition_from_fields(
                "SECURITY_AUDIT_LOG", after_deadline, "PRESENT", AUDIT_AT,
            ),
            "FALSE",
        )
        # A legal-retention date is not the supplied security-log deadline.
        for generic_date_field in ("retained_until", "legal_retention_until"):
            with self.subTest(generic_date_field=generic_date_field):
                result = resolve_policy_condition_from_fields(
                    "SECURITY_AUDIT_LOG",
                    {generic_date_field: "2033-12-31T23:59:59Z"},
                    "PRESENT",
                    AUDIT_AT,
                )
                self.assertEqual(result, "UNRESOLVED")
        self.assertEqual(required_treatment(self.rules["SECURITY_AUDIT_LOG"], "TRUE", "PRESENT"), "RETAIN")
        self.assertEqual(required_treatment(self.rules["SECURITY_AUDIT_LOG"], "FALSE", "PRESENT"), "DELETE")

    def test_support_message_policy_requires_message_or_context_content(self):
        self.assertTrue(support_message_has_content({"message_excerpt": "A shopper asked support to update an order."}))
        self.assertTrue(support_message_has_content(
            {}, raw_text="A shopper asked support to update an order.", source_kind="text",
        ))
        self.assertFalse(support_message_has_content({"requester_email": "person@example.test"}))
        self.assertEqual(
            resolve_policy_condition_from_fields(
                "SUPPORT_MESSAGE", {"requester_email": "person@example.test"}, "PRESENT", AUDIT_AT,
            ),
            "UNRESOLVED",
        )
        self.assertIsNone(resolve_policy_condition_from_fields(
            "SUPPORT_MESSAGE", {"message_excerpt": "A shopper asked support to update an order."},
            "PRESENT", AUDIT_AT,
        ))
        self.assertEqual(required_treatment(self.rules["SUPPORT_MESSAGE"], "TRUE", "PRESENT"), "REDACT")
        self.assertEqual(required_treatment(self.rules["SUPPORT_MESSAGE"], "FALSE", "PRESENT"), "DELETE")

    def test_backup_retention_requires_proven_restore_block_capability(self):
        self.assertEqual(resolve_policy_condition_from_fields(
            "BACKUP_ARCHIVE", {"can_block_restore": True}, "ACTIVE", AUDIT_AT,
        ), "TRUE")
        self.assertEqual(resolve_policy_condition_from_fields(
            "BACKUP_ARCHIVE", {"deletion_block": False}, "ACTIVE", AUDIT_AT,
        ), "TRUE")
        self.assertEqual(resolve_policy_condition_from_fields(
            "BACKUP_ARCHIVE", {"restore_allowed": True}, "ACTIVE", AUDIT_AT,
        ), "UNRESOLVED")
        self.assertEqual(resolve_policy_condition_from_fields(
            "BACKUP_ARCHIVE", {"can_block_restore": False}, "ACTIVE", AUDIT_AT,
        ), "FALSE")
        self.assertEqual(required_treatment(self.rules["BACKUP_ARCHIVE"], "TRUE", "ACTIVE"), "RETAIN")
        self.assertEqual(required_treatment(self.rules["BACKUP_ARCHIVE"], "FALSE", "ABSENT"), "COMPLIANT")
        self.assertEqual(required_treatment(self.rules["BACKUP_ARCHIVE"], "FALSE", "BLOCKED"), "COMPLIANT")
        with self.assertRaises(PolicyResolutionError):
            required_treatment(self.rules["BACKUP_ARCHIVE"], "FALSE", "ACTIVE")
        with self.assertRaises(PolicyResolutionError):
            required_treatment(self.rules["BACKUP_ARCHIVE"], "UNRESOLVED", "ACTIVE")

    def test_tombstone_shape_requires_deleted_state_stable_id_and_redacted_fields(self):
        valid = {
            "account_status": "DELETED",
            "subject_reference": "user_1",
            "name": None,
            "email": None,
            "phone": None,
            "email_hash": None,
        }
        self.assertEqual(resolve_policy_condition_from_fields(
            "ACCOUNT_TOMBSTONE", valid, "PRESENT", AUDIT_AT, stable_user_id="user_1",
        ), "TRUE")
        self.assertTrue(tombstone_has_only_stable_reference(valid, "user_1"))
        self.assertFalse(tombstone_has_only_stable_reference(valid, "user_2"))
        self.assertFalse(tombstone_has_only_stable_reference(
            {key: value for key, value in valid.items() if key != "subject_reference"}, "user_1",
        ))
        self.assertFalse(tombstone_has_only_stable_reference(
            {**valid, "email": "still-linked@example.test"}, "user_1",
        ))
        self.assertEqual(required_treatment(self.rules["ACCOUNT_TOMBSTONE"], "TRUE", "PRESENT"), "REDACT")

    def test_conditional_uncertainty_and_false_conditions_fail_closed_as_specified(self):
        for category in (
            "SUPPORT_MESSAGE", "SUPPORT_ATTACHMENT", "ANALYTICS_PROFILE",
            "PRODUCT_TELEMETRY", "EMAIL_DELIVERY_LOG", "SECURITY_AUDIT_LOG",
            "LEGAL_HOLD_RECORD", "BACKUP_ARCHIVE", "ACCOUNT_TOMBSTONE",
        ):
            for condition in ("UNRESOLVED", "NOT_APPLICABLE"):
                with self.subTest(category=category, condition=condition):
                    with self.assertRaises(PolicyResolutionError):
                        required_treatment(self.rules[category], condition, "PRESENT")

        expected_false_treatments = {
            "ANALYTICS_PROFILE": "COMPLIANT",
            "PRODUCT_TELEMETRY": "COMPLIANT",
            "EMAIL_DELIVERY_LOG": "COMPLIANT",
            "SUPPORT_MESSAGE": "DELETE",
            "SECURITY_AUDIT_LOG": "DELETE",
            "LEGAL_HOLD_RECORD": "DELETE",
            "ACCOUNT_TOMBSTONE": "DELETE",
        }
        for category, expected in expected_false_treatments.items():
            with self.subTest(category=category):
                self.assertEqual(required_treatment(self.rules[category], "FALSE", "PRESENT"), expected)
        with self.assertRaises(PolicyResolutionError):
            required_treatment(self.rules["SUPPORT_ATTACHMENT"], "FALSE", "PRESENT")
        with self.assertRaises(PolicyResolutionError):
            required_treatment(self.rules["LEGAL_HOLD_RECORD"], "MAYBE", "PRESENT")

    def test_plan_orders_flow_and_restore_controls_before_record_changes(self):
        current = [
            current_fact("ev-flow", "DATA_FLOW", "ACTIVE", "NOT_APPLICABLE", resource_id="flow-1"),
            current_fact("ev-backup", "BACKUP_ARCHIVE", "ACTIVE", "TRUE", resource_id="backup-1"),
            current_fact("ev-profile", "USER_PROFILE", "PRESENT", "NOT_APPLICABLE", resource_id="profile-1"),
            current_fact("ev-hold", "LEGAL_HOLD_RECORD", "PRESENT", "TRUE", resource_id="hold-1"),
        ]
        result = plan_case("synthetic-order", current, self.rules)
        self.assertEqual(result.deletion_status, "INCOMPLETE")
        operations = [step["operation"] for step in result.steps]
        self.assertLess(operations.index("DISABLE_DATA_FLOW"), operations.index("BLOCK_RESTORE"))
        self.assertLess(operations.index("BLOCK_RESTORE"), operations.index("DELETE_RECORD"))
        self.assertEqual(
            [step["phase"] for step in result.steps],
            sorted([step["phase"] for step in result.steps], key={"FINDING": 0, "REMEDIATION": 1, "VERIFICATION": 2}.get),
        )
        remediation_start = next(i for i, step in enumerate(result.steps) if step["phase"] == "REMEDIATION")
        verification_start = next(i for i, step in enumerate(result.steps) if step["phase"] == "VERIFICATION")
        self.assertTrue(all(step["phase"] == "REMEDIATION" for step in result.steps[remediation_start:verification_start]))
        self.assertTrue(all(step["phase"] == "VERIFICATION" for step in result.steps[verification_start:]))
        self.assertNotIn("DELETE_RECORD", [step["operation"] for step in result.steps if step["resource_id"] == "hold-1"])
        retained = [step for step in result.steps if step["resource_id"] == "hold-1"]
        self.assertEqual([step["operation"] for step in retained], ["VERIFY_RECORD_PRESENT"])
        self.assertTrue(all(not step["evidence_id"] for step in result.steps if step["phase"] in {"REMEDIATION", "VERIFICATION"}))


if __name__ == "__main__":
    unittest.main()
