import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from audit_agent.engine import _explicit_policy_condition
from audit_agent.policy import PolicyResolutionError, PolicyRule, required_treatment
from audit_agent.types import Observation


class Agent5LegalHoldRegressionTests(unittest.TestCase):
    def test_present_register_row_and_future_date_do_not_prove_active_hold(self):
        cutoff = datetime(2026, 10, 1, tzinfo=timezone.utc)
        observation = Observation(
            evidence_id="synthetic_evidence",
            locator="synthetic row",
            available_at=cutoff,
            observed_at=cutoff,
            system_id="legal_retention_register",
            resource_id="synthetic_record",
            scope_id="primary",
            category="LEGAL_HOLD_RECORD",
            state="PRESENT",
            fields={
                "record_state": "PRESENT",
                "retention_until": "2027-01-01",
            },
            source_kind="sql",
            proof_kind="snapshot",
        )
        rule = PolicyRule(
            category="LEGAL_HOLD_RECORD",
            condition="A supplied legal hold is active",
            action="RETAIN",
        )

        # The deterministic resolver must not turn ordinary row presence and
        # a future retention date into TRUE for the distinct active-hold rule.
        condition = _explicit_policy_condition(
            observation, "LEGAL_HOLD_RECORD", cutoff
        )
        self.assertIsNone(condition)
        with self.assertRaises(PolicyResolutionError):
            required_treatment(rule, condition or "UNRESOLVED", observation.state)

        # A grounded active condition is the only path in this fixture to RETAIN.
        self.assertEqual(required_treatment(rule, "TRUE", observation.state), "RETAIN")


if __name__ == "__main__":
    unittest.main()
