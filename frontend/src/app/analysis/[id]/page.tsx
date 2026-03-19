"use client";

import { useEffect, useRef } from "react";
import { useParams } from "next/navigation";
import { DiagnosisStream } from "@/components/DiagnosisStream";
import { ErrorCard } from "@/components/ErrorCard";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { getAnalysis, streamAnalysis } from "@/lib/api";
import { useAnalysisStore } from "@/lib/store";

import { Skeleton } from "@/components/ui/skeleton";

export default function AnalysisDetailPage() {
  const params = useParams<{ id: string }>();
  const analysisId = params.id;
  const initializedForId = useRef<string | null>(null);
  const closeStreamRef = useRef<(() => void) | null>(null);

  const analysis = useAnalysisStore((state) => state.analyses[analysisId]);
  const stageMap = useAnalysisStore((state) => state.stageByAnalysis[analysisId]);
  const stages = stageMap ?? {};
  const diagnosis = useAnalysisStore((state) => state.liveDiagnosisByAnalysis[analysisId] ?? null);
  const selectedErrorId = useAnalysisStore((state) => state.selectedErrorIdByAnalysis[analysisId]);
  const upsertAnalysis = useAnalysisStore((state) => state.upsertAnalysis);
  const selectError = useAnalysisStore((state) => state.selectError);
  const applyStreamEvent = useAnalysisStore((state) => state.applyStreamEvent);

  useEffect(() => {
    if (!analysisId) {
      return;
    }

    if (initializedForId.current === analysisId) {
      return;
    }
    initializedForId.current = analysisId;

    let cancelled = false;

    const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

    const getAnalysisWithRetry = async () => {
      let lastError: unknown;
      for (let attempt = 0; attempt < 8; attempt += 1) {
        try {
          return await getAnalysis(analysisId);
        } catch (error) {
          lastError = error;
          await wait(250);
        }
      }
      throw lastError;
    };

    const load = async () => {
      const result = await getAnalysisWithRetry();
      if (cancelled) {
        return;
      }
      upsertAnalysis(result);
      const currentSelected = useAnalysisStore.getState().selectedErrorIdByAnalysis[analysisId];
      if (result.errors.length && currentSelected !== result.errors[0].id) {
        selectError(analysisId, result.errors[0].id);
      }

      closeStreamRef.current?.();
      closeStreamRef.current = streamAnalysis(
        analysisId,
        (event) => {
          applyStreamEvent(analysisId, event);
        },
        () => {
          // No-op, polling is handled by full analysis refreshes.
        },
      );
    };

    load().catch(() => {
      // errors are handled by route error boundary
    });

    return () => {
      cancelled = true;
      closeStreamRef.current?.();
      closeStreamRef.current = null;
      initializedForId.current = null;
    };
  }, [analysisId, applyStreamEvent, selectError, upsertAnalysis]);

  if (!analysis) {
    return <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">Loading analysis...</main>;
  }

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <h1 className="text-2xl font-bold tracking-tight">Analysis {analysis.id.slice(0, 8)}</h1>
        <Badge variant={analysis.status === "completed" ? "success" : analysis.status === "failed" ? "error" : "primary"}>
          {analysis.status}
        </Badge>
      </div>

      <div className="grid gap-4 lg:grid-cols-5">
        <Card className="glass max-h-[75vh] overflow-y-auto p-3 lg:col-span-2">
          <h2 className="mb-3 px-1 text-sm font-semibold uppercase tracking-wide text-muted">Error Feed</h2>
          <div className="space-y-3">
            {analysis.errors.map((entry) => (
              <ErrorCard
                key={entry.id}
                error={entry}
                selected={selectedErrorId === entry.id}
                onClick={() => selectError(analysisId, entry.id)}
              />
            ))}
            {analysis.status === "running" && !analysis.errors.length ? (
              <div className="space-y-3">
                <Skeleton className="h-24 w-full rounded-lg" />
                <Skeleton className="h-24 w-full rounded-lg" />
                <Skeleton className="h-24 w-full rounded-lg" />
              </div>
            ) : !analysis.errors.length ? (
              <p className="p-2 text-sm text-muted">No errors indexed yet.</p>
            ) : null}
          </div>
        </Card>

        <div className="lg:col-span-3">
          <DiagnosisStream diagnosis={diagnosis} stages={stages} repoUrl={analysis.repo} />
        </div>
      </div>
    </main>
  );
}
