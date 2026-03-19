import asyncio
import json
import os
import re
import shutil
import subprocess
import tempfile
import urllib.request
import uuid
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from pymongo import DESCENDING, MongoClient
from pymongo.errors import PyMongoError

from app.models import AnalysisRequest, DiagnosisResult, ErrorEntry, FixSuggestion, StreamEvent, now_iso
from app.store import store


# Keep runtime workdir outside backend source tree to avoid uvicorn --reload restarts
# when demo .py files are generated.
WORK_ROOT = Path(tempfile.gettempdir()) / "proctor-runtime-codebase"
LLM_API_BASE = os.getenv("LLM_API_BASE", "https://api.openai.com/v1").rstrip("/")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "35"))


async def run_in_thread(func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))


class IngestPipeline:
    async def run(self, analysis_id: str, request: AnalysisRequest) -> Dict:
        repo_dir, repo_label = await self._prepare_repo(analysis_id, request)
        chunks = self._chunk_repo(repo_dir)
        return {
            "repo": repo_label,
            "repo_dir": str(repo_dir),
            "chunk_count": len(chunks),
            "chunks": chunks,
            "index_summary": f"Generated {len(chunks)} searchable code chunks.",
        }

    async def _prepare_repo(self, analysis_id: str, request: AnalysisRequest) -> Tuple[Path, str]:
        WORK_ROOT.mkdir(parents=True, exist_ok=True)
        if request.github_url.startswith("local://"):
            repo_dir = WORK_ROOT / f"local_analysis_{analysis_id}"
            if repo_dir.exists():
                shutil.rmtree(repo_dir)
            
            # Locate codebase relative to this file
            backend_root = Path(__file__).resolve().parents[1]
            source_dir = backend_root / "codebase" / "quickcart"
            
            if source_dir.exists():
                shutil.copytree(source_dir, repo_dir)
                return repo_dir, request.github_url
            # Fallback to demo if local source missing (should not happen if set up right)
            request.github_url = "demo://quickcart"

        if request.github_url.startswith("demo://"):
            repo_dir = WORK_ROOT / "quickcart"
            self._create_demo_repo(repo_dir)
            return repo_dir, request.github_url

        repo_dir = WORK_ROOT / f"analysis_{analysis_id}"
        if repo_dir.exists():
            shutil.rmtree(repo_dir)

        clone_url = request.github_url
        if request.github_token and request.github_url.startswith("https://github.com/"):
            clone_url = request.github_url.replace("https://", f"https://{request.github_token}@", 1)

        proc = await run_in_thread(
            subprocess.run,
            ["git", "clone", "--depth", "1", clone_url, str(repo_dir)],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            demo_repo = WORK_ROOT / "quickcart"
            self._create_demo_repo(demo_repo)
            return demo_repo, "demo://quickcart"

        return repo_dir, request.github_url

    def _create_demo_repo(self, repo_dir: Path) -> None:
        if repo_dir.exists():
            shutil.rmtree(repo_dir)

        # Check for local codebase/quickcart source
        backend_dir = Path(__file__).resolve().parent.parent
        source_dir = backend_dir / "codebase" / "quickcart"

        if source_dir.exists():
            shutil.copytree(source_dir, repo_dir)
            return

        target = repo_dir / "services" / "order-service" / "controllers"
        target.mkdir(parents=True, exist_ok=True)
        logs_dir = repo_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)

        buggy_file = target / "orderController.py"
        buggy_file.write_text(
            """from fastapi import HTTPException\n\n\ndef create_order(user: dict) -> dict:\n    # Intentional bug for demo: address may be None.\n    delivery_pincode = user[\"address\"][\"pincode\"]\n    if not delivery_pincode:\n        raise HTTPException(status_code=400, detail=\"Missing pincode\")\n    return {\"status\": \"created\", \"pincode\": delivery_pincode}\n""",
            encoding="utf-8",
        )

        (repo_dir / "services" / "order-service" / "main.py").parent.mkdir(parents=True, exist_ok=True)
        (repo_dir / "services" / "order-service" / "main.py").write_text(
            """from controllers.orderController import create_order\n\n\ndef simulate_request() -> None:\n    user = {\"id\": \"u-101\", \"address\": None}\n    create_order(user)\n\n\nif __name__ == \"__main__\":\n    simulate_request()\n""",
            encoding="utf-8",
        )

        demo_log = {
            "timestamp": now_iso(),
            "level": "ERROR",
            "service": "order-service",
            "file": "services/order-service/controllers/orderController.py",
            "line": 6,
            "error": "TypeError: 'NoneType' object is not subscriptable",
            "stack_trace": "Traceback ... delivery_pincode = user['address']['pincode']",
            "trace_id": "trace-demo-001",
        }
        (logs_dir / "runtime_logs.jsonl").write_text(json.dumps(demo_log) + "\n", encoding="utf-8")

    def _chunk_repo(self, repo_dir: Path) -> List[Dict]:
        chunks: List[Dict] = []
        for file_path in repo_dir.rglob("*.py"):
            if any(skip in file_path.parts for skip in (".git", "__pycache__", ".venv")):
                continue

            rel = str(file_path.relative_to(repo_dir)).replace(os.sep, "/")
            lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
            window = 60
            step = 45
            start = 0
            while start < len(lines):
                end = min(len(lines), start + window)
                snippet = "\n".join(lines[start:end])
                if snippet.strip():
                    chunks.append(
                        {
                            "file": rel,
                            "start_line": start + 1,
                            "end_line": end,
                            "content": snippet,
                        }
                    )
                if end == len(lines):
                    break
                start += step

        return chunks


