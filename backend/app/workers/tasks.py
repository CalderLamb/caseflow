"""
Celery tasks — all cheap, always-on work.
The draft model is NEVER called from any task here.
"""
import asyncio
import uuid
from datetime import datetime, timezone

from app.workers.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models import Attorney, Matter, Document, CaseItem, Deadline, CaseFact, ChronologyEntry, Email, Event


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def run_drive_ingestion_task(self):
    try:
        _run_async(_drive_ingestion())
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def run_gmail_ingestion_task(self):
    try:
        _run_async(_gmail_ingestion())
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task
def analyze_document_task(document_id: str):
    _run_async(_analyze_document(uuid.UUID(document_id)))


async def _drive_ingestion():
    from sqlalchemy import select
    from app.services.ingestion.drive import run_drive_ingestion
    from app.services.analysis import extract_deadlines, extract_facts, extract_chronology
    from app.services.scoring import score_deadline_item

    async with AsyncSessionLocal() as db:
        attorney = (await db.execute(select(Attorney).where(Attorney.is_active == True))).scalars().first()
        if not attorney or not attorney.google_access_token:
            return

        matters = (await db.execute(select(Matter).where(Matter.status == "active"))).scalars().all()
        matter_map = {m.drive_folder_id: m.id for m in matters if m.drive_folder_id}

        if not matter_map:
            return

        new_docs = run_drive_ingestion(attorney.google_access_token, attorney.google_refresh_token, matter_map)

        for doc_data in new_docs:
            existing = (await db.execute(
                select(Document).where(Document.content_hash == doc_data["content_hash"])
            )).scalars().first()
            if existing:
                continue

            doc = Document(**doc_data)
            db.add(doc)
            await db.flush()

            event = Event(
                source="drive",
                event_type="new_document",
                payload={"document_id": str(doc.id), "matter_id": str(doc_data["matter_id"])},
                status="pending",
            )
            db.add(event)

        await db.commit()


async def _gmail_ingestion():
    from sqlalchemy import select
    from app.services.ingestion.gmail import run_gmail_ingestion
    from app.services.analysis import match_email_to_matter

    async with AsyncSessionLocal() as db:
        attorney = (await db.execute(select(Attorney).where(Attorney.is_active == True))).scalars().first()
        if not attorney or not attorney.google_access_token:
            return

        matters = (await db.execute(select(Matter))).scalars().all()
        matter_names = [(str(m.id), m.name) for m in matters]

        emails_data = run_gmail_ingestion(attorney.google_access_token, attorney.google_refresh_token)

        for email_data in emails_data:
            existing = (await db.execute(
                select(Email).where(Email.gmail_id == email_data["gmail_id"])
            )).scalars().first()
            if existing:
                continue

            matter_id_str = match_email_to_matter(
                email_data.get("subject", ""),
                email_data.get("body", ""),
                matter_names,
            )
            if matter_id_str:
                email_data["matter_id"] = uuid.UUID(matter_id_str)

            email = Email(**email_data)
            db.add(email)

        await db.commit()


async def _analyze_document(document_id: uuid.UUID):
    from sqlalchemy import select
    from app.services.analysis import extract_deadlines, extract_facts, extract_chronology
    from app.services.scoring import score_deadline_item
    from app.services.prediction import predict_draft_outcome

    async with AsyncSessionLocal() as db:
        doc = (await db.execute(select(Document).where(Document.id == document_id))).scalars().first()
        if not doc or doc.processed or not doc.extracted_text:
            return

        matter = (await db.execute(select(Matter).where(Matter.id == doc.matter_id))).scalars().first()
        if not matter:
            return

        deadlines = extract_deadlines(doc.extracted_text, doc.title)
        for dl in deadlines:
            try:
                from datetime import date
                due = date.fromisoformat(dl["due_date"])
                deadline = Deadline(
                    matter_id=doc.matter_id,
                    description=dl["description"],
                    due_date=due,
                    is_malpractice_class=dl.get("is_malpractice_class", False),
                    source_citation={"kind": "document", "ref": str(doc.id), "label": doc.title},
                )
                db.add(deadline)
                await db.flush()

                score, factors = score_deadline_item(
                    datetime.combine(due, datetime.min.time()),
                    has_calendar_block=False,
                    is_malpractice_class=dl.get("is_malpractice_class", False),
                )
                predicted_confidence, predicted_weaknesses, _ = predict_draft_outcome(
                    "deadline", assembled_facts_count=0, facts_with_citations=0, has_legal_precedent=False
                )

                item = CaseItem(
                    matter_id=doc.matter_id,
                    kind="deadline",
                    state="evaluated",
                    trigger_text=dl["description"],
                    trigger_citation={"kind": "document", "ref": str(doc.id), "label": doc.title},
                    proposed_action=f"Calendar and address: {dl['description']}",
                    consequence_score=score,
                    score_factors=factors,
                    predicted_confidence=predicted_confidence.value,
                    predicted_weaknesses=[w for w in predicted_weaknesses],
                )
                db.add(item)
            except Exception:
                continue

        facts = extract_facts(doc.extracted_text, doc.title)
        for f in facts:
            fact = CaseFact(
                matter_id=doc.matter_id,
                fact_text=f["text"],
                source_doc_id=doc.id,
                issue_tags=f.get("issue_tags", []),
                confidence=f.get("confidence", "medium"),
            )
            db.add(fact)

        chron_entries = extract_chronology(doc.extracted_text, doc.title)
        for e in chron_entries:
            from datetime import date as date_type
            entry_date = None
            if e.get("date"):
                try:
                    entry_date = date_type.fromisoformat(e["date"])
                except Exception:
                    pass
            entry = ChronologyEntry(
                matter_id=doc.matter_id,
                date_of_entry=entry_date,
                provider=e.get("provider"),
                findings=e.get("findings"),
                treatment=e.get("treatment"),
                source_doc_id=doc.id,
            )
            db.add(entry)

        doc.processed = True
        await db.commit()
