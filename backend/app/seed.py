"""
Seed the database with the 4 real Louisiana PI cases from Google Drive.
Run: python -m app.seed
"""
import asyncio
import uuid
from datetime import date, datetime, timezone

from app.database import AsyncSessionLocal, engine, Base
from app.models import Client, Matter, CaseItem, Deadline


# Real Drive folder IDs from the CaseFlow Google Drive
CASES = [
    {
        "client_name": "Marie Thibodaux",
        "matter_name": "Thibodaux v. Pelican Bay Shopping Center LLC",
        "type": "personal_injury",
        "court": "19th Judicial District Court, East Baton Rouge Parish",
        "case_number": "C-2025-4821",
        "opened_date": date(2025, 3, 12),
        "sol_date": date(2026, 3, 12),
        "drive_folder_id": "1NeXDRQ-dt3UsQzgWQYenDHhTITOoiPPw",
        "items": [
            {
                "kind": "deadline",
                "trigger_text": "Statute of limitations expires in 286 days — slip-and-fall injury 2025-03-12",
                "proposed_action": "File suit or confirm pre-suit settlement before SOL date",
                "consequence_score": 72.0,
                "score_factors": [
                    {"label": "malpractice-class deadline", "weight": 45},
                    {"label": "286d remaining", "weight": 8},
                    {"label": "no calendar protection", "weight": 15},
                ],
                "state": "evaluated",
                "predicted_confidence": "high",
            },
            {
                "kind": "client_update",
                "trigger_text": "No outbound communication to client in 22 days",
                "proposed_action": "Send status update to Marie Thibodaux",
                "consequence_score": 23.0,
                "score_factors": [
                    {"label": "client update needed", "weight": 10},
                    {"label": "22d since last contact", "weight": 10},
                ],
                "state": "evaluated",
                "predicted_confidence": "high",
            },
        ],
        "deadlines": [
            {
                "description": "Louisiana prescriptive period — personal injury (La. C.C. art. 3492)",
                "due_date": date(2026, 3, 12),
                "is_malpractice_class": True,
                "priority": "critical",
            }
        ],
    },
    {
        "client_name": "James Broussard",
        "matter_name": "Broussard v. Fontenot et al.",
        "type": "personal_injury",
        "court": "14th Judicial District Court, Calcasieu Parish",
        "case_number": "C-2024-11032",
        "opened_date": date(2024, 9, 5),
        "sol_date": date(2025, 9, 5),
        "drive_folder_id": "1JJFD33RHr7r8w_C3D4oagPiK50UNi58V",
        "items": [
            {
                "kind": "deadline",
                "trigger_text": "SOL expired 2025-09-05 — case must be filed or prescriptive period interrupted",
                "proposed_action": "URGENT: Verify filing status and interrupt prescription immediately",
                "consequence_score": 95.0,
                "score_factors": [
                    {"label": "malpractice-class deadline", "weight": 45},
                    {"label": "past due", "weight": 30},
                    {"label": "no calendar protection", "weight": 15},
                ],
                "state": "evaluated",
                "predicted_confidence": "medium",
            },
            {
                "kind": "discovery",
                "trigger_text": "Expert reports received — plaintiff's expert contradicts defendant's biomechanical report",
                "proposed_action": "Prepare Daubert challenge or supplemental expert designation",
                "consequence_score": 40.0,
                "score_factors": [
                    {"label": "discovery", "weight": 35},
                    {"label": "high-stakes matter", "weight": 5},
                ],
                "state": "evaluated",
                "predicted_confidence": "medium",
                "predicted_weaknesses": [
                    {"category": "law", "note": "Daubert standard in Louisiana state court — verify La. C.E. art. 702 current standard"},
                    {"category": "facts", "note": "Defendant's expert report not yet in file — assertion partially sourced"},
                ],
            },
        ],
        "deadlines": [
            {
                "description": "Louisiana 1-year prescriptive period (La. C.C. art. 3492)",
                "due_date": date(2025, 9, 5),
                "is_malpractice_class": True,
                "priority": "critical",
            }
        ],
    },
    {
        "client_name": "Renee Arceneaux",
        "matter_name": "Arceneaux v. Gulf Coast Properties Inc.",
        "type": "personal_injury",
        "court": "32nd Judicial District Court, Terrebonne Parish",
        "case_number": "C-2025-0341",
        "opened_date": date(2025, 1, 18),
        "sol_date": date(2026, 1, 18),
        "drive_folder_id": "1f-pf4PYSLxFYB5aBTR5iqSAlXCdjY0yE",
        "items": [
            {
                "kind": "motion_response",
                "trigger_text": "Defendant's MSJ filed 2026-05-15 — response due within 15 days",
                "proposed_action": "Draft opposition to motion for summary judgment",
                "consequence_score": 88.0,
                "score_factors": [
                    {"label": "motion_response", "weight": 40},
                    {"label": "malpractice-class deadline", "weight": 45},
                    {"label": "3d remaining", "weight": 25},
                ],
                "state": "evaluated",
                "predicted_confidence": "medium",
                "predicted_weaknesses": [
                    {"category": "facts", "note": "IME report not yet fully processed into fact database"},
                    {"category": "law", "note": "Verify current MSJ standard under La. C.C.P. art. 966"},
                ],
            },
            {
                "kind": "chronology_flag",
                "trigger_text": "6-week gap in medical treatment records between 2025-08-12 and 2025-09-28",
                "proposed_action": "Obtain records from all treating providers for the gap period",
                "consequence_score": 35.0,
                "score_factors": [
                    {"label": "chronology_flag", "weight": 28},
                    {"label": "treatment gap flagged", "weight": 7},
                ],
                "state": "evaluated",
                "predicted_confidence": "low",
                "predicted_weaknesses": [
                    {"category": "data", "note": "Gap period records not in file — draft cannot be sourced"},
                ],
            },
        ],
        "deadlines": [
            {
                "description": "MSJ Response — La. C.C.P. art. 966",
                "due_date": date(2026, 5, 30),
                "is_malpractice_class": True,
                "priority": "critical",
            }
        ],
    },
    {
        "client_name": "Estate of Henri Fontenot",
        "matter_name": "Succession of Fontenot v. Our Lady of the Lake RMC",
        "type": "medical_malpractice",
        "court": "19th Judicial District Court, East Baton Rouge Parish",
        "case_number": "C-2024-7714",
        "opened_date": date(2024, 6, 3),
        "sol_date": date(2025, 6, 3),
        "drive_folder_id": "1ZVhceRRreXLaA7-NGv_xl42Q_Lf2nDgK",
        "items": [
            {
                "kind": "records_request",
                "trigger_text": "Medical records request to OLOL outstanding 47 days — no response",
                "proposed_action": "Send follow-up demand letter; consider subpoena if no response within 7 days",
                "consequence_score": 52.0,
                "score_factors": [
                    {"label": "records_request", "weight": 25},
                    {"label": "47d no response", "weight": 20},
                    {"label": "malpractice matter", "weight": 7},
                ],
                "state": "evaluated",
                "predicted_confidence": "high",
            },
            {
                "kind": "gap",
                "trigger_text": "Operative notes for 2024-05-28 procedure not received — critical liability document",
                "proposed_action": "Subpoena operative notes directly from hospital HIM department",
                "consequence_score": 61.0,
                "score_factors": [
                    {"label": "gap", "weight": 30},
                    {"label": "critical liability document missing", "weight": 25},
                    {"label": "malpractice matter", "weight": 6},
                ],
                "state": "evaluated",
                "predicted_confidence": "low",
                "predicted_weaknesses": [
                    {"category": "data", "note": "Operative notes not in file — any draft asserting procedural facts will be unverified"},
                ],
            },
        ],
        "deadlines": [],
    },
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        for case in CASES:
            # Create client
            client = Client(name=case["client_name"])
            db.add(client)
            await db.flush()

            # Create matter
            matter = Matter(
                client_id=client.id,
                name=case["matter_name"],
                type=case["type"],
                status="active",
                court=case.get("court"),
                case_number=case.get("case_number"),
                opened_date=case.get("opened_date"),
                sol_date=case.get("sol_date"),
                drive_folder_id=case.get("drive_folder_id"),
            )
            db.add(matter)
            await db.flush()

            # Create deadlines
            for dl in case.get("deadlines", []):
                deadline = Deadline(
                    matter_id=matter.id,
                    description=dl["description"],
                    due_date=dl["due_date"],
                    is_malpractice_class=dl.get("is_malpractice_class", False),
                    priority=dl.get("priority", "normal"),
                )
                db.add(deadline)

            # Create case items
            for item_data in case.get("items", []):
                item = CaseItem(
                    matter_id=matter.id,
                    kind=item_data["kind"],
                    state=item_data.get("state", "evaluated"),
                    trigger_text=item_data["trigger_text"],
                    trigger_citation={"kind": "document", "ref": case.get("drive_folder_id", ""), "label": case["matter_name"]},
                    proposed_action=item_data.get("proposed_action"),
                    consequence_score=item_data.get("consequence_score"),
                    score_factors=item_data.get("score_factors", []),
                    predicted_confidence=item_data.get("predicted_confidence"),
                    predicted_weaknesses=item_data.get("predicted_weaknesses", []),
                )
                db.add(item)

        await db.commit()
        print("Seeded 4 Louisiana PI matters with case items and deadlines.")


if __name__ == "__main__":
    asyncio.run(seed())
