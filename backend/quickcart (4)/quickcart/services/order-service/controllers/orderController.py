import logging
from fastapi import APIRouter, HTTPException, Request
from shared.db.mongoClient import get_collection
from services.order_service.models.order import Order, OrderItem, OrderStatus, Address
from services.order_service.utils.priceCalculator import calculate_final_price
from bson import ObjectId

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_user(user_id: str):
    users = get_collection("users")
    return await users.find_one({"_id": ObjectId(user_id)})


@router.post("/orders")
async def create_order(request: Request):
    body = await request.json()
    user_id = body.get("user_id")
    items_raw = body.get("items", [])
    coupon_code = body.get("coupon_code")

    user = await get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # BUG: user["address"] is stored as None for users who haven't set it
    # accessing user["address"]["pincode"] raises TypeError: 'NoneType' is not subscriptable
    # No null check is performed before accessing nested address fields
    delivery_pincode = user["address"]["pincode"]
    delivery_city = user["address"]["city"]

    items = [OrderItem(**i) for i in items_raw]
    cart_total = sum(i.total_price for i in items)

    pricing = await calculate_final_price(cart_total, coupon_code)

    address = Address(
        street=user["address"]["street"],
        city=delivery_city,
        state=user["address"]["state"],
        pincode=delivery_pincode,
    )

    order = Order(
        user_id=user_id,
        items=items,
        delivery_address=address,
        total_amount=pricing["cart_total"],
        discount_amount=pricing["discount_amount"],
        final_amount=pricing["final_amount"],
    )

    orders = get_collection("orders")
    result = await orders.insert_one(order.to_dict())

    logger.info(f"Order created: {result.inserted_id} for user {user_id}")
    return {"order_id": str(result.inserted_id), "amount": pricing["final_amount"]}


@router.get("/orders/{order_id}")
async def get_order(order_id: str):
    orders = get_collection("orders")
    order = await orders.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order["_id"] = str(order["_id"])
    return order


@router.patch("/orders/{order_id}/status")
async def update_order_status(order_id: str, request: Request):
    body = await request.json()
    new_status = body.get("status")

    if new_status not in [s.value for s in OrderStatus]:
        raise HTTPException(status_code=400, detail="Invalid status")

    orders = get_collection("orders")
    await orders.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": new_status}},
    )
    return {"message": "Status updated"}


@router.get("/orders/user/{user_id}")
async def get_user_orders(user_id: str):
    orders = get_collection("orders")
    cursor = orders.find({"user_id": user_id})
    result = []
    async for order in cursor:
        order["_id"] = str(order["_id"])
        result.append(order)
    return result
