import requests
import logging
from shared.config.settings import SHIPROCKET_EMAIL, SHIPROCKET_PASSWORD

logger = logging.getLogger(__name__)

_token = None


def get_auth_token() -> str:
    global _token
    if _token:
        return _token

    # BUG: No timeout set on this request
    # If Shiprocket auth endpoint is slow or down, this blocks indefinitely
    resp = requests.post(
        "https://apiv2.shiprocket.in/v1/external/auth/login",
        json={"email": SHIPROCKET_EMAIL, "password": SHIPROCKET_PASSWORD},
    )
    resp.raise_for_status()
    _token = resp.json()["token"]
    return _token


def create_shipment(order_data: dict) -> dict:
    token = get_auth_token()

    # BUG: No timeout on external API call
    # No retry logic — transient network failure = complete failure
    # No fallback to a secondary carrier
    resp = requests.post(
        "https://apiv2.shiprocket.in/v1/external/orders/create/adhoc",
        headers={"Authorization": f"Bearer {token}"},
        json=order_data,
    )

    # BUG: if resp.status_code is 4xx/5xx, raise_for_status raises
    # but it's not caught here — propagates as unhandled HTTPError
    resp.raise_for_status()
    return resp.json()


def track_shipment(tracking_id: str) -> dict:
    token = get_auth_token()

    resp = requests.get(
        f"https://apiv2.shiprocket.in/v1/external/courier/track/awb/{tracking_id}",
        headers={"Authorization": f"Bearer {token}"},
        # BUG: still no timeout — if Shiprocket is degraded,
        # every tracking request in the system hangs waiting
    )
    resp.raise_for_status()
    return resp.json()


def cancel_shipment(order_id: str) -> dict:
    token = get_auth_token()
    resp = requests.post(
        "https://apiv2.shiprocket.in/v1/external/orders/cancel",
        headers={"Authorization": f"Bearer {token}"},
        json={"ids": [order_id]},
    )
    resp.raise_for_status()
    return resp.json()
