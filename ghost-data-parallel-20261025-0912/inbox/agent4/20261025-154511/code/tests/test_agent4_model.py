from __future__ import annotations

import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

from audit_agent.cache import CachedChatModel, JsonResponseCache
from audit_agent.model import (
    INTENT_SCHEMA,
    OBSERVATION_SCHEMA,
    FoundryChatModel,
    ModelCallError,
    OutputTruncatedError,
    POLICY_CONDITION_SCHEMA,
    ResponseIdentityError,
    StructuredResponseError,
    UsageLedger,
    _validate_json_schema,
    classify_intents,
    classify_observations,
    classify_policy_conditions,
)


def _observation(observation_id: str) -> dict[str, object]:
    return {
        "observation_id": observation_id,
        "evidence_id": "evidence_synthetic_01",
        "locator": "records[0]",
        "observed_at": "2026-10-01T00:00:00Z",
        "system_id": "profile_service",
        "resource_id": f"profile_{observation_id}",
        "scope_id": "primary",
        "category_hint": "USER_PROFILE",
        "state_hint": "PRESENT",
        "proof_kind": "snapshot",
        "scope_complete": True,
        "fields": {"user_id": "user_synthetic_01"},
        "excerpt": "Synthetic profile row.",
    }


def _classified(item: dict[str, object]) -> dict[str, str]:
    return {
        "observation_id": str(item["observation_id"]),
        "system_id": str(item.get("system_id", "profile_service")),
        "resource_id": str(item.get("resource_id", "profile_synthetic")),
        "relevant_to_subject": "YES",
        "category": "USER_PROFILE",
        "state": "PRESENT",
        "identifiers_exposed": "YES",
        "policy_condition": "NOT_APPLICABLE",
        "scope_complete": "TRUE",
        "reason": "Synthetic source row; evidence_synthetic_01.",
    }


class _Model:
    def __init__(self, responder):
        self.responder = responder
        self.calls: list[tuple[str, dict[str, object]]] = []

    def chat_json(self, purpose, system_prompt, payload, schema, max_tokens=3000):
        self.calls.append((purpose, payload))
        return self.responder(purpose, payload, schema)


