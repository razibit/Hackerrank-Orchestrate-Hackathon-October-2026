import unittest

from audit_agent.data import maybe_instant, parse_instant
from audit_agent.identity import IdentityResolver


def instant(value: str):
    return parse_instant(value)


class IdentityTemporalTests(unittest.TestCase):
    def test_offset_timestamps_compare_as_the_same_instant(self):
        self.assertEqual(
            instant("2026-03-09T12:00:00+05:30"),
            instant("2026-03-09T06:30:00Z"),
        )

        resolver = IdentityResolver(
            [{"user_id": "u1", "email": "new@example.test", "updated_at": "2025-01-01T01:00:00+02:00"}],
            [{
                "audit_id": "a1", "user_id": "u1", "event_time": "2025-01-01T01:00:00+02:00",
                "field_name": "email", "old_value": "old@example.test", "new_value": "new@example.test",
            }],
        )
        before = instant("2024-12-31T22:30:00Z")
        at_change = instant("2024-12-31T23:00:00Z")
        cutoff = instant("2025-01-02T00:00:00Z")

        self.assertTrue(resolver.matches_as_of("u1", "email", "old@example.test", before, cutoff))
        self.assertFalse(resolver.matches_as_of("u1", "email", "old@example.test", at_change, cutoff))
        self.assertTrue(resolver.matches_as_of("u1", "email", "new@example.test", at_change, cutoff))
        with self.assertRaises(ValueError):
            parse_instant("2026-03-09T06:30:00")

    def test_request_alias_can_be_historical_at_audit_time(self):
        resolver = IdentityResolver(
            [{"user_id": "u1", "email": "new@example.test", "updated_at": "2025-01-02T00:00:00Z"}],
            [{
                "audit_id": "a1", "user_id": "u1", "event_time": "2025-01-02T00:00:00Z",
                "field_name": "email", "old_value": "old@example.test", "new_value": "new@example.test",
            }],
        )
        identity = resolver.resolve(
            "OLD@example.test", instant("2025-01-01T00:00:00Z"), instant("2025-01-03T00:00:00Z"),
        )

        self.assertIsNotNone(identity)
        self.assertEqual(identity.user_id, "u1")
        self.assertIn("old@example.test", identity.aliases["email"])
        self.assertTrue(resolver.matches_as_of(
            "u1", "email", "old@example.test", instant("2025-01-01T12:00:00Z"),
            instant("2025-01-03T00:00:00Z"),
        ))
        self.assertFalse(resolver.matches_as_of(
            "u1", "email", "old@example.test", instant("2025-01-02T00:00:00Z"),
            instant("2025-01-03T00:00:00Z"),
        ))
        self.assertTrue(resolver.matches_for_evidence(
            "u1", "email", "old@example.test", instant("2025-01-03T00:00:00Z"),
            instant("2025-01-03T00:00:00Z"),
        ))

    def test_reassignment_does_not_make_a_prior_owner_interval_unbounded(self):
        resolver = IdentityResolver(
            [
                {"user_id": "u1", "email": "u1-current@example.test", "updated_at": "2025-01-02T00:00:00Z"},
                {"user_id": "u2", "email": "u2-current@example.test", "updated_at": "2025-01-04T00:00:00Z"},
            ],
            [
                {
                    "audit_id": "u1-change", "user_id": "u1", "event_time": "2025-01-02T00:00:00Z",
                    "field_name": "email", "old_value": "shared@example.test",
                    "new_value": "u1-current@example.test",
                },
                {
                    "audit_id": "u2-assign", "user_id": "u2", "event_time": "2025-01-03T00:00:00Z",
                    "field_name": "email", "old_value": "u2-old@example.test",
                    "new_value": "shared@example.test",
                },
                {
                    "audit_id": "u2-change", "user_id": "u2", "event_time": "2025-01-04T00:00:00Z",
                    "field_name": "email", "old_value": "shared@example.test",
                    "new_value": "u2-current@example.test",
                },
            ],
        )
        cutoff = instant("2025-01-05T00:00:00Z")
        request_time = instant("2025-01-01T12:00:00Z")

        identity = resolver.resolve("shared@example.test", request_time, cutoff)
        self.assertIsNotNone(identity)
        self.assertEqual(identity.user_id, "u1")
        self.assertTrue(resolver.matches_for_evidence(
            "u1", "email", "shared@example.test", request_time, cutoff,
        ))
        self.assertFalse(resolver.matches_for_evidence(
            "u2", "email", "shared@example.test", request_time, cutoff,
        ))
        self.assertTrue(resolver.matches_for_evidence(
            "u2", "email", "shared@example.test", instant("2025-01-03T12:00:00Z"), cutoff,
        ))
        self.assertFalse(resolver.matches_for_evidence(
            "u1", "email", "shared@example.test", instant("2025-01-03T12:00:00Z"), cutoff,
        ))

    def test_overlapping_current_aliases_remain_ambiguous(self):
        resolver = IdentityResolver(
            [
                {"user_id": "u1", "email": "shared@example.test", "updated_at": "2025-01-01T00:00:00Z"},
                {"user_id": "u2", "email": "shared@example.test", "updated_at": "2025-01-01T00:00:00Z"},
            ],
            [],
        )
        self.assertIsNone(resolver.resolve(
            "shared@example.test", instant("2025-01-02T00:00:00Z"), instant("2025-01-03T00:00:00Z"),
        ))

    def test_missing_or_invalid_event_time_does_not_create_an_alias(self):
        for event_time in ("", "not-a-timestamp"):
            with self.subTest(event_time=event_time):
                resolver = IdentityResolver(
                    [],
                    [{
                        "audit_id": "bad", "user_id": "u1", "event_time": event_time,
                        "field_name": "email", "old_value": "old@example.test",
                        "new_value": "new@example.test",
                    }],
                )
                self.assertIsNone(resolver.resolve(
                    "old@example.test", instant("2025-01-02T00:00:00Z"), instant("2025-01-03T00:00:00Z"),
                ))

    def test_future_requests_and_observations_are_excluded_by_the_cutoff(self):
        resolver = IdentityResolver(
            [{"user_id": "u1", "email": "stable@example.test", "updated_at": "2025-01-01T00:00:00Z"}],
            [{
                "audit_id": "future-change", "user_id": "u1", "event_time": "2025-01-03T00:00:00Z",
                "field_name": "email", "old_value": "stable@example.test",
                "new_value": "future@example.test",
            }],
        )
        cutoff = instant("2025-01-02T00:00:00Z")
        future = instant("2025-01-04T00:00:00Z")

        self.assertIsNone(resolver.resolve(
            "future@example.test", instant("2025-01-01T12:00:00Z"), cutoff,
        ))
        self.assertIsNone(resolver.resolve("future@example.test", future, cutoff))
        self.assertIsNone(resolver.resolve("stable@example.test", future, cutoff))
        self.assertFalse(resolver.matches_as_of("u1", "email", "stable@example.test", future, cutoff))
        self.assertFalse(resolver.matches_for_evidence(
            "u1", "email", "stable@example.test", future, cutoff,
        ))

    def test_duplicate_names_do_not_join_distinct_emails(self):
        resolver = IdentityResolver(
            [
                {"user_id": "u1", "name": "Alex Smith", "email": "one@example.test", "updated_at": "2025-01-01T00:00:00Z"},
                {"user_id": "u2", "name": "Alex Smith", "email": "two@example.test", "updated_at": "2025-01-01T00:00:00Z"},
            ],
            [],
        )
        requested_at = instant("2025-01-02T00:00:00Z")
        audit_at = instant("2025-01-03T00:00:00Z")

        self.assertEqual(resolver.resolve("one@example.test", requested_at, audit_at).user_id, "u1")
        self.assertEqual(resolver.resolve("two@example.test", requested_at, audit_at).user_id, "u2")
        self.assertIsNone(resolver.resolve("Alex Smith", requested_at, audit_at))

    def test_invalid_optional_timestamp_returns_none(self):
        self.assertIsNone(maybe_instant("unknown"))


if __name__ == "__main__":
    unittest.main()
