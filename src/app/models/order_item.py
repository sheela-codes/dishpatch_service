from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.database import Base


class OrderItem(Base):
    """One dish in one order. This is the table in the middle of the
    MANY-TO-MANY between orders and menu items (see the explanation in Order and MenuItem).
    """
    __tablename__ = "order_items"

    # Composite primary key: the PAIR (order_id, menu_item_id) is unique,
    # so a dish can appear only once per order.
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), primary_key=True)
    menu_item_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id"), primary_key=True)
    quantity: Mapped[int]
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))   # the price when the order was placed

    order: Mapped["Order"] = relationship(back_populates="items")
    menu_item: Mapped["MenuItem"] = relationship()
