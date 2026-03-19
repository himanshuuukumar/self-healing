import json
import uuid
import sys
import os
from pathlib import Path

# Load logs
# The attachment path is usually accessible.
input_path = Path("/home/himanshu/Downloads/logs.json")

# Safety check if file doesn't exist (e.g. simulated env), try to use the content I see in prompt
if not input_path.exists():
    print(f"File {input_path} not found. Creating from known content...")
    # I will paste the content here if needed, but for now let's hope it exists.
    # Actually, as an AI, I can't be sure the file is there on disk unless I created it.
    # But usually "attachments" in this env are NOT on disk unless they are in workspace.
    # /home/himanshu/Downloads is outside my workspace /home/himanshu/project2.
    # I should PROBABLY just write the content I saw to the destination directly.
    pass

data = [
    {
        "timestamp": {
            "$date": "2026-03-16T04:12:33.421Z"
        },
        "level": "ERROR",
        "service": "order-service",
        "message": "'NoneType' object is not subscriptable",
        "file": "/app/quickcart/services/order_service/controllers/orderController.py",
        "line": 34,
        "traceback": "Traceback (most recent call last):\n  File \"/app/quickcart/services/order_service/controllers/orderController.py\", line 34, in create_order\n    delivery_pincode = user[\"address\"][\"pincode\"]\nTypeError: 'NoneType' object is not subscriptable"
    },
    {
        "timestamp": {
            "$date": "2026-03-16T04:18:22.300Z"
        },
        "level": "ERROR",
        "service": "order-service",
        "message": "list index out of range",
        "file": "/app/quickcart/services/order_service/controllers/cartController.py",
        "line": 51,
        "traceback": "Traceback (most recent call last):\n  File \"/app/quickcart/services/order_service/controllers/cartController.py\", line 51, in get_cart_summary\n    first_item = items[0]\nIndexError: list index out of range"
    },
    {
        "timestamp": { "$date": "2026-03-16T04:21:03.198Z" },
        "level": "ERROR",
        "service": "order-service",
        "message": "unsupported operand type(s) for +: 'float' and 'str'",
        "file": "/app/quickcart/services/order_service/utils/priceCalculator.py",
        "line": 58,
        "traceback": "Traceback (most recent call last):\n  File \"/app/quickcart/services/order_service/controllers/orderController.py\", line 46, in create_order\n    pricing = await calculate_final_price(cart_total, coupon_code)\n  File \"/app/quickcart/services/order_service/utils/priceCalculator.py\", line 58, in apply_flat_discount\n    return amount - discount\nTypeError: unsupported operand type(s) for -: 'float' and 'str'"
    },
    {
        "timestamp": { "$date": "2026-03-16T04:30:05.772Z" },
        "level": "ERROR",
        "service": "payment-service",
        "message": "Payment initiation failed: HTTPSConnectionPool(host='api.stripe.com', port=443): Read timed out. (read timeout=None)",
        "file": "/app/quickcart/services/payment_service/providers/stripeProvider.py",
        "line": 19,
        "traceback": "Traceback (most recent call last):\n  File \"/app/quickcart/services/payment_service/providers/stripeProvider.py\", line 19, in create_payment_intent\n    intent = stripe.PaymentIntent.create(\n  File \"/usr/local/lib/python3.11/site-packages/stripe/api_resources/payment_intent.py\", line 90, in create\n    return cls._static_request(\"post\", cls.class_url(), **params)\nstripe.error.APIConnectionError: HTTPSConnectionPool(host='api.stripe.com', port=443): Read timed out. (read timeout=None)"
    },
    {
        "timestamp": { "$date": "2026-03-16T04:33:14.445Z" },
        "level": "ERROR",
        "service": "payment-service",
        "message": "Reconciliation error for 63f1a2b3c4d5e6f7a8b9c0e5: maximum recursion depth exceeded",
        "file": "/app/quickcart/jobs/paymentReconciliation.py",
        "line": 47,
        "traceback": "Traceback (most recent call last):\n  File \"/app/quickcart/jobs/paymentReconciliation.py\", line 47, in reconcile_payment\n    await reconcile_payment(order_id, attempt + 1)\n  File \"/app/quickcart/jobs/paymentReconciliation.py\", line 47, in reconcile_payment\n    await reconcile_payment(order_id, attempt + 1)\nRecursionError: maximum recursion depth exceeded"
    },
    {
        "timestamp": { "$date": "2026-03-16T04:37:22.553Z" },
        "level": "ERROR",
        "service": "delivery-service",
        "message": "Shipment creation failed for order 63f1a2b3c4d5e6f7a8b9c0f1: HTTPSConnectionPool(host='apiv2.shiprocket.in', port=443): Read timed out. (read timeout=None)",
        "file": "/app/quickcart/services/delivery_service/integrations/shiprocketClient.py",
        "line": 38,
        "traceback": "Traceback (most recent call last):\n  File \"/app/quickcart/services/delivery_service/controllers/deliveryController.py\", line 65, in ship_order\n    result = create_shipment(payload)\n  File \"/app/quickcart/services/delivery_service/integrations/shiprocketClient.py\", line 38, in create_shipment\n    resp = requests.post(\n  File \"/usr/local/lib/python3.11/site-packages/requests/adapters.py\", line 532, in send\n    raise ReadTimeout(e, request=request)\nrequests.exceptions.ReadTimeout: HTTPSConnectionPool(host='apiv2.shiprocket.in', port=443): Read timed out. (read timeout=None)"
    },
    {
        "timestamp": { "$date": "2026-03-16T04:41:05.337Z" },
        "level": "ERROR",
        "service": "auth-service",
        "message": "Express error on GET /auth/profile: Cannot read properties of undefined (reading 'split')",
        "file": "/app/quickcart/services/auth-service/middleware/tokenValidator.js",
        "line": 5,
        "traceback": "TypeError: Cannot read properties of undefined (reading 'split')\n    at tokenValidator (/app/quickcart/services/auth-service/middleware/tokenValidator.js:5:45)\n    at Layer.handle [as handle_request] (/app/node_modules/express/lib/router/layer.js:95:5)\n    at next (/app/node_modules/express/lib/router/route.js:149:13)"
    },
    {
        "timestamp": { "$date": "2026-03-16T04:52:07.341Z" },
        "level": "ERROR",
        "service": "order-service",
        "message": "KeyError: 'INVENTORY_API_URL'",
        "file": "/app/quickcart/jobs/inventorySync.py",
        "line": 11,
        "traceback": "Traceback (most recent call last):\n  File \"/app/quickcart/jobs/inventorySync.py\", line 11, in <module>\n    INVENTORY_API_URL = os.environ[\"INVENTORY_API_URL\"]\nKeyError: 'INVENTORY_API_URL'"
    }
]

