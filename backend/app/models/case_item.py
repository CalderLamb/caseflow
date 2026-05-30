import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Numeric, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class CaseItem(Base):
    __tablename__ = "case_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    matter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("matters.id"), nullable=False)

    kind: Mapped[str] = mapped_column(
        String(50), nullable=False
        # deadline | client_update | discovery | motion_response | records_request
        # conflict | gap | chronology_flag | billing | other
    )
    state: Mapped[str] = mapped_column(
        String(30), nullable=False, default="detected"
        # detected | evaluated | draft_requested | drafted | scheduled | reviewed | done | dismissed | snoozed
    )

    trigger_text: Mapped[str] = mapped_column(Text, nullable=False)
    trigger_citation: Mapped[Optional[dict]] = mapped_column(JSONB)
    proposed_action: Mapped[Optional[str]] = mapped_column(Text)

    consequence_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    score_factors: Mapped[Optional[list]] = mapped_column(JSONB)

    predicted_confidence: Mapped[Optional[str]] = mapped_column(String(10))  # high | medium | low
    predicted_weaknesses: Mapped[Optional[list]] = mapped_column(JSONB)

    assembled_facts: Mapped[Optional[list]] = mapped_column(JSONB)

    draft_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("drafts.id"), nullable=True)

    review_slot_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    review_slot_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    snooze_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    matter: Mapped["Matter"] = relationship("Matter", back_populates="case_items")
    draft: Mapped[Optional["Draft"]] = relationship(
        "Draft", foreign_keys=[draft_id], primaryjoin="CaseItem.draft_id == Draft.id"
    )
    all_drafts: Mapped[list["Draft"]] = relationship(
        "Draft", foreign_keys="Draft.case_item_id", back_populates="case_item"
    )
