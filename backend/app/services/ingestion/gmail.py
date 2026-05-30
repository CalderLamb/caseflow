"""
Gmail ingestion worker.
Polls for new messages, classifies them, matches to matters.
"""
import base64
import re
from typing import Optional

from googleapiclient.discovery import build
from app.services.ingestion.google_auth import build_credentials


def _decode_body(payload: dict) -> str:
    body = ""
    if "parts" in payload:
        for part in payload["parts"]:
            if part.get("mimeType") == "text/plain":
                data = part.get("body", {}).get("data", "")
                if data:
                    body += base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")
    else:
        data = payload.get("body", {}).get("data", "")
        if data:
            body = base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")
    return body


def _get_header(headers: list, name: str) -> Optional[str]:
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return None


def classify_email(subject: str, body: str) -> str:
    text = f"{subject} {body}".lower()
    if any(w in text for w in ["deposition", "notice of deposition"]):
        return "scheduling"
    if any(w in text for w in ["settlement", "demand", "offer"]):
        return "settlement"
    if any(w in text for w in ["discovery", "interrogator", "request for production"]):
        return "discovery"
    if any(w in text for w in ["hearing", "court date", "trial", "docket"]):
        return "scheduling"
    if any(w in text for w in ["medical record", "records request", "hipaa"]):
        return "records"
    return "client_update"


def run_gmail_ingestion(access_token: str, refresh_token: str, max_results: int = 50) -> list[dict]:
    creds = build_credentials(access_token, refresh_token)
    service = build("gmail", "v1", credentials=creds)

    results = service.users().messages().list(
        userId="me",
        maxResults=max_results,
        q="newer_than:7d",
    ).execute()

    messages = results.get("messages", [])
    emails = []

    for msg_meta in messages:
        try:
            msg = service.users().messages().get(
                userId="me",
                id=msg_meta["id"],
                format="full",
            ).execute()

            headers = msg.get("payload", {}).get("headers", [])
            subject = _get_header(headers, "Subject") or ""
            sender = _get_header(headers, "From") or ""
            recipients = _get_header(headers, "To") or ""
            date_str = _get_header(headers, "Date") or ""
            body = _decode_body(msg.get("payload", {}))

            classification = classify_email(subject, body)
            has_attachment = any(
                p.get("filename")
                for p in msg.get("payload", {}).get("parts", [])
                if p.get("filename")
            )

            emails.append({
                "gmail_id": msg["id"],
                "thread_id": msg.get("threadId"),
                "subject": subject,
                "sender": sender,
                "recipients": recipients,
                "direction": "outbound" if "SENT" in msg.get("labelIds", []) else "inbound",
                "snippet": msg.get("snippet", "")[:500],
                "body": body[:10000],
                "has_attachment": has_attachment,
                "classification": classification,
                "processed": False,
            })
        except Exception:
            continue

    return emails
