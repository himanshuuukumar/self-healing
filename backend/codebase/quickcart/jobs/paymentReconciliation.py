import asyncio

async def reconcile_payment(order_id: str, attempt: int = 0):
    # Intentional bug: infinite recursion
    # Missing check: if attempt > MAX_RETRIES: return
    await reconcile_payment(order_id, attempt + 1)
