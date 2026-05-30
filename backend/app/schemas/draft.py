import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.schemas.common import Confidence, WeaknessCategory


class AnnotationOut(BaseModel):
    span_start: int
    span_end: int
    category: WeaknessCategory
    note: str


class DraftOut(BaseModel):
    id: uuid.UUID
    case_item_id: uuid.UUID
    body: str
    confidence: Confidence
    annotations: list[AnnotationOut]
    token_cost: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DraftCreate(BaseModel):
    pass  # Triggered by POST /items/{id}/draft — no body needed


class DraftPatch(BaseModel):
    body: str


class DraftEstimate(BaseModel):
    predicted_confidence: Optional[Confidence]
    estimated_tokens: int
    estimated_length: str  # "~300 words"
    predicted_weaknesses: list[dict]
