import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Email(Base):
    __tablename__ = "emails"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    matter_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("matters.id"))
    gmail_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    thread_id: Mapped[Optional[str]] = mapped_column(String(255))
    subject: Mapped[Optional[str]] = mapped_column(Text)
    sender: Mapped[Optional[str]] = mapped_column(String(500))
    recipients: Mapped[Optional[str]] = mapped_column(Text)
    direction: Mapped[str] = mapped_column(String(10), default="inbound")  # inbound | outbound
    snippet: Mapped[Optional[str]] = mapped_column(Text)
    body: Mapped[Optional[str]] = mapped_column(Text)
    received_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    has_attachment: Mapped[bool] = mapped_column(Boolean, default=False)
    classification: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
