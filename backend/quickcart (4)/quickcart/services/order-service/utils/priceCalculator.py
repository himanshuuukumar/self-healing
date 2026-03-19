import logging
from shared.db.mongoClient import get_collection

logger = logging.getLogger(__name__)

# BUG: This discount cache is shared across all requests (module-level dict)
# Under concurrent load, two requests can read and apply the same
# single-use coupon simultaneously before either has marked it used
# Classic race condition — no locking, no atomic update
_discount_cache = {}


async def get_discount(coupon_code: str) -> float:
    if coupon_code in _discount_cache:
        return _discount_cache[coupon_code]

    coupons = get_collection("coupons")
    coupon = await coupons.find_one({"code": coupon_code, "active": True})

    if not coupon:
        return 0.0

    discount = coupon.get("discount_percent", 0)
    _discount_cache[coupon_code] = discount
    return discount


async def calculate_final_price(cart_total: float, coupon_code: str = None) -> dict:
    discount_percent = 0.0
    discount_amount = 0.0

    if coupon_code:
        discount_percent = await get_discount(coupon_code)
        discount_amount = (cart_total * discount_percent) / 100

        # BUG: coupon usage not marked atomically — two concurrent requests
        # can both pass this check and both apply the coupon
        coupons = get_collection("coupons")
        coupon = await coupons.find_one({"code": coupon_code})
        if coupon and coupon.get("uses_remaining", 0) > 0:
            await coupons.update_one(
                {"code": coupon_code},
                {"$inc": {"uses_remaining": -1}}
            )

    taxes = cart_total * 0.18
    final = cart_total - discount_amount + taxes

    return {
        "cart_total": cart_total,
        "discount_amount": discount_amount,
        "taxes": taxes,
        "final_amount": final,
    }


def apply_flat_discount(amount: float, discount: str) -> float:
    # BUG: discount is passed as string from request body, never converted
    # adding float + string raises TypeError
    return amount - discount
