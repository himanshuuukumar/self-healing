# Proctor Backend (FastAPI)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

- `POST /api/analyze`
- `GET /api/analysis/{id}`
- `GET /api/analysis/{id}/stream`
- `GET /api/analyses`

## Demo Mode

Use this to run a full realistic demo with an intentionally broken service and generated logs.

1. In the dashboard, set `GitHub Repo URL` to `demo://quickcart`.
2. Fill MongoDB fields as normal.
3. If MongoDB is reachable, logs are read from your collection.
4. If MongoDB is unavailable, pipeline falls back to local demo logs in `backend/codebase/quickcart/logs/runtime_logs.jsonl`.

The pipeline will:

- create or clone the codebase
- chunk and index Python files
- correlate error logs with code chunks
- run diagnosis agent logic
- produce PR-style root cause, affected file/line, and fix patch

## Optional LLM Agent Mode

Set environment variables in `.env` to enable real LLM-based diagnosis planning:

- `LLM_API_KEY` or `OPENAI_API_KEY`
- `LLM_API_BASE` (default `https://api.openai.com/v1`)
- `LLM_MODEL` (default `gpt-4o-mini`)
- `LLM_TIMEOUT_SECONDS` (default `35`)

If no key is provided, backend automatically uses deterministic fallback diagnosis logic.
