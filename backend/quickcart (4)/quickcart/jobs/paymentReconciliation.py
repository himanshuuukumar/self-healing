import asyncio
import logging
from shared.db.mongoClient import get_collection
from services.payment_service.providers.stripeProvider import get_payment_status

logger = logging.getLogger(__name__)

MAX_RETRIES = 5


async def reconcile_payment(order_id: str, attempt: int = 0):
    orders = get_collection("orders")
    order = await orders.find_one({"_id": order_id})

    if not order:
        logger.warning(f"reconcile_payment: order {order_id} not found")
        return

    payment_ref = order.get("payment_ref")
    if not payment_ref:
        return

    try:
        status = await get_payment_status(payment_ref)

        if status == "succeeded":
            await orders.update_one(
                {"_id": order_id},
                {"$set": {"status": "confirmed", "reconciled": True}}
            )
            logger.info(f"Reconciled order {order_id} → confirmed")

        elif status == "requires_action":
            logger.warning(f"Order {order_id} requires action — skipping")

        elif status in ("processing", "requires_confirmation"):
            # BUG: calls itself recursively with no base case check BEFORE recursing
            # attempt counter is incremented but MAX_RETRIES check is missing here
            # if Stripe keeps returning "processing", this recurses until
            # Python hits RecursionError: maximum recursion depth exceeded
            await asyncio.sleep(2)
            await reconcile_payment(order_id, attempt + 1)

        else:
            await orders.update_one(
                {"_id": order_id},
                {"$set": {"status": "payment_failed"}}
            )

    except Exception as e:
        logger.error(f"Reconciliation error for {order_id}: {e}")
        if attempt < MAX_RETRIES:
            # BUG: same issue here — retry on exception also recurses
            # combining both paths means the actual recursion depth
            # can be 2x MAX_RETRIES before hitting the Python limit
            await reconcile_payment(order_id, attempt + 1)


async def run_reconciliation():
    orders = get_collection("orders")
    pending = await orders.find({
        "status": "awaiting_payment",
        "reconciled": {"$ne": True},
    }).to_list(length=200)

    logger.info(f"Reconciliation started for {len(pending)} orders")

    tasks = [reconcile_payment(str(o["_id"])) for o in pending]
    await asyncio.gather(*tasks)

    logger.info("Reconciliation complete")


async def run_job():
    while True:
        try:
            await run_reconciliation()
        except Exception as e:
            logger.error(f"Reconciliation job failed: {e}")
        await asyncio.sleep(300)  # every 5 minutes


if __name__ == "__main__":
    asyncio.run(run_job())
