from datetime import date
from typing import List, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column

from src.app.database import Base



class Restaurant(Base):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    operational: Mapped[bool] = mapped_column(default=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))         
    menu_items: Mapped[List["MenuItem"]] = relationship(back_populates="restaurant")   
    cuisine_id: Mapped[int] = mapped_column(ForeignKey("cuisines.id"))
    city: Mapped[str]
    opened_at: Mapped[Optional[date]]
    external_ref: Mapped[Optional[str]]
    cuisine: Mapped["Cuisine"] = relationship()        # follow cuisine_id to the Cuisine object
    owner: Mapped["User"] = relationship()      # follow user_id to the User object