class BatchIdentityValidationTests(unittest.TestCase):
    def test_observation_response_order_is_irrelevant_and_ids_are_preserved(self):
        records = [_observation("obs-1"), _observation("obs-2")]

        def respond(_purpose, payload, _schema):
            return {"observations": [_classified(item) for item in reversed(payload["observations"])]}

        result = classify_observations(_Model(respond), "case-synthetic", "user-synthetic", "2026-10-01T00:00:00Z", records, "prompt v3")
        self.assertEqual(set(result), {"obs-1", "obs-2"})
        self.assertEqual(result["obs-1"]["resource_id"], "profile_obs-1")

    def test_duplicate_missing_and_mismatched_ids_are_split_and_retried_by_batch(self):
        records = [_observation("obs-1"), _observation("obs-2")]

        for mode in ("duplicate", "missing", "mismatched"):
            with self.subTest(mode=mode):
                def respond(_purpose, payload, _schema, current_mode=mode):
                    items = payload["observations"]
                    valid = [_classified(item) for item in items]
                    if len(items) == 1:
                        return {"observations": valid}
                    if current_mode == "duplicate":
                        return {"observations": [valid[0], valid[0]]}
                    if current_mode == "missing":
                        return {"observations": valid[:1]}
                    invalid = dict(valid[1], observation_id="obs-not-supplied")
                    return {"observations": [valid[0], invalid]}

                model = _Model(respond)
                result = classify_observations(model, "case-synthetic", "user-synthetic", "2026-10-01T00:00:00Z", records, "prompt v3")
                self.assertEqual(set(result), {"obs-1", "obs-2"})
                self.assertEqual(len(model.calls), 3)

    def test_single_observation_with_fabricated_observation_id_fails_closed(self):
        record = _observation("obs-1")
        model = _Model(lambda _purpose, _payload, _schema: {
            "observations": [dict(_classified(record), observation_id="obs-invented")],
        })
        with self.assertRaises(ResponseIdentityError):
            classify_observations(model, "case-synthetic", "user-synthetic", "2026-10-01T00:00:00Z", [record], "prompt v3")

    def test_duplicate_input_ids_are_rejected_before_a_call(self):
        records = [_observation("obs-1"), _observation("obs-1")]
        model = _Model(lambda *_args: {"observations": []})
        with self.assertRaisesRegex(ValueError, "duplicate observation_id"):
            classify_observations(model, "case-synthetic", "user-synthetic", "2026-10-01T00:00:00Z", records, "prompt v3")
        self.assertEqual(model.calls, [])

    def test_intent_id_mismatch_splits_batch_and_invalid_not_applicable_is_rejected(self):
        requests = [
            {"case_id": "case-a", "request_text": "Please delete my account."},
            {"case_id": "case-b", "request_text": "I do not want deletion."},
        ]

        def respond(_purpose, payload, _schema):
            cases = payload["requests"]
            def item(request):
                intent = "DELETE" if request["case_id"] == "case-a" else "NOT_DELETE"
                return {"case_id": request["case_id"], "intent": intent, "confidence": "HIGH", "reason": "Synthetic request."}
            if len(cases) > 1:
                return {"cases": [item(cases[0]), dict(item(cases[1]), case_id="case-unknown")]}
            return {"cases": [item(cases[0])]}

        model = _Model(respond)
        result = classify_intents(model, requests, "prompt revision 2")
        self.assertEqual(result["case-a"]["intent"], "DELETE")
        self.assertEqual(result["case-b"]["intent"], "NOT_DELETE")
        self.assertEqual(len(model.calls), 3)

        invalid = _Model(lambda _purpose, payload, _schema: {
            "cases": [{"case_id": payload["requests"][0]["case_id"], "intent": "NOT_APPLICABLE", "confidence": "HIGH", "reason": "Synthetic."}],
        })
        with self.assertRaises(StructuredResponseError):
            classify_intents(invalid, requests[:1], "prompt revision 2")

    def test_policy_condition_ids_are_correlated_without_string_coercion(self):
        records = [
            {"observation_id": "obs-1", "fields": {"message_body": "A shopper asked support about an order."}},
            {"observation_id": "obs-2", "fields": {"message_body": "Internal note."}},
        ]

        def respond(_purpose, payload, _schema):
            items = payload["observations"]
            if len(items) > 1:
                first = items[0]["observation_id"]
                return {"policy_conditions": [
                    {"observation_id": first, "condition": "TRUE", "reason": "Synthetic message content."},
                    {"observation_id": "obs-not-supplied", "condition": "FALSE", "reason": "Synthetic message content."},
                ]}
            return {"policy_conditions": [
                {"observation_id": items[0]["observation_id"], "condition": "TRUE", "reason": "Synthetic message content."},
            ]}

        model = _Model(respond)
        result = classify_policy_conditions(model, "case-synthetic", "2026-10-01T00:00:00Z", records, "policy prompt v2")
        self.assertEqual(set(result), {"obs-1", "obs-2"})
        self.assertEqual(len(model.calls), 3)

    def test_invalid_observation_enum_is_rejected_without_coercion(self):
        record = _observation("obs-1")
        response = _classified(record)
        response["state"] = "COMPLETE"
        model = _Model(lambda *_args: {"observations": [response]})
        with self.assertRaises(StructuredResponseError):
            classify_observations(model, "case-synthetic", "user-synthetic", "2026-10-01T00:00:00Z", [record], "prompt v3")

    def test_present_retention_row_and_future_date_cannot_be_promoted_to_active_legal_hold(self):
        record = _observation("obs-retention-1")
        record.update({
            "evidence_id": "evidence_synthetic_retention",
            "category_hint": "UNRESOLVED",
            "state_hint": "PRESENT",
            "fields": {
                "record_state": "PRESENT",
                "order_id": "order_synthetic_01",
                "retention_until": "2026-12-31",
            },
            "excerpt": "Retention register row; record_state=PRESENT; retention_until=2026-12-31.",
        })
        false_positive = _classified(record)
        false_positive.update({"category": "LEGAL_HOLD_RECORD", "policy_condition": "TRUE"})
        hinted_record = _observation("obs-retention-2")
        hinted_record.update({
            "category_hint": "LEGAL_HOLD_RECORD",
            "state_hint": "PRESENT",
            "fields": {"record_state": "PRESENT", "retention_until": "2026-12-31"},
            "excerpt": "Retention register row; record_state=PRESENT; retention_until=2026-12-31.",
        })
        hinted_false_positive = _classified(hinted_record)
        hinted_false_positive.update({"category": "LEGAL_HOLD_RECORD", "policy_condition": "TRUE"})
        model = _Model(lambda *_args: {"observations": [false_positive, hinted_false_positive]})

        result = classify_observations(model, "case-synthetic", "user-synthetic", "2026-10-25T00:00:00Z", [record, hinted_record], "prompt v4")
        for observation_id in ("obs-retention-1", "obs-retention-2"):
            with self.subTest(observation_id=observation_id):
                self.assertEqual(result[observation_id]["state"], "PRESENT")
                self.assertEqual(result[observation_id]["category"], "UNRESOLVED")
                self.assertEqual(result[observation_id]["policy_condition"], "UNRESOLVED")
                self.assertIn("does not establish a legal hold", result[observation_id]["reason"])

    def test_legal_hold_condition_requires_explicit_active_or_inactive_evidence(self):
        active = _observation("obs-hold-active")
        active.update({"category_hint": "UNRESOLVED", "fields": {"hold_status": "ACTIVE"}, "excerpt": "Legal hold status: active."})
        active_answer = _classified(active)
        active_answer.update({"category": "LEGAL_HOLD_RECORD", "policy_condition": "UNRESOLVED"})

        released = _observation("obs-hold-released")
        released.update({"category_hint": "UNRESOLVED", "fields": {"hold_status": "RELEASED"}, "excerpt": "Legal hold is released."})
        released_answer = _classified(released)
        released_answer.update({"category": "LEGAL_HOLD_RECORD", "policy_condition": "TRUE"})

        conflict = _observation("obs-hold-conflict")
        conflict.update({"category_hint": "UNRESOLVED", "fields": {"hold_status": "ACTIVE"}, "excerpt": "The legal hold is released."})
        conflict_answer = _classified(conflict)
        conflict_answer.update({"category": "LEGAL_HOLD_RECORD", "policy_condition": "TRUE"})

        model = _Model(lambda _purpose, payload, _schema: {
            "observations": [
                active_answer if item["observation_id"] == "obs-hold-active" else
                released_answer if item["observation_id"] == "obs-hold-released" else
                conflict_answer
                for item in payload["observations"]
            ],
        })
        result = classify_observations(
            model,
            "case-synthetic",
            "user-synthetic",
            "2026-10-25T00:00:00Z",
            [active, released, conflict],
            "prompt v3",
        )
        self.assertEqual(result["obs-hold-active"]["category"], "LEGAL_HOLD_RECORD")
        self.assertEqual(result["obs-hold-active"]["policy_condition"], "TRUE")
        self.assertEqual(result["obs-hold-released"]["policy_condition"], "FALSE")
        self.assertEqual(result["obs-hold-conflict"]["policy_condition"], "UNRESOLVED")

    def test_non_string_source_ids_are_rejected_instead_of_coerced(self):
        record = _observation("obs-1")
        response = _classified(record)
        response["system_id"] = 17
        model = _Model(lambda *_args: {"observations": [response]})
        with self.assertRaises(StructuredResponseError):
            classify_observations(model, "case-synthetic", "user-synthetic", "2026-10-01T00:00:00Z", [record], "prompt v3")

    def test_strict_schema_rejects_missing_required_fields_and_closed_extra_fields(self):
        with self.assertRaisesRegex(StructuredResponseError, "missing required"):
            _validate_json_schema({"cases": [{"case_id": "case-a"}]}, INTENT_SCHEMA)
        with self.assertRaisesRegex(StructuredResponseError, "unexpected field"):
            _validate_json_schema({"observations": [], "deletion_status": "COMPLETE"}, OBSERVATION_SCHEMA)


