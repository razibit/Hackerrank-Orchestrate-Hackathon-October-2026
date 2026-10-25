from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class PolicyRule:
    category: str
    condition: str
    action: str


class PolicyResolutionError(RuntimeError):
    pass


def load_policy(rows: list[dict[str, str]]) -> dict[str, PolicyRule]:
    rules: dict[str, PolicyRule] = {}
    for row in rows:
        category = row.get("data_category", "").strip()
        condition = row.get("condition", "").strip()
        action = row.get("required_action", "").strip().upper()
        if not category or not condition or action not in {"DELETE", "REDACT", "ANONYMIZE", "RETAIN"}:
            raise ValueError("deletion_rules.csv contains an invalid rule")
        if category in rules:
            raise ValueError(f"duplicate deletion rule for {category}")
        rules[category] = PolicyRule(category, condition, action)
    return rules


def model_policy_payload(rules: dict[str, PolicyRule]) -> dict[str, dict[str, str]]:
    return {category: {"condition": rule.condition, "required_action": rule.action} for category, rule in rules.items()}


def required_treatment(rule: PolicyRule, condition: str, observed_state: str) -> str:
    """Resolve supplied conditional policy without silently treating uncertainty as success."""
    if rule.condition.casefold() == "always":
        return rule.action
    value = condition.upper()
    if value == "UNRESOLVED" or value == "NOT_APPLICABLE":
        raise PolicyResolutionError(f"{rule.category}: conditional policy is unresolved")
    if value == "TRUE":
        return rule.action
    if value != "FALSE":
        raise PolicyResolutionError(f"{rule.category}: invalid conditional policy result")

    # A false condition means the conditional action does not apply. Resolve the
    # cases whose safe outcome follows directly from the stated policy semantics.
    if rule.category in {"ANALYTICS_PROFILE", "PRODUCT_TELEMETRY", "EMAIL_DELIVERY_LOG"}:
        return "COMPLIANT"
    if rule.category in {"SUPPORT_MESSAGE", "SECURITY_AUDIT_LOG", "LEGAL_HOLD_RECORD", "ACCOUNT_TOMBSTONE"}:
        return "DELETE"
    if rule.category == "BACKUP_ARCHIVE":
        if observed_state == "BLOCKED":
            return "COMPLIANT"
        raise PolicyResolutionError("BACKUP_ARCHIVE: supplied evidence says restore access cannot be blocked")
    if rule.category == "SUPPORT_ATTACHMENT":
        raise PolicyResolutionError("SUPPORT_ATTACHMENT: evidence does not establish subject-exclusive ownership")
    raise PolicyResolutionError(f"{rule.category}: no safe false-condition treatment is specified")
