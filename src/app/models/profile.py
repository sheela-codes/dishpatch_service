from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.database import Base


class Profile(Base):
    """A person's name and picture."""
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    preferred_name: Mapped[Optional[str]]
    picture: Mapped[Optional[str]]
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id"))

    # ONE-TO-ONE with Contact and with Account
    contact: Mapped["Contact"] = relationship(back_populates="profile")
    account: Mapped["Account"] = relationship(back_populates="profile")
