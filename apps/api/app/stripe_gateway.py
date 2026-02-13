import stripe
from .settings import settings

stripe.api_key = settings.stripe_secret_key

def create_checkout_session(*, amount_cents: int, currency: str, success_url: str, cancel_url: str, metadata: dict):
    # Hosted Checkout = you do not handle card data
    return stripe.checkout.Session.create(
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": currency,
                "product_data": {"name": "Order Payment"},
                "unit_amount": amount_cents,
            },
            "quantity": 1,
        }],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata=metadata,
    )
