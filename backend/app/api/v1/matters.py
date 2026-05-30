import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import Matter, Client, CaseItem, Deadline, Document, ChronologyEntry, CaseFact, Draft

router = APIRouter()


@router.get("/matters")
async def list_matters(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(
        select(Matter, Client).join(Client)
    )).all()

    result = []
    for matter, client in rows:
        open_items = (await db.execute(
            select(func.count()).where(
                CaseItem.matter_id == matter.id,
                CaseItem.state.not_in(["done", "dismissed"]),
            )
        )).scalar() or 0

        total_tokens = (await db.execute(
            select(func.sum(Draft.token_cost)).join(
                CaseItem, Draft.case_item_id == CaseItem.id
            ).where(CaseItem.matter_id == matter.id)
        )).scalar() or 0

        result.append({
            "id": str(matter.id),
            "name": matter.name,
            "type": matter.type,
            "status": matter.status,
            "court": matter.court,
            "case_number": matter.case_number,
            "opened_date": matter.opened_date.isoformat() if matter.opened_date else None,
            "sol_date": matter.sol_date.isoformat() if matter.sol_date else None,
            "drive_folder_id": matter.drive_folder_id,
            "client_name": client.name,
            "open_item_count": open_items,
            "total_token_cost": total_tokens,
        })
    return result


@router.get("/matters/{matter_id}")
async def get_matter(matter_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    row = (await db.execute(
        select(Matter, Client).join(Client).where(Matter.id == matter_id)
    )).first()
    if not row:
        raise HTTPException(status_code=404, detail="Matter not found")
    matter, client = row

    items = (await db.execute(
        select(CaseItem).where(CaseItem.matter_id == matter_id)
        .order_by(CaseItem.consequence_score.desc().nullslast())
        .limit(50)
    )).scalars().all()

    deadlines = (await db.execute(
        select(Deadline).where(Deadline.matter_id == matter_id)
        .order_by(Deadline.due_date)
    )).scalars().all()

    documents = (await db.execute(
        select(Document).where(Document.matter_id == matter_id)
        .order_by(Document.created_at.desc())
        .limit(50)
    )).scalars().all()

    chronology = (await db.execute(
        select(ChronologyEntry).where(ChronologyEntry.matter_id == matter_id)
        .order_by(ChronologyEntry.date_of_entry)
    )).scalars().all()

    facts = (await db.execute(
        select(CaseFact).where(CaseFact.matter_id == matter_id).limit(50)
    )).scalars().all()

    total_tokens = (await db.execute(
        select(func.sum(Draft.token_cost)).join(
            CaseItem, Draft.case_item_id == CaseItem.id
        ).where(CaseItem.matter_id == matter_id)
    )).scalar() or 0

    return {
        "id": str(matter.id),
        "name": matter.name,
        "type": matter.type,
        "status": matter.status,
        "court": matter.court,
        "case_number": matter.case_number,
        "opened_date": matter.opened_date.isoformat() if matter.opened_date else None,
        "sol_date": matter.sol_date.isoformat() if matter.sol_date else None,
        "drive_folder_id": matter.drive_folder_id,
        "client_name": client.name,
        "open_item_count": len([i for i in items if i.state not in ("done", "dismissed")]),
        "total_token_cost": total_tokens,
        "items": [{"id": str(i.id), "kind": i.kind, "state": i.state, "trigger_text": i.trigger_text, "consequence_score": float(i.consequence_score or 0)} for i in items],
        "deadlines": [{"id": str(d.id), "description": d.description, "due_date": d.due_date.isoformat(), "is_malpractice_class": d.is_malpractice_class} for d in deadlines],
        "documents": [{"id": str(d.id), "title": d.title, "doc_type": d.doc_type, "source": d.source, "processed": d.processed} for d in documents],
        "chronology": [{"id": str(e.id), "date_of_entry": e.date_of_entry.isoformat() if e.date_of_entry else None, "provider": e.provider, "findings": e.findings, "flagged": e.flagged} for e in chronology],
        "facts": [{"id": str(f.id), "text": f.fact_text, "issue_tags": f.issue_tags, "confidence": f.confidence} for f in facts],
        "cost_by_month": [],
    }


@router.get("/matters/{matter_id}/cost")
async def get_matter_cost(matter_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    total = (await db.execute(
        select(func.sum(Draft.token_cost)).join(
            CaseItem, Draft.case_item_id == CaseItem.id
        ).where(CaseItem.matter_id == matter_id)
    )).scalar() or 0
    return {"matter_id": str(matter_id), "total_tokens": total}
