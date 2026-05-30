from enum import Enum
from typing import Optional
from pydantic import BaseModel


class Confidence(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class WeaknessCategory(str, Enum):
    law = "law"
    facts = "facts"
    data = "data"
    contradiction = "contradiction"
    procedure = "procedure"


class Citation(BaseModel):
    kind: str  # document | email | event
    ref: str
    page: Optional[int] = None
    label: str


class ScoreFactor(BaseModel):
    label: str
    weight: float


class PredictedWeakness(BaseModel):
    category: WeaknessCategory
    note: str


class AssembledFact(BaseModel):
    text: str
    citation: Citation


class ReviewSlot(BaseModel):
    start: str
    end: str
