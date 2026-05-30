import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.schemas.common import (
    Confidence, Citation, ScoreFactor, PredictedWeakness, AssembledFact, ReviewSlot
)


class CaseItemOut(BaseModel):
    id: uuid.UUID
    matter_id: uuid.UUID
    matter_name: str
    kind: str
    state: str
    trigger_text: str
    trigger_citations: list[Citation]
    proposed_action: Optional[str]
    consequence_score: Optional[float]
    score_factors: list[ScoreFactor]
    predicted_confidence: Optional[Confidence]
    predicted_weaknesses: list[PredictedWeakness]
    draft_id: Optional[uuid.UUID]
    review_slot: Optional[ReviewSlot]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CaseItemDetail(CaseItemOut):
    assembled_facts: list[AssembledFact]


class DismissRequest(BaseModel):
    reason: str


class SnoozeRequest(BaseModel):
    snooze_until: datetime


class QueueParams(BaseModel):
    state: Optional[str] = None
    matter_id: Optional[uuid.UUID] = None
    min_score: Optional[float] = None
    page: int = 1
    page_size: int = 50


class QueueResponse(BaseModel):
    items: list[CaseItemOut]
    total: int
    page: int
    page_size: int
