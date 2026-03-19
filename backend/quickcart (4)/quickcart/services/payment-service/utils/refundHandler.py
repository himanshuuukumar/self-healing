import logging
from shared.db.mongoClient import get_collection
from services.payment_service.providers.stripeProvider import create_refund
from services.payment_service.providers.razorpayProvider import initiate_refund

logger = logging.getLogger(__name__)


async def process_refund(order_id: str, reason: str = "customer_request"):
    orders = get_collection("orders")
    order = await orders.find_one({"_id": order_id})

    if not order:
        raise ValueError(f"Order {order_id} not found")

    payment_id = order.get("payment_id")
    provider = order.get("payment_provider", "stripe")

    # BUG: order["final_amount"] is stored as float in DB
    # order["discount_amount"] is fetched from request body as string
    # Adding float + string raises TypeError: unsupported operand type(s) for +: 'float' and 'str'
    refund_amount = order["final_amount"] + order["discount_amount"]

    logger.info(f"Processing refund for order {order_id}, amount: {refund_amount}")

    if provider == "stripe":
        result = await create_refund(payment_id, refund_amount)
    elif provider == "razorpay":
        result = await initiate_refund(payment_id, refund_amount)
    else:
        raise ValueError(f"Unknown provider: {provider}")

    await orders.update_one(
        {"_id": order_id},
        {"$set": {"status": "refunded", "refund_id": result.get("id")}},
    )

    return result


async def calculate_partial_refund(order_id: str, item_ids: list) -> float:
    orders = get_collection("orders")
    order = await orders.find_one({"_id": order_id})

    items = order.get("items", [])
    refund_total = 0.0

    for item in items:
        if item["product_id"] in item_ids:
            refund_total += item["total_price"]

    return refund_total
