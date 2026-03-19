from datetime import datetime
from enum import Enum
from typing import Optional, List
from dataclasses import dataclass, field


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


@dataclass
class OrderItem:
    product_id: str
    name: str
    quantity: int
    unit_price: float
    total_price: float


@dataclass
class Address:
    street: str
    city: str
    state: str
    pincode: str
    country: str = "India"


@dataclass
class Order:
    user_id: str
    items: List[OrderItem]
    delivery_address: Address
    status: OrderStatus = OrderStatus.PENDING
    total_amount: float = 0.0
    discount_amount: float = 0.0
    final_amount: float = 0.0
    payment_id: Optional[str] = None
    tracking_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "items": [vars(i) for i in self.items],
            "delivery_address": vars(self.delivery_address),
            "status": self.status.value,
            "total_amount": self.total_amount,
            "discount_amount": self.discount_amount,
            "final_amount": self.final_amount,
            "payment_id": self.payment_id,
            "tracking_id": self.tracking_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
