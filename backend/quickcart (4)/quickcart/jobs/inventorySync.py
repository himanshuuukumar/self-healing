import os
import asyncio
import logging
import requests
from shared.db.mongoClient import get_collection

logger = logging.getLogger(__name__)

# BUG: os.environ[] raises KeyError immediately at import time
# if INVENTORY_API_URL is not in the environment
# This crashes the entire job process on startup — not just this file
INVENTORY_API_URL = os.environ["INVENTORY_API_URL"]
INVENTORY_API_KEY = os.environ["INVENTORY_API_KEY"]


async def fetch_inventory_from_api() -> list:
    # BUG: No timeout — if inventory API is slow, this blocks the event loop
    resp = requests.get(
        f"{INVENTORY_API_URL}/products/stock",
        headers={"X-API-Key": INVENTORY_API_KEY},
    )
    resp.raise_for_status()
    return resp.json().get("products", [])


async def sync_inventory():
    products_from_api = await fetch_inventory_from_api()
    products_col = get_collection("products")

    updated = 0
    for product in products_from_api:
        result = await products_col.update_one(
            {"sku": product["sku"]},
            {
                "$set": {
                    "stock": product["quantity"],
                    "price": product["price"],
                    "last_synced": product.get("updated_at"),
                }
            },
        )
        if result.modified_count:
            updated += 1

    logger.info(f"Inventory sync complete: {updated} products updated")
    return updated


async def run_job():
    while True:
        try:
            await sync_inventory()
        except Exception as e:
            logger.error(f"Inventory sync failed: {e}")

        # sync every 15 minutes
        await asyncio.sleep(900)


if __name__ == "__main__":
    asyncio.run(run_job())
