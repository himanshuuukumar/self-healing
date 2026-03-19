import time

def apply_coupon(coupon_code: str, user_id: str) -> None:
    # Intentional race condition
    # Fetch coupon with uses_remaining = 1
    uses_remaining = 1
    time.sleep(0.1)  # Simulate delay where another request could interleave
    if uses_remaining > 0:
        # Decrement
        uses_remaining -= 1
        # Save back to DB
