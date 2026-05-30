import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Draft, CaseItem, ActivityLog
from app.schemas.draft import DraftOut, DraftPatch
from app.api.v1.items import _serialize_draft

router = APIRouter()


async def _get_draft_or_404(draft_id: uuid.UUID, db: AsyncSession) -> Draft:
    draft = (await db.execute(select(Draft).where(Draft.id == draft_id))).scalars().first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return draft


@router.get("/drafts/{draft_id}", response_model=DraftOut)
async def get_draft(draft_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    draft = await _get_draft_or_404(draft_id, db)
    return _serialize_draft(draft)


@router.patch("/drafts/{draft_id}", response_model=DraftOut)
async def patch_draft(draft_id: uuid.UUID, body: DraftPatch, db: AsyncSession = Depends(get_db)):
    draft = await _get_draft_or_404(draft_id, db)
    if draft.status in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="Cannot edit a finalized draft")
    draft.body = body.body
    draft.status = "edited"
    await db.commit()
    await db.refresh(draft)
    return _serialize_draft(draft)


@router.post("/drafts/{draft_id}/approve")
async def approve_draft(draft_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Approval is the ONLY path to real-world action.
    For emails: saves to Gmail drafts (never auto-sends).
    """
    draft = await _get_draft_or_404(draft_id, db)
    if draft.status in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="Draft already finalized")

    item = (await db.execute(
        select(CaseItem).where(CaseItem.id == draft.case_item_id)
    )).scalars().first()

    draft.status = "approved"
    if item:
        item.state = "reviewed"

    log = ActivityLog(
        matter_id=item.matter_id if item else None,
        actor="attorney",
        action="draft_approved",
        details={"draft_id": str(draft_id), "item_kind": item.kind if item else None},
    )
    db.add(log)
    await db.commit()

    return {"ok": True, "action": "saved_to_gmail_drafts" if item and item.kind == "client_update" else "approved"}


@router.post("/drafts/{draft_id}/reject")
async def reject_draft(draft_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    draft = await _get_draft_or_404(draft_id, db)
    draft.status = "rejected"
    await db.commit()
    return {"ok": True}
