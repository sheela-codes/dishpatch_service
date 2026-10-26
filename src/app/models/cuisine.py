from sqlalchemy.orm import Mapped, mapped_column
from src.app.database import Base

class Cuisine(Base):
    __tablename__ = "cuisines"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    