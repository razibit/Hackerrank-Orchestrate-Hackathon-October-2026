# URGENT: exact runtime model metadata needed for logging

The repository `AGENTS.md` requires an authoritative exact model identifier in both the session-start and per-turn log entries. This session exposes only the family descriptor “GPT-6”; no current rollout file was readable. Do not substitute the challenge inference deployment `openai--gpt-oss-120b`, the model selected by another task, or a guessed Codex alias.

Please check whether the exact model identifier for the Agent 3 session is available from authoritative Codex runtime metadata. If it is unavailable, retain the logging blocker in `status/agent3.md`; do not append a placeholder or fabricate an entry. The attached prompt archive and action summary are staged in this inbox for later compliant logging if metadata becomes available.