class MockedStructuredCallTests(unittest.TestCase):
    @staticmethod
    def _response(content: str, finish_reason: str = "stop"):
        return types.SimpleNamespace(
            choices=[types.SimpleNamespace(
                message=types.SimpleNamespace(content=content),
                finish_reason=finish_reason,
            )],
            usage=types.SimpleNamespace(prompt_tokens=11, completion_tokens=3, total_tokens=14),
            model="synthetic-model-id",
        )

    def test_malformed_and_schema_invalid_json_retry_with_accurate_usage(self):
        responses = [
            self._response("not-json"),
            self._response('{"value": 3}'),
            self._response('{"value": "ok"}'),
        ]
        requests = []

        class FakeOpenAI:
            def __init__(self, **_kwargs):
                self.chat = types.SimpleNamespace(completions=types.SimpleNamespace(create=self.create))

            def create(self, **kwargs):
                requests.append(kwargs)
                return responses.pop(0)

        schema = {
            "type": "object",
            "properties": {"value": {"type": "string"}},
            "required": ["value"],
            "additionalProperties": False,
        }
        ledger = UsageLedger.create()
        env = {
            "AZURE_FOUNDRY_ENDPOINT": "https://foundry.synthetic.invalid",
            "AZURE_FOUNDRY_DEPLOYMENT": "synthetic-deployment",
            "AZURE_FOUNDRY_ALLOW_UNCAPPED_GPU_HOURS": "1",
        }
        with patch.dict(os.environ, env, clear=True), patch.dict(sys.modules, {"openai": types.SimpleNamespace(OpenAI=FakeOpenAI)}), patch("audit_agent.model.time.sleep"):
            model = FoundryChatModel(ledger, max_calls=10)
            model.token_provider = lambda: "synthetic-token"
            result = model.chat_json("synthetic", "Synthetic prompt", {}, schema, max_tokens=20)

        self.assertEqual(result, {"value": "ok"})
        self.assertEqual(len(requests), 3)
        self.assertTrue(all(call["response_format"]["json_schema"]["strict"] for call in requests))
        totals = ledger.totals()
        self.assertEqual(totals["api_calls"], 3)
        self.assertEqual(totals["successful_calls"], 1)
        self.assertEqual(totals["failed_calls"], 2)
        self.assertEqual(totals["retries"], 2)
        self.assertEqual(totals["input_tokens"], 33)
        self.assertEqual(totals["output_tokens"], 9)
        self.assertEqual(totals["total_tokens"], 42)

    def test_persistent_malformed_json_fails_after_three_attempts(self):
        responses = [self._response("bad json") for _ in range(3)]

        class FakeOpenAI:
            def __init__(self, **_kwargs):
                self.chat = types.SimpleNamespace(completions=types.SimpleNamespace(create=self.create))

            def create(self, **_kwargs):
                return responses.pop(0)

        ledger = UsageLedger.create()
        env = {
            "AZURE_FOUNDRY_ENDPOINT": "https://foundry.synthetic.invalid",
            "AZURE_FOUNDRY_DEPLOYMENT": "synthetic-deployment",
            "AZURE_FOUNDRY_ALLOW_UNCAPPED_GPU_HOURS": "1",
        }
        schema = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}
        with patch.dict(os.environ, env, clear=True), patch.dict(sys.modules, {"openai": types.SimpleNamespace(OpenAI=FakeOpenAI)}), patch("audit_agent.model.time.sleep"):
            model = FoundryChatModel(ledger, max_calls=10)
            model.token_provider = lambda: "synthetic-token"
            with self.assertRaisesRegex(ModelCallError, "bounded retries"):
                model.chat_json("synthetic", "Synthetic prompt", {}, schema)
        totals = ledger.totals()
        self.assertEqual(totals["api_calls"], 3)
        self.assertEqual(totals["failed_calls"], 3)
        self.assertEqual(totals["retries"], 2)

    def test_provider_length_stop_is_recorded_once_and_not_retried_at_client_layer(self):
        response = self._response('{"value":', finish_reason="length")
        calls = []

        class FakeOpenAI:
            def __init__(self, **_kwargs):
                self.chat = types.SimpleNamespace(completions=types.SimpleNamespace(create=self.create))

            def create(self, **kwargs):
                calls.append(kwargs)
                return response

        ledger = UsageLedger.create()
        env = {
            "AZURE_FOUNDRY_ENDPOINT": "https://foundry.synthetic.invalid",
            "AZURE_FOUNDRY_DEPLOYMENT": "synthetic-deployment",
            "AZURE_FOUNDRY_ALLOW_UNCAPPED_GPU_HOURS": "1",
        }
        schema = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}
        with patch.dict(os.environ, env, clear=True), patch.dict(sys.modules, {"openai": types.SimpleNamespace(OpenAI=FakeOpenAI)}):
            model = FoundryChatModel(ledger, max_calls=10)
            model.token_provider = lambda: "synthetic-token"
            with self.assertRaises(OutputTruncatedError):
                model.chat_json("synthetic", "Synthetic prompt", {}, schema)
        self.assertEqual(len(calls), 1)
        self.assertEqual(ledger.totals()["api_calls"], 1)
        self.assertEqual(ledger.totals()["output_tokens"], 3)

    def test_prompt_text_is_part_of_response_cache_key(self):
        class FakeModel:
            provider = "synthetic-provider"
            model = "synthetic-model"
            deployment = "synthetic-deployment"

            def __init__(self):
                self.calls = 0
                self.ledger = UsageLedger.create()

            def chat_json(self, *_args, **_kwargs):
                self.calls += 1
                return {"value": "synthetic"}

        with tempfile.TemporaryDirectory() as directory:
            model = FakeModel()
            cached = CachedChatModel(model, JsonResponseCache(Path(directory)))
            schema = {"type": "object", "properties": {"value": {"type": "string"}}, "required": ["value"], "additionalProperties": False}
            cached.chat_json("synthetic", "prompt revision 1", {"x": 1}, schema)
            cached.chat_json("synthetic", "prompt revision 2", {"x": 1}, schema)
            changed_schema = {"type": "object", "properties": {"value": {"type": "string"}, "reason": {"type": "string"}}, "required": ["value", "reason"], "additionalProperties": False}
            cached.chat_json("synthetic", "prompt revision 2", {"x": 1}, changed_schema)
            model.model = "synthetic-model-revision-2"
            cached.chat_json("synthetic", "prompt revision 2", {"x": 1}, changed_schema)
            self.assertEqual(model.calls, 4)


