import logging
from fastapi import APIRouter, HTTPException, Request
from shared.db.mongoClient import get_collection
from services.order_service.models.cart import Cart, CartItem

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/cart/{user_id}")
async def get_cart(user_id: str):
    carts = get_collection("carts")
    cart = await carts.find_one({"user_id": user_id})
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart


@router.post("/cart/{user_id}/add")
async def add_to_cart(user_id: str, item: dict):
    carts = get_collection("carts")
    cart_data = await carts.find_one({"user_id": user_id})

    cart = Cart(user_id=user_id)
    if cart_data:
        cart.items = [CartItem(**i) for i in cart_data.get("items", [])]

    cart.add_item(CartItem(**item))
    await carts.update_one(
        {"user_id": user_id},
        {"$set": cart.to_dict()},
        upsert=True,
    )
    return {"message": "Item added"}


@router.get("/cart/{user_id}/summary")
async def get_cart_summary(user_id: str):
    carts = get_collection("carts")
    cart_data = await carts.find_one({"user_id": user_id})

    if not cart_data:
        raise HTTPException(status_code=404, detail="Cart not found")

    items = cart_data.get("items", [])

    # BUG: directly accesses items[0] without checking if list is empty
    # Empty cart will raise IndexError: list index out of range
    first_item = items[0]
    logger.info(f"Cart for {user_id} starts with product: {first_item['product_id']}")

    return {
        "item_count": len(items),
        "first_item": first_item,
        "total": sum(i["unit_price"] * i["quantity"] for i in items),
    }


@router.delete("/cart/{user_id}/clear")
async def clear_cart(user_id: str):
    carts = get_collection("carts")
    await carts.delete_one({"user_id": user_id})
    return {"message": "Cart cleared"}