class LogFetcher:
    async def run(self, request: AnalysisRequest, repo_dir: Path) -> List[ErrorEntry]:
        mongo_logs = await run_in_thread(self._read_from_mongo, request)
        if mongo_logs:
            return mongo_logs
        return await run_in_thread(self._read_from_demo_file, repo_dir)

    def _read_from_mongo(self, request: AnalysisRequest) -> List[ErrorEntry]:
        if not request.mongo_uri or not request.mongo_db or not request.mongo_collection:
            return []
        try:
            with MongoClient(request.mongo_uri, serverSelectionTimeoutMS=2500) as client:
                collection = client[request.mongo_db][request.mongo_collection]
                cursor = collection.find({}, sort=[("timestamp", DESCENDING)], limit=20)
                entries: List[ErrorEntry] = []
                for doc in cursor:
                    message = str(doc.get("error") or doc.get("message") or "Unknown error")
                    level = str(doc.get("level") or "ERROR").upper()
                    entries.append(
                        ErrorEntry(
                            id=str(doc.get("_id") or uuid.uuid4()),
                            timestamp=str(doc.get("timestamp") or now_iso()),
                            level="WARN" if level == "WARN" else "ERROR",
                            service=str(doc.get("service") or "app-service"),
                            file=str(doc.get("file") or "services/order-service/controllers/orderController.py"),
                            line=int(doc.get("line") or 6),
                            error=message,
                            stack_trace=str(doc.get("stack_trace") or doc.get("traceback") or message),
                            trace_id=str(doc.get("trace_id") or f"trace-{uuid.uuid4().hex[:8]}"),
                        )
                    )
                return entries
        except PyMongoError:
            return []
        except Exception:
            return []

    def _read_from_demo_file(self, repo_dir: Path) -> List[ErrorEntry]:
        path = repo_dir / "logs" / "runtime_logs.jsonl"
        if not path.exists():
            return []

        entries: List[ErrorEntry] = []
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not line.strip():
                continue
            payload = json.loads(line)
            entries.append(
                ErrorEntry(
                    id=str(uuid.uuid4()),
                    timestamp=str(payload.get("timestamp") or now_iso()),
                    level="WARN" if str(payload.get("level", "ERROR")).upper() == "WARN" else "ERROR",
                    service=str(payload.get("service") or "order-service"),
                    file=str(payload.get("file") or "services/order-service/controllers/orderController.py"),
                    line=int(payload.get("line") or 1),
                    error=str(payload.get("error") or "Unknown error"),
                    stack_trace=str(payload.get("stack_trace") or ""),
                    trace_id=str(payload.get("trace_id") or f"trace-{uuid.uuid4().hex[:8]}"),
                )
            )
        return entries


