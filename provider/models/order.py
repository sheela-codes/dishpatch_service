from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from provider.formats import utc_timestamp


@dataclass
class OrderItem:
    """One dish inside an order (an element of the order's "items" list)."""

    item_ref: str         # 'M0071'
    quantity: int         # at least 1
    unit_price: float     # the menu price on the day of the order

    def to_json(self) -> dict:
        return {
            "item_ref": self.item_ref,
            "quantity": self.quantity,
            "unit_price": round(self.unit_price, 2),
        }


def _timestamp_or_none(dt: Optional[datetime]) -> Optional[str]:
    """Timestamps that haven't happened yet are None, which json.dumps writes as null."""
    return utc_timestamp(dt) if dt is not None else None


@dataclass
class Order:
    """One order with its items: one line of activity/orders.jsonl."""

    ref: str                          # 'O-20261019-0013'
    customer_ref: str
    restaurant_ref: str
    status: str                       # 'delivered' or 'cancelled' in generated data
    placed_at: datetime               # timezone-aware
    items: list[OrderItem] = field(default_factory=list)
    driver_ref: Optional[str] = None     # None if cancelled before pickup
    accepted_at: Optional[datetime] = None
    picked_up_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    def to_json(self) -> dict:
        """This order as one JSON object, in the partner's file format (field order as in the spec)."""
        return {
            "order_ref": self.ref,
            "customer_ref": self.customer_ref,
            "restaurant_ref": self.restaurant_ref,
            "driver_ref": self.driver_ref,
            "status": self.status,
            "placed_at": utc_timestamp(self.placed_at),
            "accepted_at": _timestamp_or_none(self.accepted_at),
            "picked_up_at": _timestamp_or_none(self.picked_up_at),
            "delivered_at": _timestamp_or_none(self.delivered_at),
            "cancelled_at": _timestamp_or_none(self.cancelled_at),
            "items": [item.to_json() for item in self.items],
        }
