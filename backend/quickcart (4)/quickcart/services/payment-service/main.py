from fastapi import FastAPI
from services.payment_service.controllers.paymentController import router as payment_router
import logging

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="QuickCart Payment Service")

app.include_router(payment_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "payment-service"}
