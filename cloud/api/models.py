
from datetime import datetime, timezone

from sqlalchemy import Integer, Float, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class Inspection(Base):
    __tablename__ = "inspections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mean_brightness: Mapped[float] = mapped_column(Float)
    standard_deviation: Mapped[float] = mapped_column(Float)
    min_brightness: Mapped[int] = mapped_column(Integer)
    max_brightness: Mapped[int] = mapped_column(Integer)
    uniformity_score: Mapped[float] = mapped_column(Float)
    inspection_status: Mapped[str] = mapped_column(String(10))

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=True
    )
