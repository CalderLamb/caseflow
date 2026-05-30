import uuid
from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Text, Date, DateTime, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class ChronologyEntry(Base):
    __tablename__ = "chronology_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    matter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("matters.id"), nullable=False)
    date_of_entry: Mapped[Optional[date]] = mapped_column(Date)
    provider: Mapped[Optional[str]] = mapped_column(String(255))
    findings: Mapped[Optional[str]] = mapped_column(Text)
    treatment: Mapped[Optional[str]] = mapped_column(Text)
    source_doc_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"))
    page: Mapped[Optional[int]] = mapped_column()
    flagged: Mapped[bool] = mapped_column(Boolean, default=False)
    flag_reason: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
