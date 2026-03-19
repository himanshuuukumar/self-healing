import time
import requests

def track_shipment(tracking_id: str) -> dict:
    # Intentional bug: timeout
    time.sleep(31)
    # The logs say requests.exceptions.ReadTimeout
    raise requests.exceptions.ReadTimeout("Read timed out")
