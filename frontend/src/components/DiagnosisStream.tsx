"use client";

import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { ExternalLink } from "lucide-react";
import { CodeDiff } from "@/components/CodeDiff";
import { StageIndicator } from "@/components/StageIndicator";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { DiagnosisResult, StageStatus, StreamStage } from "@/lib/types";
import { githubBlobUrl } from "@/lib/utils";

interface DiagnosisStreamProps {
  diagnosis: DiagnosisResult | null;
  stages: Partial<Record<StreamStage, StageStatus>>;
  repoUrl: string;
}

export function DiagnosisStream({ diagnosis, stages, repoUrl }: DiagnosisStreamProps) {
  const [animatedConfidence, setAnimatedConfidence] = useState(0);

  useEffect(() => {
    const target = diagnosis?.confidence ?? 0;
    let frame: number;
    const step = () => {
      setAnimatedConfidence((prev) => {
        const next = prev + (target - prev) * 0.12;
        if (Math.abs(target - next) < 0.5) {
          return target;
        }
        frame = requestAnimationFrame(step);
        return next;
      });
    };

    frame = requestAnimationFrame(step);
    return () => cancelAnimationFrame(frame);
  }, [diagnosis?.confidence]);

  const rootCause = diagnosis?.root_cause ?? "Waiting for streamed diagnosis output...";
  const githubUrl = diagnosis
    ? githubBlobUrl(repoUrl, diagnosis.affected_file, diagnosis.affected_line)
    : "#";

  const stageRows = useMemo(
    () => [
      { key: "fetching_logs" as StreamStage, label: "Stage 1 - Fetching Logs" },
      { key: "retrieving_code" as StreamStage, label: "Stage 2 - Retrieving Code" },
      { key: "diagnosing" as StreamStage, label: "Stage 3 - Diagnosing" },
      { key: "generating_fix" as StreamStage, label: "Stage 4 - Generating Fix" },
    ],
    [],
  );

  return (
    <div className="glass rounded-xl p-4 sm:p-5">
      <div className="grid gap-2">
        {stageRows.map((stage) => (
          <StageIndicator key={stage.key} label={stage.label} status={stages[stage.key] ?? "idle"} />
        ))}
      </div>

      <div className="mt-6 space-y-5">
        <section>
          <p className="mb-2 text-xs uppercase tracking-wide text-muted">Root Cause</p>
          <motion.p
            key={rootCause}
            initial={{ opacity: 0.4 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.35 }}
            className="rounded-lg border border-border bg-zinc-950 p-3 text-sm leading-6"
          >
            {rootCause}
          </motion.p>
        </section>

        <section>
          <p className="mb-2 text-xs uppercase tracking-wide text-muted">Affected File</p>
          <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-border bg-zinc-950 p-3">
            <p className="font-mono text-xs text-zinc-300">
              {diagnosis?.affected_file ?? "N/A"} - line {diagnosis?.affected_line ?? "-"}
            </p>
            <a href={githubUrl} target="_blank" rel="noreferrer">
              <Button size="sm" variant="outline" disabled={!diagnosis}>
                <ExternalLink className="mr-1 h-4 w-4" /> View in GitHub
              </Button>
            </a>
          </div>
        </section>

        <section>
          <p className="mb-2 text-xs uppercase tracking-wide text-muted">Suggested Fix</p>
          <CodeDiff before={diagnosis?.fix_suggestion.before ?? ""} after={diagnosis?.fix_suggestion.after ?? ""} />
          {diagnosis?.fix_suggestion.explanation ? (
            <div className="mt-4 rounded-md bg-zinc-900 p-3 text-sm text-zinc-300 whitespace-pre-wrap font-mono">
              {diagnosis.fix_suggestion.explanation}
            </div>
          ) : null}
        </section>

        <section>
          <p className="mb-2 text-xs uppercase tracking-wide text-muted">Confidence</p>
          <div className="rounded-lg border border-border bg-zinc-950 p-3">
            <Progress value={animatedConfidence} />
            <p className="mt-2 text-right font-mono text-sm text-zinc-300">{Math.round(animatedConfidence)}%</p>
          </div>
        </section>
      </div>
    </div>
  );
}
