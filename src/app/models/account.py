from sqlalchemy import ForeignKey, text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.database import Base

# The two enum types already exist in Postgres (created by dishpatch.sql).
# create_type=False: use them as they are; never try to create them.
ACCOUNT_TYPE = ENUM("Customer", "Restaurant", "Admin", "Driver", name="account_type", create_type=False)
PERMISSION_TYPE = ENUM("R", "RW", "RWD", "RWDE", name="permission_type", create_type=False)


class Account(Base):
    """How a person logs in: username and password, and what kind of user they are."""
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    # server_default: if we don't set it, the database fills in its own default.
    permission: Mapped[str] = mapped_column(PERMISSION_TYPE, server_default=text("'R'"))
    type: Mapped[str] = mapped_column(ACCOUNT_TYPE, server_default=text("'Customer'"))
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"))

    # ONE-TO-ONE with Profile and with User
    profile: Mapped["Profile"] = relationship(back_populates="account")
    user: Mapped["User"] = relationship(back_populates="account")
