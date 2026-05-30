import uuid
from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Text, Date, DateTime, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Deadline(Base):
    __tablename__ = "deadlines"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    matter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("matters.id"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="normal")  # critical | high | normal | low
    is_malpractice_class: Mapped[bool] = mapped_column(Boolean, default=False)
    calendar_event_id: Mapped[Optional[str]] = mapped_column(String(255))
    source_citation: Mapped[Optional[dict]] = mapped_column(JSONB)
    warning_dates: Mapped[Optional[list]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    matter: Mapped["Matter"] = relationship("Matter", back_populates="deadlines")
