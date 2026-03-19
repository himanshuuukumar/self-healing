"use client";

import { Badge } from "@/components/ui/badge";
import { ErrorEntry } from "@/lib/types";
import { cn } from "@/lib/utils";

interface ErrorCardProps {
  error: ErrorEntry;
  selected: boolean;
  onClick: () => void;
}

export function ErrorCard({ error, selected, onClick }: ErrorCardProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "w-full rounded-lg border p-3 text-left transition-colors",
        selected ? "border-primary bg-violet-500/10" : "border-border bg-zinc-950 hover:bg-zinc-900",
      )}
    >
      <div className="mb-2 flex items-center justify-between gap-2">
        <Badge variant={error.level === "ERROR" ? "error" : "warning"}>{error.error.split(":")[0]}</Badge>
        <span className="text-xs text-muted">{new Date(error.timestamp).toLocaleString()}</span>
      </div>
      <p className="text-sm font-semibold">{error.service}</p>
      <p className="font-mono text-xs text-muted">
        {error.file}:{error.line}
      </p>
      <p className="mt-2 line-clamp-2 text-xs text-zinc-300">{error.error}</p>
    </button>
  );
}
