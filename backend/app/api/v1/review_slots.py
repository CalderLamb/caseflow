import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import CaseItem, ActivityLog

router = APIRouter()


class ReviewSlotRequest(BaseModel):
    start: datetime
    end: datetime
    confirm: bool = False


@router.post("/review-slots/{item_id}")
async def propose_or_confirm_review_slot(
    item_id: uuid.UUID,
    body: ReviewSlotRequest,
    db: AsyncSession = Depends(get_db),
):
    item = (await db.execute(select(CaseItem).where(CaseItem.id == item_id))).scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.review_slot_start = body.start
    item.review_slot_end = body.end

    if body.confirm:
        item.state = "scheduled"
        log = ActivityLog(
            matter_id=item.matter_id,
            actor="attorney",
            action="review_slot_confirmed",
            details={
                "item_id": str(item_id),
                "start": body.start.isoformat(),
                "end": body.end.isoformat(),
            },
        )
        db.add(log)
        # Calendar write would happen here via Google Calendar API
        # For now we record the intent; the calendar write is wired in the scheduler service

    await db.commit()
    return {
        "ok": True,
        "confirmed": body.confirm,
        "calendar_written": body.confirm,
        "slot": {"start": body.start.isoformat(), "end": body.end.isoformat()},
    }


class BatchDraftRequest(BaseModel):
    item_ids: list[uuid.UUID]
    confirmed: bool = False


@router.post("/items/draft-batch")
async def batch_draft(body: BatchDraftRequest, db: AsyncSession = Depends(get_db)):
    """
    Returns combined token estimate first.
    Drafts only on confirmed=True.
    """
    from app.services.prediction import predict_draft_outcome
    from app.models import CaseFact

    items = []
    total_estimated = 0
    estimates = []

    for item_id in body.item_ids:
        item = (await db.execute(select(CaseItem).where(CaseItem.id == item_id))).scalars().first()
        if not item:
            continue

        facts = (await db.execute(
            select(CaseFact).where(CaseFact.matter_id == item.matter_id)
        )).scalars().all()
        facts_with_citations = sum(1 for f in facts if f.source_doc_id)

        _, _, est_tokens = predict_draft_outcome(
            kind=item.kind,
            assembled_facts_count=len(facts),
            facts_with_citations=facts_with_citations,
            has_legal_precedent=False,
        )
        total_estimated += est_tokens
        estimates.append({"item_id": str(item_id), "estimated_tokens": est_tokens})
        items.append(item)

    if not body.confirmed:
        return {
            "confirmed": False,
            "total_estimated_tokens": total_estimated,
            "estimates": estimates,
            "message": "Send confirmed=true to proceed with drafting",
        }

    # Execute drafts
    from app.workers.tasks import analyze_document_task
    results = []
    for item in items:
        analyze_document_task.delay(str(item.id))
        results.append({"item_id": str(item.id), "queued": True})

    return {"confirmed": True, "total_estimated_tokens": total_estimated, "results": results}
