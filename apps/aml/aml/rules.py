from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass
class RuleResult:
    score: int
    reasons: list[str]

def run_rules(
    tx: dict[str, Any],
    *,
    features: dict[str, int],
    high_risk_countries: set[str],
) -> RuleResult:
    score = 0
    reasons: list[str] = []

    amt = float(tx["amount"])
    currency = (tx.get("currency") or "").lower()
    country = (tx.get("country") or "").upper()

    # Large amount (tune thresholds per business)
    if amt >= 5000:
        score += 30
        reasons.append("large_amount>=5000")

    # Velocity in 1 hour
    if features.get("merchant_tx_1h_count", 0) >= 10:
        score += 25
        reasons.append("high_velocity_1h>=10")

    # Structuring-ish behavior: repeated near-threshold amounts
    if features.get("merchant_tx_24h_near_1000_count", 0) >= 5:
        score += 25
        reasons.append("possible_structuring_near_1000")

    # High-risk geographies (placeholder field)
    if country and country in high_risk_countries:
        score += 40
        reasons.append(f"high_risk_country:{country}")

    # Unusual currency (example rule)
    if currency not in {"usd", "eur", "gbp"}:
        score += 5
        reasons.append(f"unusual_currency:{currency}")

    # Status anomalies
    if tx.get("status") != "paid":
        score += 10
        reasons.append("non_paid_event_seen")

    return RuleResult(score=min(score, 100), reasons=reasons)
