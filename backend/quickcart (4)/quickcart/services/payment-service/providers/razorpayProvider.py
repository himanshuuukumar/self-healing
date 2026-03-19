import razorpay
import logging
from shared.config.settings import RAZORPAY_KEY, RAZORPAY_SECRET

client = razorpay.Client(auth=(RAZORPAY_KEY, RAZORPAY_SECRET))
logger = logging.getLogger(__name__)


async def create_order(amount: float, currency: str = "INR", receipt: str = None):
    # BUG: No error handling — razorpay.errors.BadRequestError not caught
    order = client.order.create({
        "amount": int(amount * 100),
        "currency": currency,
        "receipt": receipt or "receipt#default",
        "payment_capture": 1,
    })
    return order


async def verify_payment_signature(order_id: str, payment_id: str, signature: str) -> bool:
    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
        })
        return True
    except Exception:
        return False


async def fetch_payment(payment_id: str):
    payment = client.payment.fetch(payment_id)
    return payment


async def initiate_refund(payment_id: str, amount: float):
    refund = client.payment.refund(payment_id, {"amount": int(amount * 100)})
    return refund
