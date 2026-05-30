from typing import Optional
import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import CaseItem, Matter
from app.schemas.case_item import QueueResponse, CaseItemOut
from app.schemas.common import Citation, ScoreFactor, PredictedWeakness, ReviewSlot

router = APIRouter()


def _serialize_item(item: CaseItem, matter: Matter) -> CaseItemOut:
    citations = []
    if item.trigger_citation:
        tc = item.trigger_citation
        if isinstance(tc, list):
            citations = [Citation(**c) for c in tc]
        else:
            citations = [Citation(
                kind=tc.get("kind", "document"),
                ref=tc.get("ref", ""),
                page=tc.get("page"),
                label=tc.get("label", ""),
            )]

    review_slot = None
    if item.review_slot_start and item.review_slot_end:
        review_slot = ReviewSlot(
            start=item.review_slot_start.isoformat(),
            end=item.review_slot_end.isoformat(),
        )

    return CaseItemOut(
        id=item.id,
        matter_id=item.matter_id,
        matter_name=matter.name,
        kind=item.kind,
        state=item.state,
        trigger_text=item.trigger_text,
        trigger_citations=citations,
        proposed_action=item.proposed_action,
        consequence_score=float(item.consequence_score) if item.consequence_score is not None else None,
        score_factors=[ScoreFactor(**f) for f in (item.score_factors or [])],
        predicted_confidence=item.predicted_confidence,
        predicted_weaknesses=[PredictedWeakness(**w) for w in (item.predicted_weaknesses or [])],
        draft_id=item.draft_id,
        review_slot=review_slot,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("/queue", response_model=QueueResponse)
async def get_queue(
    state: Optional[str] = Query(None),
    matter_id: Optional[uuid.UUID] = Query(None),
    min_score: Optional[float] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(CaseItem, Matter).join(Matter, CaseItem.matter_id == Matter.id)

    q = q.where(CaseItem.state.not_in(["done", "dismissed"]))

    if state:
        q = q.where(CaseItem.state == state)
    if matter_id:
        q = q.where(CaseItem.matter_id == matter_id)
    if min_score is not None:
        q = q.where(CaseItem.consequence_score >= min_score)

    q = q.order_by(CaseItem.consequence_score.desc().nullslast(), CaseItem.created_at.desc())

    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    q = q.offset((page - 1) * page_size).limit(page_size)
    rows = (await db.execute(q)).all()

    items = [_serialize_item(item, matter) for item, matter in rows]
    return QueueResponse(items=items, total=total, page=page, page_size=page_size)
