import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    matter_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("matters.id"))
    ext_event_id: Mapped[Optional[str]] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    kind: Mapped[str] = mapped_column(String(50), default="review")  # review | deadline | hearing | deposition
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
