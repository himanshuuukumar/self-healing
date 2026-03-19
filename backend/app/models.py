from datetime import datetime, timezone
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    github_url: str
    github_token: Optional[str] = ""
    mongo_uri: Optional[str] = ""
    mongo_db: Optional[str] = ""
    mongo_collection: Optional[str] = ""
    cubeapm_url: Optional[str] = None
    cubeapm_key: Optional[str] = None


class ErrorEntry(BaseModel):
    id: str
    timestamp: str
    level: Literal["ERROR", "WARN"]
    service: str
    file: str
    line: int
    error: str
    stack_trace: str
    trace_id: str


class FixSuggestion(BaseModel):
    before: str
    after: str
    explanation: str


class DiagnosisResult(BaseModel):
    error_id: str
    root_cause: str
    affected_file: str
    affected_line: int
    fix_suggestion: FixSuggestion
    confidence: float = Field(ge=0, le=100)


class Analysis(BaseModel):
    id: str
    repo: str
    status: Literal["running", "completed", "failed"]
    created_at: str
    errors: List[ErrorEntry]
    diagnoses: List[DiagnosisResult]


class StreamEvent(BaseModel):
    stage: Literal["fetching_logs", "retrieving_code", "diagnosing", "generating_fix"]
    status: Literal["started", "completed", "failed"]
    data: Optional[Dict] = None
    message: Optional[str] = None


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