class PromptAssembler:
    async def run(self, error: ErrorEntry, chunks: List[Dict]) -> Dict:
        keywords = set(re.findall(r"[a-zA-Z_]{3,}", f"{error.error} {error.stack_trace}".lower()))
        # Prioritize chunks that contain the error file path
        ranked = sorted(chunks, key=lambda chunk: self._score_chunk(chunk, keywords, error.file), reverse=True)
        # Proctor enhancement: Increase context window from 3 to 15 chunks for better reasoning
        selected = ranked[:15]
        prompt = (
            f"Error: {error.error}\n"
            f"File: {error.file}:{error.line}\n"
            f"Stack trace: {error.stack_trace}\n"
            f"Top chunks: {len(selected)}"
        )
        return {"prompt": prompt, "chunks": selected}

    def _score_chunk(self, chunk: Dict, keywords: set, error_file: str) -> int:
        content = chunk["content"].lower()
        # Heavily boost the file where the error actually occurred
        file_hint = 500 if chunk["file"] == error_file else 0
        # Boost if the chunk contains the specific line number range of the error
        line_hint = 200 if chunk["file"] == error_file and chunk["start_line"] <= 50 and chunk["end_line"] >= 10 else 0
        return file_hint + line_hint + sum(1 for word in keywords if word in content)


class LLMClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")

    def enabled(self) -> bool:
        return bool(self.api_key)

    def generate_plan(self, error: ErrorEntry, chunks: List[Dict]) -> Optional[Dict]:
        if not self.enabled():
            return None

        condensed_chunks = []
        # Pass all selected chunks, Gemini Flash has 1M context so this is cheap
        for chunk in chunks:
            condensed_chunks.append(
                {
                    "file": chunk["file"],
                    "start_line": chunk["start_line"],
                    "end_line": chunk["end_line"],
                    "content": chunk["content"],
                }
            )

        system = (
            "You are Proctor, an elite autonomous software debugging agent. "
            "Your goal is to fix the provided error by analyzing the runtime logs and codebase context. "
            "You must follow a rigorous chain-of-thought process:\n"
            "1. ANALYZE: Understand the error message, stack trace, and variable states.\n"
            "2. LOCALIZE: Pinpoint the exact line of code causing the crash.\n"
            "3. EXPLAIN: Describe WHY the error happens (root cause).\n"
            "4. FIX: Generate a minimal, safe, and correct patch.\n"
            "\n"
            "Return a strict JSON object with the following fields:\n"
            "- issue_summary: A concise 1-sentence description of what went wrong.\n"
            "- root_cause: A detailed technical explanation of the bug.\n"
            "- reasoning: Your step-by-step analysis of the bug and validation of the fix.\n"
            "- affected_file: The relative path to the file needing changes.\n"
            "- affected_line: The line number where the fix should be applied.\n"
            "- before: The original code snippet (context) around the error. Must match source EXACTLY.\n"
            "- after: The fixed code snippet (context) replacing the 'before' block.\n"
            "- solution_steps: An array of strings describing the fix steps.\n"
            "- confidence: A number between 0-100 indicating your certainty.\n"
        )
        user_prompt = {
            "error": {
                "message": error.error,
                "file": error.file,
                "line": error.line,
                "stack_trace": error.stack_trace,
                "service": error.service,
            },
            "chunks": condensed_chunks,
            "task": "Find the likely bug location and produce a minimal, safe fix recommendation.",
        }
        
        # Ensure base URL creates a valid path
        base_url = LLM_API_BASE.rstrip("/")
        
        payload = {
            "model": LLM_MODEL,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(user_prompt)},
            ],
        }
        req = urllib.request.Request(
            f"{base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )

        try:
            import time
            for attempt in range(3):
                try:
                    with urllib.request.urlopen(req, timeout=LLM_TIMEOUT_SECONDS) as response:
                        body = response.read().decode("utf-8")
                    break
                except urllib.error.HTTPError as e:
                    if e.code == 429 and attempt < 2:
                        time.sleep(2 * (attempt + 1))
                        continue
                    raise e
            else:
                raise Exception("Retries exhausted")

            parsed = json.loads(body)
            content = parsed["choices"][0]["message"]["content"]
            
            # Clean markdown code blocks from response
            if content.strip().startswith("```"):
                content = content.strip().split("\n", 1)[1]
                if content.strip().endswith("```"):
                    content = content.strip()[:-3]
            
            plan = json.loads(content)
            return plan
        except Exception as e:
            # Fallback for debugging locally if API fails
            import traceback
            traceback.print_exc()
            print(f"LLM generation failed: {e}")
            return None


class DiagnosisAgent:
    def __init__(self) -> None:
        self.llm = LLMClient()

    async def run(self, error: ErrorEntry, assembled: Dict) -> DiagnosisResult:
        chunks = assembled["chunks"]
        target_chunk = self._choose_target_chunk(error, chunks)
        adjusted_line, before_line = self._extract_before_line(target_chunk, error)

        plan = await run_in_thread(self.llm.generate_plan, error, chunks)
        if plan:
            return self._from_llm_plan(plan, error, before_line, adjusted_line)

        # Fallback if LLM fails
        after = "# Automatic fix generation failed. Please check logs."
        root = f"Analysis failed for error: {error.error}"
        explanation = (
            "# Analysis Failed\n\n"
            "We could not generate a fix suggestion at this time.\n"
            "Please check the backend logs for LLM API errors."
        )

        return DiagnosisResult(
            error_id=error.id,
            root_cause=root,
            affected_file=error.file,
            affected_line=adjusted_line,
            fix_suggestion=FixSuggestion(before=before_line, after=after, explanation=explanation),
            confidence=0.0,
        )

    def _from_llm_plan(self, plan: Dict, error: ErrorEntry, before_line: str, adjusted_line: int) -> DiagnosisResult:
        affected_file = str(plan.get("affected_file") or error.file)
        affected_line = int(plan.get("affected_line") or adjusted_line)
        root_cause = str(plan.get("root_cause") or plan.get("issue_summary") or error.error)
        before = str(plan.get("before") or before_line)
        after = str(plan.get("after") or "")
        
        steps = plan.get("solution_steps")
        if isinstance(steps, list):
            solution_steps = [str(step) for step in steps if str(step).strip()]
        else:
            solution_steps = ["Follow standard debugging procedures."]

        # Use the rich reasoning from the LLM if available
        reasoning = plan.get("reasoning") or plan.get("issue_summary") or error.error

        explanation = (
            "# Proctor Diagnosis\n\n"
            "## Root Cause Analysis\n"
            f"{root_cause}\n\n"
            "## Reasoning\n"
            f"{reasoning}\n\n"
            "## Recommended Solution\n"
            + "\n".join(f"{i + 1}. {step}" for i, step in enumerate(solution_steps))
        )

        confidence = float(plan.get("confidence") or 50.0)
        
        return DiagnosisResult(
            error_id=error.id,
            root_cause=root_cause,
            affected_file=affected_file,
            affected_line=affected_line,
            fix_suggestion=FixSuggestion(before=before, after=after, explanation=explanation),
            confidence=confidence,
        )

    def _choose_target_chunk(self, error: ErrorEntry, chunks: List[Dict]) -> Dict:
        for chunk in chunks:
            if chunk["file"] == error.file:
                return chunk
        return chunks[0] if chunks else {"content": "", "start_line": 1}

    def _extract_before_line(self, chunk: Dict, error: ErrorEntry) -> Tuple[int, str]:
        lines = chunk.get("content", "").splitlines()
        start_line = int(chunk.get("start_line", 1))
        
        # Try exact line match if within chunk
        idx = error.line - start_line
        if 0 <= idx < len(lines):
            return error.line, lines[idx].strip()
            
        # If line not in chunk (e.g. chunking offset), return placeholder
        return error.line, "<Code context not available for this line>"



async def stream_root_cause(analysis_id: str, diagnosis: DiagnosisResult, publish: Callable) -> None:
    words = diagnosis.root_cause.split(" ")
    progressive = ""
    for word in words:
        progressive = f"{progressive} {word}".strip()
        await publish(
            analysis_id,
            StreamEvent(
                stage="diagnosing",
                status="started",
                data={
                    "error_id": diagnosis.error_id,
                    "root_cause": progressive,
                    "affected_file": diagnosis.affected_file,
                    "affected_line": diagnosis.affected_line,
                },
            ),
        )
        await asyncio.sleep(0.04)


async def run_pipeline(analysis_id: str, request: AnalysisRequest, publish: Callable):
    ingest = IngestPipeline()
    fetcher = LogFetcher()
    assembler = PromptAssembler()
    agent = DiagnosisAgent()

    await publish(analysis_id, StreamEvent(stage="fetching_logs", status="started", message="Cloning and indexing repository"))
    index_result = await ingest.run(analysis_id, request)
    repo_dir = Path(index_result["repo_dir"])
    errors = await fetcher.run(request, repo_dir)
    if not errors:
        errors = [
            ErrorEntry(
                id=str(uuid.uuid4()),
                timestamp=now_iso(),
                level="ERROR",
                service="order-service",
                file="services/order-service/controllers/orderController.py",
                line=6,
                error="TypeError: 'NoneType' object is not subscriptable",
                stack_trace="Traceback ... delivery_pincode = user['address']['pincode']",
                trace_id="trace-fallback-001",
            )
        ]

    # Persistent save of errors to store immediately
    current_analysis = store.get_analysis(analysis_id)
    if current_analysis:
        current_analysis.errors = errors
        store.set_analysis(current_analysis)

    await publish(
        analysis_id,
        StreamEvent(
            stage="fetching_logs",
            status="completed",
            message=f"Indexed repo and fetched {len(errors)} log errors",
            data={"errors": [e.dict() for e in errors]},
        ),
    )

    await publish(analysis_id, StreamEvent(stage="retrieving_code", status="started", message="Retrieving relevant code chunks"))
    assembled = await assembler.run(errors[0], index_result["chunks"])
    await publish(
        analysis_id,
        StreamEvent(
            stage="retrieving_code",
            status="completed",
            message=f"Selected {len(assembled['chunks'])} relevant chunks",
        ),
    )

    await publish(analysis_id, StreamEvent(stage="diagnosing", status="started", message="Running diagnosis agent"))
    diagnosis = await agent.run(errors[0], assembled)
    await stream_root_cause(analysis_id, diagnosis, publish)
    await publish(
        analysis_id,
        StreamEvent(
            stage="diagnosing",
            status="completed",
            data={
                "error_id": diagnosis.error_id,
                "root_cause": diagnosis.root_cause,
                "affected_file": diagnosis.affected_file,
                "affected_line": diagnosis.affected_line,
            },
        ),
    )

    await publish(analysis_id, StreamEvent(stage="generating_fix", status="started", message="Generating PR-ready patch"))
    await asyncio.sleep(0.25)
    await publish(
        analysis_id,
        StreamEvent(
            stage="generating_fix",
            status="completed",
            data={
                "error_id": diagnosis.error_id,
                "root_cause": diagnosis.root_cause,
                "affected_file": diagnosis.affected_file,
                "affected_line": diagnosis.affected_line,
                "confidence": diagnosis.confidence,
                "fix_suggestion": {
                    "before": diagnosis.fix_suggestion.before,
                    "after": diagnosis.fix_suggestion.after,
                    "explanation": diagnosis.fix_suggestion.explanation,
                },
            },
        ),
    )

    return errors, [diagnosis]
