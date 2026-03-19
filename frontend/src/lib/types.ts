export interface AnalysisRequest {
  github_url: string;
  github_token: string;
  mongo_uri: string;
  mongo_db: string;
  mongo_collection: string;
}

export interface ErrorEntry {
  id: string;
  timestamp: string;
  level: "ERROR" | "WARN";
  service: string;
  file: string;
  line: number;
  error: string;
  stack_trace: string;
  trace_id: string;
}

export interface DiagnosisResult {
  error_id: string;
  root_cause: string;
  affected_file: string;
  affected_line: number;
  fix_suggestion: {
    before: string;
    after: string;
    explanation: string;
  };
  confidence: number;
}

export interface Analysis {
  id: string;
  repo: string;
  status: "running" | "completed" | "failed";
  created_at: string;
  errors: ErrorEntry[];
  diagnoses: DiagnosisResult[];
}

export type StreamStage =
  | "fetching_logs"
  | "retrieving_code"
  | "diagnosing"
  | "generating_fix";

export interface StreamEvent {
  stage: StreamStage;
  status: "started" | "completed" | "failed";
  data?: Partial<DiagnosisResult> & { errors?: ErrorEntry[] };
  message?: string;
}

export type StageStatus = "idle" | "running" | "completed" | "failed";
