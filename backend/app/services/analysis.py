"""
Document analysis service — extracts deadlines, facts, and chronology entries from document text.
All calls are cheap (Haiku model). MUST NOT invoke draft service.
"""
import json
import re
from typing import Optional
import anthropic
from app.config import settings

_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def _call_haiku(prompt: str, system: str) -> str:
    resp = _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text


def extract_deadlines(text: str, doc_title: str) -> list[dict]:
    system = """Extract legal deadlines from document text.
Return ONLY valid JSON array:
[{"description": "...", "due_date": "YYYY-MM-DD", "is_malpractice_class": true/false, "context": "..."}]
is_malpractice_class is true for statutes of limitation, prescriptive periods, or filing deadlines whose breach causes malpractice.
Return [] if none found."""

    result = _call_haiku(f"Document: {doc_title}\n\nText:\n{text[:8000]}", system)
    try:
        match = re.search(r"\[.*\]", result, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return []


def extract_facts(text: str, doc_title: str, matter_type: str = "personal_injury") -> list[dict]:
    system = """Extract key facts from a legal document.
Return ONLY valid JSON array:
[{"text": "...", "issue_tags": ["liability"|"damages"|"causation"|"procedure"], "confidence": "high"|"medium"|"low"}]
Only include facts material to a {matter_type} case. Return [] if none."""

    result = _call_haiku(f"Document: {doc_title}\n\nText:\n{text[:8000]}", system.replace("{matter_type}", matter_type))
    try:
        match = re.search(r"\[.*\]", result, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return []


def extract_chronology(text: str, doc_title: str) -> list[dict]:
    system = """Extract medical or event chronology entries from this document.
Return ONLY valid JSON array:
[{"date": "YYYY-MM-DD or null", "provider": "...", "findings": "...", "treatment": "..."}]
Return [] if no chronology entries found."""

    result = _call_haiku(f"Document: {doc_title}\n\nText:\n{text[:8000]}", system)
    try:
        match = re.search(r"\[.*\]", result, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return []


def match_email_to_matter(
    subject: str,
    body: str,
    matter_names: list[tuple[str, str]],  # [(matter_id, matter_name)]
) -> Optional[str]:
    """Returns matter_id string or None."""
    text = f"{subject}\n{body[:2000]}".lower()
    for matter_id, name in matter_names:
        parts = name.lower().replace(" v. ", " ").replace("et al.", "").split()
        key_parts = [p for p in parts if len(p) > 3][:3]
        if any(p in text for p in key_parts):
            return matter_id
    return None
