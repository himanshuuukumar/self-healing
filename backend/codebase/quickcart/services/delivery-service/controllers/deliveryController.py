from ..integrations.shiprocketClient import track_shipment

def track_order(order_id: str):
    # This just calls the buggy service
    return track_shipment("trk_123")
