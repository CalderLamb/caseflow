"""
Drive ingestion worker.
Watches the root folder, dedupes by content_hash, extracts text, creates Document rows.
NEVER alters sharing, moves, or deletes attorney files.
"""
import hashlib
import io
import uuid
from datetime import datetime, timezone
from typing import Optional

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from app.config import settings
from app.services.ingestion.google_auth import build_credentials


SUPPORTED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "text/plain",
    "application/vnd.google-apps.document",
}


def list_folder_files(service, folder_id: str) -> list[dict]:
    results = []
    page_token = None
    while True:
        resp = service.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            fields="nextPageToken, files(id, name, mimeType, md5Checksum, modifiedTime, parents)",
            pageToken=page_token,
        ).execute()
        results.extend(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return results


def download_file_bytes(service, file_id: str, mime_type: str) -> bytes:
    if mime_type == "application/vnd.google-apps.document":
        request = service.files().export_media(
            fileId=file_id,
            mimeType="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    else:
        request = service.files().get_media(fileId=file_id)

    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buf.getvalue()


def compute_content_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_text(data: bytes, mime_type: str) -> str:
    try:
        if mime_type == "application/pdf":
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(data))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        elif "word" in mime_type or mime_type == "application/vnd.google-apps.document":
            from docx import Document
            doc = Document(io.BytesIO(data))
            return "\n".join(p.text for p in doc.paragraphs)
        else:
            return data.decode("utf-8", errors="replace")
    except Exception:
        return ""


def detect_doc_type(filename: str, text: str) -> str:
    name_lower = filename.lower()
    text_lower = (text or "")[:500].lower()

    if any(x in name_lower for x in ["petition", "complaint", "answer"]):
        return "pleading"
    if "deposition" in name_lower or "depo" in name_lower:
        return "deposition"
    if any(x in name_lower for x in ["medical", "record", "treatment", "discharge"]):
        return "medical_record"
    if "expert" in name_lower or "report" in name_lower:
        return "expert_report"
    if any(x in name_lower for x in ["discovery", "interrogatory", "interrogatories", "request"]):
        return "discovery"
    if "insurance" in name_lower:
        return "insurance"
    if "settlement" in name_lower:
        return "settlement"
    if "intake" in name_lower or "investigation" in name_lower:
        return "intake"
    return "document"


def folder_path_from_parents(service, file_id: str) -> str:
    """Walk up to get a readable path like 'Case 1/01 - Intake/file.pdf'."""
    try:
        parts = []
        current_id = file_id
        for _ in range(5):
            meta = service.files().get(fileId=current_id, fields="name, parents").execute()
            parts.append(meta["name"])
            parents = meta.get("parents", [])
            if not parents:
                break
            current_id = parents[0]
        parts.reverse()
        return "/".join(parts)
    except Exception:
        return ""


def run_drive_ingestion(access_token: str, refresh_token: str, matter_map: dict[str, uuid.UUID]) -> list[dict]:
    """
    Scan all matter folders and return a list of new document dicts ready for DB insert.
    matter_map: {drive_folder_id -> matter_id}
    """
    creds = build_credentials(access_token, refresh_token)
    service = build("drive", "v3", credentials=creds)

    new_docs = []
    for folder_id, matter_id in matter_map.items():
        files = list_folder_files(service, folder_id)
        for f in files:
            if f["mimeType"] not in SUPPORTED_MIME_TYPES and "folder" in f["mimeType"]:
                # recurse into subfolders
                sub_files = list_folder_files(service, f["id"])
                files.extend(sub_files)
                continue
            if f["mimeType"] not in SUPPORTED_MIME_TYPES:
                continue

            file_bytes = download_file_bytes(service, f["id"], f["mimeType"])
            content_hash = compute_content_hash(file_bytes)
            text = extract_text(file_bytes, f["mimeType"])
            doc_type = detect_doc_type(f["name"], text)
            path = folder_path_from_parents(service, f["id"])

            new_docs.append({
                "matter_id": matter_id,
                "title": f["name"],
                "doc_type": doc_type,
                "source": "drive",
                "source_ref": f["id"],
                "drive_folder_path": path,
                "content_hash": content_hash,
                "extracted_text": text[:50000],
                "processed": False,
            })

    return new_docs
