# QuickCart — E-commerce Order Management Platform

A microservices-based e-commerce backend simulating a real production system.
Built with Python (FastAPI) and Node.js (Express) across multiple independent services.

---

## Architecture

```
quickcart/
├── gateway/               # Node.js API Gateway (port 3000)
├── services/
│   ├── auth-service/      # Node.js — JWT auth, sessions (port 3001)
│   ├── order-service/     # Python FastAPI — orders, cart (port 8001)
│   ├── payment-service/   # Python FastAPI — Stripe, Razorpay (port 8002)
│   ├── notification-service/ # Node.js — email, SMS (port 3003)
│   └── delivery-service/  # Python FastAPI — Shiprocket (port 8003)
├── shared/
│   ├── db/                # MongoDB clients (Python + Node)
│   └── config/            # Settings / env vars
└── jobs/                  # Background workers (Python)
    ├── orderTimeoutJob.py
    ├── inventorySync.py
    └── paymentReconciliation.py
```

---

## Services

| Service | Language | Responsibility |
|---|---|---|
| Gateway | Node.js | Routing, rate limiting, auth middleware |
| Auth | Node.js | Register, login, JWT, sessions |
| Order | Python | Cart management, order creation |
| Payment | Python | Stripe + Razorpay integration, refunds |
| Notification | Node.js | Email (SendGrid) + SMS (Twilio) |
| Delivery | Python | Shiprocket shipping + tracking |

---

## Environment Variables Required

```env
MONGO_URI=mongodb://localhost:27017
JWT_SECRET=your_jwt_secret
STRIPE_API_KEY=sk_test_...
RAZORPAY_KEY=rzp_test_...
RAZORPAY_SECRET=...
SHIPROCKET_EMAIL=...
SHIPROCKET_PASSWORD=...
SENDGRID_API_KEY=SG....
TWILIO_SID=AC...
TWILIO_TOKEN=...
INVENTORY_API_URL=https://inventory.internal
INVENTORY_API_KEY=...
```

---

## Known Bugs (for debugging platform testing)

| File | Bug Type |
|---|---|
| `services/order-service/controllers/orderController.py` | Null reference — `user["address"]["pincode"]` when address is None |
| `services/payment-service/providers/stripeProvider.py` | No timeout on Stripe API calls |
| `shared/db/mongoClient.py` | No connection pool limit, no reconnect |
| `services/auth-service/middleware/tokenValidator.js` | Null reference — `req.headers.authorization.split()` when header missing |
| `services/notification-service/controllers/notificationController.js` | Null reference on user + unhandled promise in email send |
| `services/notification-service/providers/emailProvider.js` | Unhandled promise rejection — `sgMail.send()` not awaited |
| `services/delivery-service/integrations/shiprocketClient.py` | No timeout on external API, no fallback |
| `services/payment-service/utils/refundHandler.py` | TypeError — float + string in refund amount calculation |
| `services/order-service/controllers/cartController.py` | IndexError — `items[0]` on empty cart |
| `jobs/orderTimeoutJob.py` | Silent exception swallowing in async job loop |
| `services/order-service/utils/priceCalculator.py` | Race condition on coupon usage |
| `services/auth-service/utils/jwtHelper.js` | Unhandled crash on malformed/expired JWT |
| `jobs/inventorySync.py` | `os.environ[]` crash on missing env var at import time |
| `gateway/middleware/rateLimiter.js` | Memory leak — IP table grows unboundedly |
| `jobs/paymentReconciliation.py` | Infinite recursion — no base case before recursive call |
