import logging
from fastapi import APIRouter, HTTPException, Request
from shared.db.mongoClient import get_collection
from services.delivery_service.integrations.shiprocketClient import (
    create_shipment,
    track_shipment,
    cancel_shipment,
)
from bson import ObjectId

logger = logging.getLogger(__name__)
router = APIRouter()


def build_shipment_payload(order: dict) -> dict:
    address = order.get("delivery_address", {})

    # BUG: if delivery_address is missing any field, KeyError is raised
    # no defensive access with .get() and defaults
    return {
        "order_id": str(order["_id"]),
        "order_date": order["created_at"],
        "pickup_location": "Primary Warehouse",
        "billing_customer_name": order["user_name"],
        "billing_address": address["street"],
        "billing_city": address["city"],
        "billing_pincode": address["pincode"],
        "billing_state": address["state"],
        "billing_country": address.get("country", "India"),
        "billing_email": order["user_email"],
        "billing_phone": order["user_phone"],
        "order_items": [
            {
                "name": item["name"],
                "sku": item["product_id"],
                "units": item["quantity"],
                "selling_price": item["unit_price"],
            }
            for item in order["items"]
        ],
        "payment_method": "prepaid",
        "sub_total": order["final_amount"],
        "weight": 0.5,
    }


@router.post("/delivery/ship/{order_id}")
async def ship_order(order_id: str):
    orders = get_collection("orders")
    order = await orders.find_one({"_id": ObjectId(order_id)})

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    payload = build_shipment_payload(order)

    try:
        result = create_shipment(payload)
        tracking_id = result.get("payload", {}).get("awb_code")

        await orders.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {"tracking_id": tracking_id, "status": "shipped"}},
        )

        return {"tracking_id": tracking_id, "shipment": result}

    except Exception as e:
        logger.error(f"Shipment creation failed for order {order_id}: {e}")
        raise HTTPException(status_code=502, detail="Shipment creation failed")


@router.get("/delivery/track/{order_id}")
async def track_order(order_id: str):
    orders = get_collection("orders")
    order = await orders.find_one({"_id": ObjectId(order_id)})

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    tracking_id = order.get("tracking_id")

    # BUG: if tracking_id is None (order not yet shipped),
    # track_shipment is called with None and Shiprocket returns 4xx
    # which then raises HTTPError — not caught here
    result = track_shipment(tracking_id)
    return result


@router.post("/delivery/cancel/{order_id}")
async def cancel_order_delivery(order_id: str):
    orders = get_collection("orders")
    order = await orders.find_one({"_id": ObjectId(order_id)})

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    result = cancel_shipment(order_id)

    await orders.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": "cancelled"}},
    )

    return result
