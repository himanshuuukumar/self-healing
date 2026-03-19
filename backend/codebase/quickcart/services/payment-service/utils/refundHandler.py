def process_refund(order_id: str) -> float:
    # Intentional bug: type mismatch
    order = {
        "final_amount": 1299.0,
        "discount_amount": "200"  # String instead of float
    }
    refund_amount = order["final_amount"] + order["discount_amount"]
    return refund_amount
