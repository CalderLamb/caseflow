import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    matter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("matters.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    doc_type: Mapped[Optional[str]] = mapped_column(String(100))
    source: Mapped[str] = mapped_column(String(20), nullable=False)  # drive | gmail | local
    source_ref: Mapped[Optional[str]] = mapped_column(String(500))
    drive_folder_path: Mapped[Optional[str]] = mapped_column(String(1000))
    content_hash: Mapped[Optional[str]] = mapped_column(String(64))
    page_count: Mapped[Optional[int]] = mapped_column(Integer)
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    extracted_text: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    matter: Mapped["Matter"] = relationship("Matter", back_populates="documents")
