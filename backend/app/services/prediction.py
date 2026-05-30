"""
Prediction service — estimates draft confidence BEFORE any draft is generated.
Uses cheap signals: match clarity, fact sourcing, law settledness.
"""
from typing import Optional
from app.schemas.common import Confidence


def predict_draft_outcome(
    kind: str,
    assembled_facts_count: int,
    facts_with_citations: int,
    has_legal_precedent: bool,
    matter_type: str = "personal_injury",
) -> tuple[Confidence, list[dict], int]:
    """
    Returns (predicted_confidence, predicted_weaknesses, estimated_tokens).
    """
    weaknesses = []
    score = 0  # higher = worse outcome

    citation_ratio = facts_with_citations / max(assembled_facts_count, 1)
    if citation_ratio < 0.5:
        score += 2
        weaknesses.append({
            "category": "facts",
            "note": "fewer than half of assembled facts have cited sources — draft may assert unsourced claims",
        })
    elif citation_ratio < 0.8:
        score += 1
        weaknesses.append({
            "category": "facts",
            "note": "some facts lack direct citations — verify before approving",
        })

    if assembled_facts_count == 0:
        score += 3
        weaknesses.append({
            "category": "data",
            "note": "no assembled facts in the file for this item — draft will rely on general patterns",
        })

    if not has_legal_precedent:
        score += 2
        weaknesses.append({
            "category": "law",
            "note": "no verified legal authority found in the file — cited standards unverified",
        })

    # Routing by kind complexity
    complex_kinds = {"motion_response", "chronology_flag", "gap", "conflict"}
    routine_kinds = {"client_update", "deadline", "billing"}

    if kind in complex_kinds:
        score += 1

    if score == 0 and kind in routine_kinds:
        confidence = Confidence.high
        estimated_tokens = 400
    elif score <= 1:
        confidence = Confidence.high
        estimated_tokens = 600
    elif score <= 3:
        confidence = Confidence.medium
        estimated_tokens = 800
    else:
        confidence = Confidence.low
        estimated_tokens = 1000

    return confidence, weaknesses, estimated_tokens
