import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class CaseFact(Base):
    __tablename__ = "case_facts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    matter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("matters.id"), nullable=False)
    fact_text: Mapped[str] = mapped_column(Text, nullable=False)
    source_doc_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"))
    page: Mapped[Optional[int]] = mapped_column()
    issue_tags: Mapped[Optional[list]] = mapped_column(JSONB)  # ["liability", "damages", "causation"]
    confidence: Mapped[Optional[str]] = mapped_column(String(10))
    contradicts_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("case_facts.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
