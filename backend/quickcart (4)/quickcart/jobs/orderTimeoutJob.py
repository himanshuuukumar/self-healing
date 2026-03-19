import asyncio
import logging
from datetime import datetime, timedelta
from shared.db.mongoClient import get_collection

logger = logging.getLogger(__name__)

TIMEOUT_MINUTES = 30


async def cancel_timed_out_orders():
    orders = get_collection("orders")
    cutoff = datetime.utcnow() - timedelta(minutes=TIMEOUT_MINUTES)

    stale_orders = await orders.find({
        "status": "awaiting_payment",
        "created_at": {"$lt": cutoff}
    }).to_list(length=100)

    cancelled = 0
    for order in stale_orders:
        await orders.update_one(
            {"_id": order["_id"]},
            {"$set": {"status": "cancelled", "cancelled_reason": "payment_timeout"}},
        )
        cancelled += 1
        logger.info(f"Cancelled timed-out order: {order['_id']}")

    return cancelled


async def run_job():
    while True:
        try:
            count = await cancel_timed_out_orders()
            logger.info(f"Order timeout job: cancelled {count} orders")
        except Exception:
            # BUG: exception is completely swallowed — no logging, no alerting
            # if cancel_timed_out_orders throws (e.g. DB connection drop),
            # the job silently continues the loop as if nothing happened
            # stale orders pile up indefinitely with no one knowing
            pass

        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(run_job())
