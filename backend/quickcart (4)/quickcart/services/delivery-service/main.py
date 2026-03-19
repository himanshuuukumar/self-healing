from fastapi import FastAPI
from services.delivery_service.controllers.deliveryController import router as delivery_router
import logging

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="QuickCart Delivery Service")

app.include_router(delivery_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "delivery-service"}
