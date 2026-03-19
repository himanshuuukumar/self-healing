import { Analysis, AnalysisRequest, StreamEvent } from "@/lib/types";

const API_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "").replace(/\/$/, "");
const API_TIMEOUT_MS = 30000;

function apiUrl(path: string): string {
  return API_BASE ? `${API_BASE}${path}` : path;
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), API_TIMEOUT_MS);

  try {
    const response = await fetch(apiUrl(path), {
      ...init,
      signal: controller.signal,
    });

    if (!response.ok) {
      const body = await response.text().catch(() => "");
      const detail = body?.trim() ? ` ${body.trim()}` : "";
      throw new Error(`Request failed (${response.status}).${detail}`);
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error("Request timed out. Ensure backend is running on port 8000 and try again.");
    }
    if (error instanceof TypeError) {
      throw new Error("Network error: could not reach backend. Ensure backend is running and refresh the page.");
    }
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("Unexpected request error");
  } finally {
    clearTimeout(timeout);
  }
}

export async function startAnalysis(payload: AnalysisRequest): Promise<{ analysis_id: string }> {
  return requestJson<{ analysis_id: string }>("/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function getAnalysis(id: string): Promise<Analysis> {
  return requestJson<Analysis>(`/api/analysis/${id}`, {
    cache: "no-store",
  });
}

export async function getAnalyses(): Promise<Analysis[]> {
  return requestJson<Analysis[]>("/api/analyses", {
    cache: "no-store",
  });
}

export function streamAnalysis(
  id: string,
  onEvent: (event: StreamEvent) => void,
  onError?: (error: Event) => void,
) {
  const source = new EventSource(apiUrl(`/api/analysis/${id}/stream`));

  source.onmessage = (event) => {
    const parsed = JSON.parse(event.data) as StreamEvent;
    onEvent(parsed);
  };

  source.onerror = (error) => {
    onError?.(error);
  };

  return () => source.close();
}
