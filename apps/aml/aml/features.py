from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import redis

@dataclass
class TxFeatures:
    merchant_tx_1h_count: int
    merchant_tx_24h_count: int
    merchant_tx_24h_near_1000_count: int

def compute_features(r: redis.Redis, tx: dict[str, Any]) -> TxFeatures:
    """
    Uses Redis expiring counters as a simple online feature store.
    """
    mid = str(tx["merchant_id"])
    amt = float(tx["amount"])

    # Velocity counters
    key_1h = f"m:{mid}:tx_1h"
    key_24h = f"m:{mid}:tx_24h"
    key_near = f"m:{mid}:near_1000_24h"

    r.incr(key_1h); r.expire(key_1h, 3600)
    r.incr(key_24h); r.expire(key_24h, 86400)

    if 900.0 <= amt <= 1100.0:
        r.incr(key_near); r.expire(key_near, 86400)

    return TxFeatures(
        merchant_tx_1h_count=int(r.get(key_1h) or 0),
        merchant_tx_24h_count=int(r.get(key_24h) or 0),
        merchant_tx_24h_near_1000_count=int(r.get(key_near) or 0),
    )

def features_as_dict(f: TxFeatures) -> dict[str, int]:
    return {
        "merchant_tx_1h_count": f.merchant_tx_1h_count,
        "merchant_tx_24h_count": f.merchant_tx_24h_count,
        "merchant_tx_24h_near_1000_count": f.merchant_tx_24h_near_1000_count,
    }
