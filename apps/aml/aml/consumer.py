import redis
from sqlalchemy.orm import Session
from .settings import settings
from .models import AmlAlert
from .rules import run_rules
from .features import compute_features, features_as_dict

r = redis.Redis.from_url(settings.redis_url, decode_responses=True)

def consume_forever(db_factory):
    group = "aml_group"
    stream = "tx_events"
    consumer = "aml_1"

    try:
        r.xgroup_create(stream, group, id="0-0", mkstream=True)
    except redis.exceptions.ResponseError:
        pass

    high_risk = {c.strip().upper() for c in settings.high_risk_countries.split(",") if c.strip()}

    while True:
        resp = r.xreadgroup(group, consumer, {stream: ">"}, count=10, block=5000)
        if not resp:
            continue

        for _, messages in resp:
            for msg_id, fields in messages:
                tx = dict(fields)

                feats = compute_features(r, tx)
                feats_dict = features_as_dict(feats)

                result = run_rules(tx, features=feats_dict, high_risk_countries=high_risk)

                if result.score >= settings.aml_alert_threshold:
                    db: Session = db_factory()
                    try:
                        alert = AmlAlert(
                            payment_id=int(tx["payment_id"]),
                            merchant_id=int(tx["merchant_id"]),
                            score=result.score,
                            reasons={"rules": result.reasons, "features": feats_dict},
                        )
                        db.add(alert)
                        db.commit()
                    finally:
                        db.close()

                r.xack(stream, group, msg_id)
