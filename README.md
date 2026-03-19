# Proctor - Autonomous Debugging Platform

This workspace contains:

- `frontend/` - Next.js 14 dashboard (TypeScript, Tailwind, Zustand, shadcn-style UI)
- `backend/` - FastAPI analysis service with SSE streaming

## Frontend

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

## Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open the dashboard at `http://localhost:3000`.

## Quick Demo Flow

To run the end-to-end demo pipeline with intentional bug + logs:

1. Open `http://localhost:3000/analyze`
2. Set `GitHub Repo URL` to `demo://quickcart`
3. Fill GitHub token with any placeholder value (form requires a minimum length)
4. Provide MongoDB values:
	- if reachable, backend reads real logs from MongoDB
	- if unreachable, backend automatically uses local demo logs
5. Click `Run Analysis`

The backend now performs repository setup, log ingestion, code chunking, diagnosis, and PR-style fix generation.
