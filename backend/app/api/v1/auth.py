"""
Google OAuth flow — single attorney account.
No account creation in-app. Tokens stored encrypted in DB.
"""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt
from app.database import get_db
from app.models import Attorney
from app.config import settings
from app.services.ingestion.google_auth import SCOPES

router = APIRouter()


def _make_flow() -> Flow:
    return Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
    )


@router.get("/auth/login")
async def login():
    flow = _make_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return RedirectResponse(url=auth_url)


@router.get("/auth/callback")
async def callback(code: str, db: AsyncSession = Depends(get_db)):
    flow = _make_flow()
    flow.fetch_token(code=code)
    creds = flow.credentials

    from googleapiclient.discovery import build as gapi_build
    user_info = gapi_build("oauth2", "v2", credentials=creds).userinfo().get().execute()
    email = user_info.get("email", "")
    name = user_info.get("name", email)

    attorney = (await db.execute(
        select(Attorney).where(Attorney.email == email)
    )).scalars().first()

    if not attorney:
        attorney = Attorney(email=email, name=name)
        db.add(attorney)

    attorney.google_access_token = creds.token
    attorney.google_refresh_token = creds.refresh_token or attorney.google_refresh_token
    attorney.google_token_expiry = creds.expiry
    await db.commit()

    access_token = jwt.encode(
        {
            "sub": str(attorney.id),
            "email": attorney.email,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/auth/me")
async def me(db: AsyncSession = Depends(get_db)):
    attorney = (await db.execute(select(Attorney).where(Attorney.is_active == True))).scalars().first()
    if not attorney:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"id": str(attorney.id), "email": attorney.email, "name": attorney.name}
