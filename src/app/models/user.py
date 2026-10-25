from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.database import Base


class User(Base):
    """A person on Dishpatch: a customer, a driver or a restaurant owner (see account.type)."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    external_ref: Mapped[Optional[str]] = mapped_column(unique=True)    # partner ref, e.g. 'C0042'
    active: Mapped[bool] = mapped_column(server_default=text("true"))
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # ONE-TO-ONE with Account
    account: Mapped["Account"] = relationship(back_populates="user")
