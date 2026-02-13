from fastapi import FastAPI
from .db import engine, Base, SessionLocal
from .models import AmlAlert
from .consumer import consume_forever
import threading

app = FastAPI(title="AML Monitor", version="1.0.0")
Base.metadata.create_all(bind=engine)

@app.get("/alerts")
def list_alerts(limit: int = 50):
    db = SessionLocal()
    try:
        rows = db.query(AmlAlert).order_by(AmlAlert.created_at.desc()).limit(limit).all()
        return [{"id": r.id, "payment_id": r.payment_id, "score": r.score, "status": r.status, "reasons": r.reasons} for r in rows]
    finally:
        db.close()

@app.on_event("startup")
def _start_consumer():
    t = threading.Thread(target=consume_forever, args=(SessionLocal,), daemon=True)
    t.start()
