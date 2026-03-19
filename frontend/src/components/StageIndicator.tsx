"use client";

import { CheckCircle2, Loader2, AlertTriangle, CircleDashed } from "lucide-react";
import { StageStatus } from "@/lib/types";
import { cn } from "@/lib/utils";

interface StageIndicatorProps {
  label: string;
  status: StageStatus;
}

export function StageIndicator({ label, status }: StageIndicatorProps) {
  return (
    <div className="flex items-center gap-3 rounded-lg border border-border bg-zinc-950/70 px-3 py-2">
      <span
        className={cn(
          "flex h-6 w-6 items-center justify-center rounded-full",
          status === "running" && "bg-primary/20 text-violet-300 pulse-dot",
          status === "completed" && "bg-emerald-500/20 text-emerald-300",
          status === "failed" && "bg-red-500/20 text-red-300",
          status === "idle" && "bg-zinc-800 text-zinc-300",
        )}
      >
        {status === "running" && <Loader2 className="h-4 w-4 animate-spin" />}
        {status === "completed" && <CheckCircle2 className="h-4 w-4" />}
        {status === "failed" && <AlertTriangle className="h-4 w-4" />}
        {status === "idle" && <CircleDashed className="h-4 w-4" />}
      </span>
      <span className="text-sm text-foreground">{label}</span>
    </div>
  );
}