class PromptContractTests(unittest.TestCase):
    def test_intent_prompt_covers_original_language_negation_and_past_audit(self):
        prompt = (ROOT / "code" / "prompts" / "intent_classification.md").read_text(encoding="utf-8")
        self.assertIn("prompt revision 2", prompt)
        self.assertIn("original language", prompt)
        self.assertIn("scope of negation", prompt)
        self.assertIn("explicitly refuses or forbids deletion", prompt)
        self.assertIn("identified past deletion", prompt)
        self.assertIn("untrusted content", prompt)
        self.assertIn("UNRESOLVED", prompt)

    def test_evidence_prompt_does_not_turn_a_retention_date_into_a_legal_hold(self):
        prompt = (ROOT / "code" / "prompts" / "evidence_classification.md").read_text(encoding="utf-8")
        self.assertIn("prompt revision 4", prompt)
        self.assertIn("retention_until", prompt)
        self.assertIn("does not by itself establish a legal hold", prompt)
        self.assertIn("category_hint` is `UNRESOLVED`", prompt)
        self.assertIn("input `evidence_id` is the source", prompt)
        self.assertIn("never invent, substitute, or transfer an ID", prompt)
        self.assertIn("identity_link_evidence_ids", prompt)
        self.assertIn("copying that ID exactly", prompt)

    def test_support_condition_requires_message_content(self):
        prompt = (ROOT / "code" / "prompts" / "policy_condition_resolution.md").read_text(encoding="utf-8")
        self.assertIn("prompt revision 2", prompt)
        self.assertIn("message body/content is missing", prompt)
        self.assertIn("requester email", prompt)
        self.assertIn("UNRESOLVED", prompt)


if __name__ == "__main__":
    unittest.main()
