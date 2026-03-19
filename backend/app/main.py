import asyncio
import json
import uuid

from dotenv import load_dotenv

load_dotenv()

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.models import Analysis, AnalysisRequest, StreamEvent, now_iso
from app.pipeline import run_pipeline
from app.store import store

app = FastAPI(title="Proctor Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def execute_analysis(analysis_id: str, request: AnalysisRequest) -> None:
    try:
        errors, diagnoses = await run_pipeline(analysis_id, request, store.publish)
        current = store.get_analysis(analysis_id)
        if current is None:
            return

        current.errors = errors
        current.diagnoses = diagnoses
        current.status = "completed"
        store.set_analysis(current)
    except Exception as exc:  # pragma: no cover
        failed = store.get_analysis(analysis_id)
        if failed is not None:
            failed.status = "failed"
            store.set_analysis(failed)
        await store.publish(
            analysis_id,
            StreamEvent(stage="generating_fix", status="failed", message=f"Analysis failed: {exc}"),
        )


@app.post("/api/analyze")
async def analyze(payload: AnalysisRequest, background_tasks: BackgroundTasks):
    analysis_id = str(uuid.uuid4())
    analysis = Analysis(
        id=analysis_id,
        repo=payload.github_url,
        status="running",
        created_at=now_iso(),
        errors=[],
        diagnoses=[],
    )
    store.set_analysis(analysis)
    background_tasks.add_task(execute_analysis, analysis_id, payload)
    return {"analysis_id": analysis_id}


@app.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    analysis = store.get_analysis(analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis


@app.get("/api/analysis/{analysis_id}/stream")
async def stream_analysis(analysis_id: str):
    if store.get_analysis(analysis_id) is None:
        raise HTTPException(status_code=404, detail="Analysis not found")

    async def event_generator():
        # Replay fetch logs state if already populated in store (fixes race condition where frontend connects late)
        existing = store.get_analysis(analysis_id)
        if existing and existing.errors:
            # We emit the completion event again to ensure the frontend syncs
            replay_event = StreamEvent(
                stage="fetching_logs",
                status="completed",
                data={"errors": [e.dict() for e in existing.errors]},
            )
            yield f"data: {json.dumps(replay_event.model_dump(exclude_none=True))}\n\n"

        queue = store.subscribe(analysis_id)
        try:
            while True:
                event = await queue.get()
                payload = event.model_dump(exclude_none=True)
                # In strict loop, yield properly
                yield f"data: {json.dumps(payload)}\n\n"
                if event.status in {"failed"}:
                    break
                current = store.get_analysis(analysis_id)
                if current and current.status in {"completed", "failed"} and event.stage == "generating_fix":
                    break
        finally:
            store.unsubscribe(analysis_id, queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/analyses")
async def list_analyses():
    return store.list_analyses()


@app.get("/health")
async def healthcheck():
    return {"status": "ok"}
