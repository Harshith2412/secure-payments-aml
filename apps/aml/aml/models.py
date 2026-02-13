from sqlalchemy import Integer, String, DateTime, func, JSON, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class AmlAlert(Base):
    __tablename__ = "aml_alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    payment_id: Mapped[int] = mapped_column(Integer, index=True)
    merchant_id: Mapped[int] = mapped_column(Integer, index=True)
    score: Mapped[int] = mapped_column(Integer, index=True)
    reasons: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(30), default="open")  # open/in_review/closed
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
