import logging
from fastapi import APIRouter, HTTPException, Request
from shared.db.mongoClient import get_collection
from services.payment_service.providers.stripeProvider import (
    create_payment_intent,
    confirm_payment,
    get_payment_status,
)
from services.payment_service.providers.razorpayProvider import (
    create_order as create_razorpay_order,
    verify_payment_signature,
)
from services.payment_service.utils.refundHandler import process_refund
from bson import ObjectId

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/payments/initiate")
async def initiate_payment(request: Request):
    body = await request.json()
    order_id = body.get("order_id")
    provider = body.get("provider", "stripe")

    orders = get_collection("orders")
    order = await orders.find_one({"_id": ObjectId(order_id)})

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    amount = order["final_amount"]

    try:
        if provider == "stripe":
            intent = await create_payment_intent(
                amount=amount,
                metadata={"order_id": order_id}
            )
            payment_ref = intent.id

        elif provider == "razorpay":
            rz_order = await create_razorpay_order(
                amount=amount,
                receipt=order_id
            )
            payment_ref = rz_order["id"]

        else:
            raise HTTPException(status_code=400, detail="Unsupported provider")

        await orders.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {
                "payment_ref": payment_ref,
                "payment_provider": provider,
                "status": "awaiting_payment"
            }}
        )

        return {"payment_ref": payment_ref, "provider": provider, "amount": amount}

    except Exception as e:
        # BUG: catches all exceptions but just re-raises as 500
        # Stripe-specific errors (card declined, invalid key) are swallowed
        # with no distinction — client gets no actionable info
        logger.error(f"Payment initiation failed: {e}")
        raise HTTPException(status_code=500, detail="Payment initiation failed")


@router.post("/payments/confirm")
async def confirm_payment_handler(request: Request):
    body = await request.json()
    order_id = body.get("order_id")
    payment_method_id = body.get("payment_method_id")
    payment_intent_id = body.get("payment_intent_id")

    # BUG: no validation that these fields exist in body
    # if payment_intent_id is None, confirm_payment crashes inside stripe SDK
    intent = await confirm_payment(payment_intent_id, payment_method_id)

    orders = get_collection("orders")
    await orders.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": "confirmed", "payment_id": payment_intent_id}}
    )

    return {"status": intent.status}


@router.post("/payments/verify-razorpay")
async def verify_razorpay(request: Request):
    body = await request.json()
    order_id = body.get("razorpay_order_id")
    payment_id = body.get("razorpay_payment_id")
    signature = body.get("razorpay_signature")

    valid = await verify_payment_signature(order_id, payment_id, signature)
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid payment signature")

    orders = get_collection("orders")
    await orders.update_one(
        {"razorpay_order_id": order_id},
        {"$set": {"status": "confirmed", "payment_id": payment_id}}
    )

    return {"verified": True}


@router.post("/payments/refund")
async def refund_payment(request: Request):
    body = await request.json()
    order_id = body.get("order_id")
    reason = body.get("reason", "customer_request")

    result = await process_refund(order_id, reason)
    return {"refund": result}


@router.get("/payments/{order_id}/status")
async def payment_status(order_id: str):
    orders = get_collection("orders")
    order = await orders.find_one({"_id": ObjectId(order_id)})

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    payment_ref = order.get("payment_ref")
    provider = order.get("payment_provider", "stripe")

    if provider == "stripe" and payment_ref:
        status = await get_payment_status(payment_ref)
        return {"status": status, "provider": provider}

    return {"status": order.get("status"), "provider": provider}
