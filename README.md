# CaseFlow

**A proactive legal intelligence system.** Watches Google Drive, Gmail, and Calendar — turns what it finds into ranked Case Items. Drafting is on-demand and attorney-triggered only.

## What it does

- **Ranked queue** — every case item gets a 0–100 consequence score. Malpractice-class deadlines surface first.
- **On-demand drafts** — one press generates a draft via Claude. It never fires automatically.
- **Self-critique** — every draft comes back with a confidence grade (high/medium/low) and inline typed annotations marking weaknesses: `law`, `facts`, `data`, `contradiction`, `procedure`.
- **Drive ingestion** — polls the configured folder, dedupes by content hash, extracts text, and creates items from deadlines, gaps, and facts it finds.
- **Gmail ingestion** — classifies inbound/outbound mail, matches to matters, creates `client_update` items.
- **Every assertion is cited.** Trigger text, facts, and annotations all link to source.

## Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + TypeScript + Vite + Tailwind + TanStack Query |
| Backend | Python 3.11 + FastAPI + SQLAlchemy 2 (async) + Alembic |
| Database | PostgreSQL 16 (Supabase or local) |
| Queue | Celery + Redis |
| AI | Anthropic Claude (Opus for drafts, Haiku for analysis/critique) |
| Auth | Google OAuth 2.0 (single attorney account) |

## Google Drive

The watched folder contains 4 active matters:

| Matter | Status |
|---|---|
| Thibodaux v. Pelican Bay Shopping Center LLC | active |
| Broussard v. Fontenot et al. | active |
| Arceneaux v. Gulf Coast Properties Inc. | active |
| Succession of Fontenot v. Our Lady of the Lake RMC | active |

## Quick start

```bash
# 1. Clone and configure
cp backend/.env.example backend/.env
# Fill in ANTHROPIC_API_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

# 2. Start services
docker-compose up -d db redis

# 3. Run backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 4. Seed database with 4 real Louisiana PI matters
python -m app.seed

# 5. Run frontend
cd ../frontend
npm install
npm run dev
# → http://localhost:5173

# 6. Start Celery worker (Drive + Gmail ingestion)
cd backend
celery -A app.workers.celery_app worker --loglevel=info
```

## Google OAuth setup

1. Create a project at [Google Cloud Console](https://console.cloud.google.com)
2. Enable: Google Drive API, Gmail API, Google Calendar API, Google OAuth2
3. Create OAuth credentials → Web application
4. Add `http://localhost:8000/auth/callback` as authorized redirect URI
5. Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`
6. Visit `http://localhost:8000/auth/login` to authorize

## Architecture

```
SOURCE EVENTS      ALWAYS-ON (cheap)       ON-DEMAND (expensive)
─────────────      ─────────────────────   ─────────────────────
Google Drive ──┐
Gmail        ──┤──▶ Ingestion ──▶ Analysis ──▶ Case Items
Calendar     ──┘    Scoring      Prediction    │
                                               │ attorney presses button
                                               ▼
                                         Draft Service
                                         (Claude Opus)
                                               │
                                               ▼
                                    Draft + confidence + annotations
```

## API contract

OpenAPI schema at `http://localhost:8000/docs`

Key rules:
1. **No endpoint except `POST /items/{id}/draft` and `POST /items/draft-batch` may invoke the draft model.**
2. **Real-world actions (send, file, calendar write) only happen through an `approve` call.**
3. **The system reads Drive but never alters sharing, moves, or deletes files.**

## Testing

```bash
cd backend
pip install -r requirements.txt
pytest tests/
```

The `test_draft_isolation` test does a static import check — it fails if any ingestion/scoring path imports `draft_service`.

## Phase status

- [x] Phase 0 — Foundation (scaffold, schema, contract, auth, seed data)
- [x] Phase 1 — Deadline items (Drive ingestion, scorer v1, scheduler)
- [x] Phase 2 — Gmail + request-a-draft path (prediction, draft service, self-critique)
- [ ] Phase 3 — Documents, chronology, medium-confidence drafts
- [ ] Phase 4 — Scoring intelligence + explainability
- [ ] Phase 5 — Scheduling the day + batch + billing byproduct
