from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class CartItem:
    product_id: str
    name: str
    quantity: int
    unit_price: float

    @property
    def total_price(self):
        return self.quantity * self.unit_price


@dataclass
class Cart:
    user_id: str
    items: List[CartItem] = field(default_factory=list)
    coupon_code: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def add_item(self, item: CartItem):
        for existing in self.items:
            if existing.product_id == item.product_id:
                existing.quantity += item.quantity
                return
        self.items.append(item)

    def remove_item(self, product_id: str):
        self.items = [i for i in self.items if i.product_id != product_id]

    def total(self):
        return sum(i.total_price for i in self.items)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "items": [vars(i) for i in self.items],
            "coupon_code": self.coupon_code,
            "total": self.total(),
        }
