from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.database import Base

# Already exists in Postgres; create_type=False means "use it, don't create it".
ORDER_STATUS = ENUM("placed", "accepted", "preparing", "picked_up", "delivered", "cancelled",
                    name="order_status", create_type=False)


class Order(Base):
    """One order: who ordered, from which restaurant, its status and timeline."""
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"))
    driver_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(ORDER_STATUS, server_default=text("'placed'"))
    placed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    picked_up_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    external_ref: Mapped[Optional[str]] = mapped_column(unique=True)    # partner ref

    # Two foreign keys point at users (the customer and the driver), so each relationship
    # says which column it follows.
    customer: Mapped["User"] = relationship(foreign_keys=[customer_id])
    driver: Mapped[Optional["User"]] = relationship(foreign_keys=[driver_id])
    restaurant: Mapped["Restaurant"] = relationship()

    # ONE-TO-MANY: one order has many order items (the dishes and their quantities)
    items: Mapped[List["OrderItem"]] = relationship(back_populates="order")
