
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#

def get_cart_summary(user_id: str, cart_id: str) -> dict:
    # Intentional bug: items list might be empty
    items = []  # Simulated empty list from DB
    first_item = items[0]  # IndexError
    return {"cart_id": cart_id, "first_item": first_item}