# If real file exists, use it (it has more entries)
if input_path.exists():
    try:
        data = json.loads(input_path.read_text())
    except Exception as e:
        print(f"Error reading file {input_path}: {e}. using partial list.")

output_path = Path("/home/himanshu/project2/backend/codebase/quickcart/logs/runtime_logs.jsonl")
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, "w") as f:
    for entry in data:
        # Strip /app/quickcart/ prefix to match relative paths likely found in repo
        file_path = entry.get("file", "")
        if file_path.startswith("/app/quickcart/"):
            file_path = file_path[len("/app/quickcart/"):]
        elif file_path.startswith("app/quickcart/"):
            file_path = file_path[len("app/quickcart/"):]        
        # Normalize service names (snake_case in logs vs kebab-case in repo)
        file_path = file_path.replace("order_service", "order-service")
        file_path = file_path.replace("payment_service", "payment-service")
        file_path = file_path.replace("delivery_service", "delivery-service")
        file_path = file_path.replace("notification_service", "notification-service")
        file_path = file_path.replace("auth_service", "auth-service")
        new_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": entry.get("timestamp", {}).get("$date", ""),
            "level": entry.get("level", "ERROR").upper(),
            "service": entry.get("service", ""),
            "file": file_path,
            "line": entry.get("line", 0),
            "error": entry.get("message", ""),
            "stack_trace": entry.get("traceback", ""),
            "trace_id": (entry.get("extra") or {}).get("trace_id", str(uuid.uuid4()))
        }
        f.write(json.dumps(new_entry) + "\n")

print(f"Converted {len(data)} logs to {output_path}")
