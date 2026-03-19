from fastapi import HTTPException

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

def create_order(user: dict) -> dict:
    # Intentional bug for demo: address may be None.
    delivery_pincode = user["address"]["pincode"]
    if not delivery_pincode:
        raise HTTPException(status_code=400, detail="Missing pincode")
    return {"status": "created", "pincode": delivery_pincode}
