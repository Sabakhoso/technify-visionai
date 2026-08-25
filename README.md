# Technify VisionAI

> An AI intelligence layer for existing CCTV — turns live camera feeds into real-time security events, alerts, and searchable video evidence.

Technify VisionAI is a multi-tenant SaaS platform that adds AI-powered monitoring on top of a site's existing cameras. Detected objects are evaluated against configurable rules (intrusion zones, line crossing, loitering, schedules), which raise events, trigger alerts, and store evidence clips — all visible from a live dashboard.

## Architecture

The project is split into two apps that share a Supabase backend:

- **`backend/`** — FastAPI cloud API. Ingests detections from the edge AI service, runs the rule/event engine, sends alerts, and manages data. Writes to Supabase using the service-role key.
- **`frontend/`** — React (Vite) dashboard for live events, camera management, incident timelines, and evidence review. Reads Supabase directly, protected by Row-Level Security.
- **Supabase** — PostgreSQL database, authentication, and file storage for evidence clips.

> Note: AI detection and object tracking (YOLO) run in a separate edge/ML service that posts results to the backend API. That service is not part of this repository.

## Tech Stack

- **Backend:** FastAPI, async SQLAlchemy (asyncpg), Alembic, Pydantic, Supabase
- **Frontend:** React 18, Vite, React Router, Supabase JS
- **Data / Auth / Storage:** Supabase (PostgreSQL)

## Getting Started

### Prerequisites

- Python 3.13+
- Node.js 18+
- A Supabase project

### 1. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate            # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt

copy .env.example .env            # then fill in your Supabase keys and database URL

python -m alembic upgrade head    # apply database migrations
python -m uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000` (interactive API docs at `/docs`).

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

## Environment Variables

Backend configuration is loaded from `backend/.env`. Copy `backend/.env.example`, then fill in your own values. **Never commit your real `.env` file** — it contains secret keys.

## Project Status

Early development (MVP). The data model, authentication, multi-tenant isolation, and database migrations are in place; detection ingestion and alerting are in progress.

## License

Proprietary — all rights reserved.
