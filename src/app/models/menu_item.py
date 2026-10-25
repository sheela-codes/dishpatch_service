from decimal import Decimal
from typing import Optional

from sqlalchemy import ForeignKey, Numeric, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.database import Base


class MenuItem(Base):
    """One dish on one restaurant's menu."""
    __tablename__ = "menu_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    price: Mapped[Decimal] = mapped_column(Numeric)      # money: Decimal, not float (exact cents)
    description: Mapped[Optional[str]]
    picture: Mapped[Optional[str]]
    menu_id: Mapped[Optional[int]]                       # menus aren't used yet (always NULL)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"))
    external_ref: Mapped[Optional[str]] = mapped_column(unique=True)    # partner ref, e.g. 'M0071'
    active: Mapped[bool] = mapped_column(server_default=text("true"))

    # MANY-TO-ONE: many dishes belong to one restaurant (the other side is Restaurant.menu_items)
    restaurant: Mapped["Restaurant"] = relationship(back_populates="menu_items")
