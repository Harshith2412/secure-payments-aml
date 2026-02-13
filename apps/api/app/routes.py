import json
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
import stripe
import redis

from .db import get_db
from .models import Payment
from .settings import settings
from .stripe_gateway import create_checkout_session
from .security import encrypt_text
from .audit import write_audit
from .schemas import PaymentCreate, PaymentCreateResponse

@router.post("/payments/create", response_model=PaymentCreateResponse)
def create_payment(payload: PaymentCreate, request: Request, db: Session = Depends(get_db)):
    amount = float(payload.amount)
    currency = payload.currency
    customer_ref = payload.customer_ref
r = redis.Redis.from_url(settings.redis_url, decode_responses=True)
router = APIRouter()

@router.post("/payments/create")
def create_payment(payload: dict, request: Request, db: Session = Depends(get_db)):
    """
    payload: { amount: 12.34, currency: "usd", customer_ref: "user-123" }
    NOTE: customer_ref is NOT a PAN; it's your internal reference (encrypted at rest).
    """
    amount = float(payload["amount"])
    currency = payload.get("currency", "usd")
    customer_ref = payload.get("customer_ref", "unknown")

    p = Payment(
        merchant_id=1,  # demo. In real life, read from JWT auth.
        amount=amount,
        currency=currency,
        status="created",
        customer_ref_enc=encrypt_text(customer_ref),
        metadata={"source": "api"},
    )
    db.add(p)
    db.commit()
    db.refresh(p)

    session = create_checkout_session(
        amount_cents=int(round(amount * 100)),
        currency=currency,
        success_url="http://localhost:8000/success",
        cancel_url="http://localhost:8000/cancel",
        metadata={"payment_id": str(p.id)},
    )

    p.stripe_checkout_session_id = session["id"]
    db.commit()

    write_audit(
        db,
        actor_user_id=1,
        action="payment.create",
        resource=f"payment:{p.id}",
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details={"amount": amount, "currency": currency},
    )

    return {"payment_id": p.id, "checkout_url": session["url"]}

@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    # PCI-ish: always verify webhook signature
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing signature")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.stripe_webhook_secret,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid webhook: {e}")

    # Idempotency: avoid double-processing the same event
    event_id = event["id"]
    if r.setnx(f"stripe_event:{event_id}", "1") == 0:
        return {"status": "duplicate_ignored"}
    r.expire(f"stripe_event:{event_id}", 60 * 60 * 24)

    event_type = event["type"]

    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        payment_id = int(session["metadata"]["payment_id"])
        payment_intent = session.get("payment_intent")

        p = db.get(Payment, payment_id)
        if not p:
            raise HTTPException(status_code=404, detail="Payment not found")

        p.status = "paid"
        p.stripe_payment_intent_id = payment_intent
        db.commit()

        # Emit to AML queue (simple Redis stream demo)
        r.xadd("tx_events", {
            "payment_id": str(p.id),
            "merchant_id": str(p.merchant_id),
            "amount": str(p.amount),
            "currency": p.currency,
            "status": p.status,
            "ts": str(p.created_at),
        })

    return {"status": "ok"}
