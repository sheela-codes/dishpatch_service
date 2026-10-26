from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.database import Base


class Contact(Base):
    """How to reach a person: phone, email, address."""
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    phone_number: Mapped[str]
    email: Mapped[str]
    address: Mapped[Optional[str]]
    city: Mapped[Optional[str]]
    description: Mapped[Optional[str]]

    # ONE-TO-ONE: one contact belongs to one profile (the other side is Profile.contact)
    profile: Mapped["Profile"] = relationship(back_populates="contact")
