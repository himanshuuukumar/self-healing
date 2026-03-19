from fastapi import FastAPI
from services.order_service.controllers.orderController import router as order_router
from services.order_service.controllers.cartController import router as cart_router
import logging

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="QuickCart Order Service")

app.include_router(order_router, prefix="/api/v1")
app.include_router(cart_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "order-service"}
