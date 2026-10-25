import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

from audit_agent.model import (
    FoundryChatModel,
    ModelConfigurationError,
    OutputTruncatedError,
    UsageLedger,
    classify_observations,
)
from audit_agent.cache import CachedChatModel, JsonResponseCache
import main


class FoundryConfigurationTests(unittest.TestCase):
    def test_copied_completion_endpoint_is_normalized_for_openai_sdk(self):
        values = {
            "AZURE_FOUNDRY_ENDPOINT": "https://resource.services.ai.azure.com/openai/v1/chat/completions?api-version=2026-01-01",
            "AZURE_FOUNDRY_DEPLOYMENT": "deployment-name",
            "AZURE_FOUNDRY_ALLOW_UNCAPPED_GPU_HOURS": "1",
            "MAX_RUN_COST_USD": "30",
        }
        with patch.dict(os.environ, values, clear=True):
            model = FoundryChatModel(UsageLedger.create(), max_calls=8)
        self.assertEqual(model.endpoint, "https://resource.services.ai.azure.com/openai/v1/")
        self.assertEqual(model.deployment, "deployment-name")
        self.assertTrue(model.uncapped_gpu_hours)
        self.assertIsNone(model.cap)
        self.assertEqual(model.max_calls, 8)

    def test_rate_capped_mode_requires_verified_rate_and_start(self):
        values = {
            "AZURE_FOUNDRY_ENDPOINT": "https://resource.services.ai.azure.com",
            "AZURE_FOUNDRY_DEPLOYMENT": "deployment-name",
            "MAX_RUN_COST_USD": "30",
        }
        with patch.dict(os.environ, values, clear=True):
            with self.assertRaisesRegex(ModelConfigurationError, "verified Foundry accelerator rate"):
                FoundryChatModel(UsageLedger.create())

    def test_zero_model_call_limit_means_unlimited(self):
        values = {
            "AZURE_FOUNDRY_ENDPOINT": "https://resource.services.ai.azure.com",
            "AZURE_FOUNDRY_DEPLOYMENT": "deployment-name",
            "AZURE_FOUNDRY_ALLOW_UNCAPPED_GPU_HOURS": "1",
        }
        with patch.dict(os.environ, values, clear=True):
            model = FoundryChatModel(UsageLedger.create(), max_calls=0)
        self.assertEqual(model.max_calls, 0)
        model._guard()
        model.ledger.records.extend({} for _ in range(1001))
        model._guard()

    def test_negative_model_call_limit_is_rejected(self):
        values = {
            "AZURE_FOUNDRY_ENDPOINT": "https://resource.services.ai.azure.com",
            "AZURE_FOUNDRY_DEPLOYMENT": "deployment-name",
            "AZURE_FOUNDRY_ALLOW_UNCAPPED_GPU_HOURS": "1",
        }
        with patch.dict(os.environ, values, clear=True):
            with self.assertRaisesRegex(ModelConfigurationError, "zero \\(unlimited\\)"):
                FoundryChatModel(UsageLedger.create(), max_calls=-1)

    def test_local_loader_ignores_all_api_key_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env"
            path.write_text(
                "AZURE_OPENAI_ENDPOINT=https://resource.services.ai.azure.com/openai/v1/chat/completions\n"
                "DEPLOYMENT_NAME=deployment-name\n"
                "AZURE_OPENAI_API_KEY=never-load-this\n"
                "AZURE_FOUNDRY_API_KEY=never-load-this-either\n",
                encoding="utf-8",
            )
            with patch.object(main, "ROOT", Path(directory)), patch.dict(os.environ, {}, clear=True):
                main._load_local_configuration()
                self.assertEqual(os.environ["AZURE_FOUNDRY_ENDPOINT"], "https://resource.services.ai.azure.com/openai/v1/chat/completions")
                self.assertEqual(os.environ["AZURE_FOUNDRY_DEPLOYMENT"], "deployment-name")
                self.assertNotIn("AZURE_OPENAI_API_KEY", os.environ)
                self.assertNotIn("AZURE_FOUNDRY_API_KEY", os.environ)


class CacheOnlyReplayTests(unittest.TestCase):
    def test_cache_only_reuses_cached_result_without_calling_provider(self):
        class FakeModel:
            provider = "test-provider"
            model = "test-model"
            deployment = "test-deployment"

            def __init__(self):
                self.ledger = UsageLedger.create()
                self.calls = 0

            def chat_json(self, purpose, system_prompt, payload, schema, max_tokens=3000):
                self.calls += 1
                return {"classification": "kept"}

        with tempfile.TemporaryDirectory() as directory:
            fake = FakeModel()
            cache = JsonResponseCache(Path(directory))
            online_wrapper = CachedChatModel(fake, cache)
            args = ("test", "prompt", {"x": 1}, {"type": "object"})
            self.assertEqual(online_wrapper.chat_json(*args), {"classification": "kept"})
            self.assertEqual(fake.calls, 1)

            offline_wrapper = CachedChatModel(fake, cache, cache_only=True)
            self.assertEqual(offline_wrapper.chat_json(*args), {"classification": "kept"})
            self.assertEqual(fake.calls, 1)

    def test_cache_only_fails_closed_on_miss_without_provider_call(self):
        class FakeModel:
            provider = "test-provider"
            model = "test-model"
            deployment = "test-deployment"

            def __init__(self):
                self.ledger = UsageLedger.create()
                self.calls = 0

            def chat_json(self, *args, **kwargs):
                self.calls += 1
                return {"unexpected": True}

        with tempfile.TemporaryDirectory() as directory:
            fake = FakeModel()
            wrapper = CachedChatModel(fake, JsonResponseCache(Path(directory)), cache_only=True)
            with self.assertRaisesRegex(RuntimeError, "cache-only replay"):
                wrapper.chat_json("test", "prompt", {"x": 1}, {"type": "object"})
            self.assertEqual(fake.calls, 0)


class TruncatedStructuredOutputTests(unittest.TestCase):
    def test_evidence_batches_split_after_provider_length_stop(self):
        class SplitOnlyModel:
            calls = 0

            def chat_json(self, purpose, system_prompt, payload, schema, max_tokens=3000):
                self.calls += 1
                items = payload["observations"]
                if len(items) > 1:
                    raise OutputTruncatedError("synthetic provider length stop")
                item = items[0]
                return {"observations": [{"observation_id": item["observation_id"]}]}

        model = SplitOnlyModel()
        observations = [{"observation_id": f"obs-{index}"} for index in range(5)]
        result = classify_observations(
            model, "case-test", "user-test", "2026-10-01T00:00:00Z", observations, "prompt",
        )
        self.assertEqual(set(result), {item["observation_id"] for item in observations})
        self.assertGreater(model.calls, 1)

    def test_single_observation_truncation_stays_unresolved(self):
        class AlwaysTruncatedModel:
            def chat_json(self, *args, **kwargs):
                raise OutputTruncatedError("synthetic provider length stop")

        with self.assertRaises(OutputTruncatedError):
            classify_observations(
                AlwaysTruncatedModel(), "case-test", "user-test", "2026-10-01T00:00:00Z",
                [{"observation_id": "obs-1"}], "prompt",
            )


if __name__ == "__main__":
    unittest.main()
