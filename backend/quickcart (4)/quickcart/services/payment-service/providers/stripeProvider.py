import stripe
import logging
from shared.config.settings import STRIPE_API_KEY

stripe.api_key = STRIPE_API_KEY
logger = logging.getLogger(__name__)


async def create_payment_intent(amount: float, currency: str = "inr", metadata: dict = None):
    # BUG: No timeout set on Stripe API call
    # If Stripe is slow or down, this hangs indefinitely and blocks the event loop
    # No retry logic — a single network blip causes the whole payment to fail
    intent = stripe.PaymentIntent.create(
        amount=int(amount * 100),
        currency=currency,
        metadata=metadata or {},
    )
    logger.info(f"PaymentIntent created: {intent.id}")
    return intent


async def confirm_payment(payment_intent_id: str, payment_method_id: str):
    # BUG: stripe.error.CardError, stripe.error.StripeError not caught here
    # Any Stripe exception propagates up as unhandled
    intent = stripe.PaymentIntent.confirm(
        payment_intent_id,
        payment_method=payment_method_id,
    )
    return intent


async def create_refund(payment_intent_id: str, amount: float = None):
    params = {"payment_intent": payment_intent_id}
    if amount:
        params["amount"] = int(amount * 100)

    refund = stripe.Refund.create(**params)
    logger.info(f"Refund created: {refund.id}")
    return refund


async def get_payment_status(payment_intent_id: str):
    intent = stripe.PaymentIntent.retrieve(payment_intent_id)
    return intent.status
