import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import CaseItem, Matter, Draft, CaseFact
from app.schemas.case_item import CaseItemDetail, DismissRequest, SnoozeRequest
from app.schemas.draft import DraftOut, DraftEstimate
from app.schemas.common import Citation, ScoreFactor, PredictedWeakness, AssembledFact, ReviewSlot, Confidence
from app.api.v1.queue import _serialize_item

router = APIRouter()


async def _get_item_or_404(item_id: uuid.UUID, db: AsyncSession) -> tuple[CaseItem, Matter]:
    row = (await db.execute(
        select(CaseItem, Matter).join(Matter).where(CaseItem.id == item_id)
    )).first()
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")
    return row[0], row[1]


@router.get("/items/{item_id}", response_model=CaseItemDetail)
async def get_item(item_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    item, matter = await _get_item_or_404(item_id, db)

    facts = (await db.execute(
        select(CaseFact).where(CaseFact.matter_id == item.matter_id).limit(20)
    )).scalars().all()

    assembled_facts = [
        AssembledFact(
            text=f.fact_text,
            citation=Citation(
                kind="document",
                ref=str(f.source_doc_id) if f.source_doc_id else "",
                page=f.page,
                label=f"page {f.page}" if f.page else "document",
            ),
        )
        for f in facts
    ]

    base = _serialize_item(item, matter)
    return CaseItemDetail(**base.model_dump(), assembled_facts=assembled_facts)


@router.post("/items/{item_id}/draft", response_model=DraftOut)
async def request_draft(item_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    THE expensive endpoint. Generates one draft + self-critique.
    Idempotent per item — returns existing pending draft if already generated.
    """
    item, matter = await _get_item_or_404(item_id, db)

    if item.draft_id:
        existing = (await db.execute(select(Draft).where(Draft.id == item.draft_id))).scalars().first()
        if existing and existing.status == "pending_review":
            return _serialize_draft(existing)

    from app.services.draft_service import generate_draft
    from app.models import CaseFact

    facts = (await db.execute(
        select(CaseFact).where(CaseFact.matter_id == item.matter_id).limit(20)
    )).scalars().all()

    assembled_facts = [
        {
            "text": f.fact_text,
            "citation": {"kind": "document", "ref": str(f.source_doc_id or ""), "label": "source doc"},
        }
        for f in facts
    ]

    body, confidence, annotations, token_cost = generate_draft(
        item_kind=item.kind,
        trigger_text=item.trigger_text,
        assembled_facts=assembled_facts,
        matter_name=matter.name,
    )

    draft = Draft(
        case_item_id=item.id,
        body=body,
        confidence=confidence,
        annotations=annotations,
        token_cost=token_cost,
        status="pending_review",
    )
    db.add(draft)
    await db.flush()

    item.draft_id = draft.id
    item.state = "drafted"
    await db.commit()
    await db.refresh(draft)

    return _serialize_draft(draft)


@router.post("/items/{item_id}/draft/estimate", response_model=DraftEstimate)
async def estimate_draft(item_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    item, matter = await _get_item_or_404(item_id, db)

    facts = (await db.execute(
        select(CaseFact).where(CaseFact.matter_id == item.matter_id)
    )).scalars().all()

    facts_with_citations = sum(1 for f in facts if f.source_doc_id)
    from app.services.prediction import predict_draft_outcome
    predicted_confidence, predicted_weaknesses, estimated_tokens = predict_draft_outcome(
        kind=item.kind,
        assembled_facts_count=len(facts),
        facts_with_citations=facts_with_citations,
        has_legal_precedent=False,
    )
    words = estimated_tokens // 2
    return DraftEstimate(
        predicted_confidence=predicted_confidence,
        estimated_tokens=estimated_tokens,
        estimated_length=f"~{words} words",
        predicted_weaknesses=[{"category": w["category"], "note": w["note"]} for w in predicted_weaknesses],
    )


@router.post("/items/{item_id}/dismiss", status_code=status.HTTP_204_NO_CONTENT)
async def dismiss_item(item_id: uuid.UUID, body: DismissRequest, db: AsyncSession = Depends(get_db)):
    item, _ = await _get_item_or_404(item_id, db)
    item.state = "dismissed"
    await db.commit()


@router.post("/items/{item_id}/snooze", status_code=status.HTTP_204_NO_CONTENT)
async def snooze_item(item_id: uuid.UUID, body: SnoozeRequest, db: AsyncSession = Depends(get_db)):
    item, _ = await _get_item_or_404(item_id, db)
    item.state = "snoozed"
    item.snooze_until = body.snooze_until
    await db.commit()


@router.post("/items/{item_id}/rerank")
async def rerank_item(item_id: uuid.UUID, new_score: float, db: AsyncSession = Depends(get_db)):
    """Capture attorney re-ordering as a training signal."""
    item, _ = await _get_item_or_404(item_id, db)
    from app.models import ActivityLog
    log = ActivityLog(
        matter_id=item.matter_id,
        actor="attorney",
        action="rerank",
        details={"item_id": str(item_id), "old_score": float(item.consequence_score or 0), "new_score": new_score},
    )
    db.add(log)
    await db.commit()
    return {"ok": True}


def _serialize_draft(draft: Draft) -> DraftOut:
    from app.schemas.draft import AnnotationOut
    from app.schemas.common import WeaknessCategory
    annotations = []
    for a in (draft.annotations or []):
        try:
            annotations.append(AnnotationOut(
                span_start=a.get("span_start", 0),
                span_end=a.get("span_end", 0),
                category=WeaknessCategory(a.get("category", "data")),
                note=a.get("note", ""),
            ))
        except Exception:
            pass
    return DraftOut(
        id=draft.id,
        case_item_id=draft.case_item_id,
        body=draft.body,
        confidence=Confidence(draft.confidence),
        annotations=annotations,
        token_cost=draft.token_cost,
        status=draft.status,
        created_at=draft.created_at,
        updated_at=draft.updated_at,
    )
