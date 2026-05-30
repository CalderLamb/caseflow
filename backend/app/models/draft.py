import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Draft(Base):
    __tablename__ = "drafts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("case_items.id"), nullable=False)

    body: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[str] = mapped_column(String(10), nullable=False)  # high | medium | low
    annotations: Mapped[Optional[list]] = mapped_column(JSONB)
    token_cost: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    requested_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("attorneys.id"))
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="pending_review"
        # pending_review | edited | approved | rejected | superseded
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    case_item: Mapped["CaseItem"] = relationship(
        "CaseItem", foreign_keys=[case_item_id], back_populates="all_drafts"
    )
