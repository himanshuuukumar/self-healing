"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { getAnalyses } from "@/lib/api";
import { useAnalysisStore } from "@/lib/store";
import { repoNameFromUrl } from "@/lib/utils";

export default function HistoryPage() {
  const [filter, setFilter] = useState("");
  const analysesMap = useAnalysisStore((state) => state.analyses);
  const setAnalyses = useAnalysisStore((state) => state.setAnalyses);

  useEffect(() => {
    getAnalyses()
      .then((data) => setAnalyses(data))
      .catch(() => {
        // handled by route error boundary in runtime failures
      });
  }, [setAnalyses]);

  const analyses = useMemo(
    () =>
      Object.values(analysesMap)
        .filter((item) => repoNameFromUrl(item.repo).toLowerCase().includes(filter.toLowerCase()))
        .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()),
    [analysesMap, filter],
  );

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analysis History</h1>
          <p className="mt-1 text-sm text-zinc-300">Inspect completed and running autonomous debugging sessions.</p>
        </div>
        <Input
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          placeholder="Filter by repo name"
          className="w-full sm:w-72"
        />
      </div>

      <Card className="glass overflow-hidden">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Repo</TableHead>
                <TableHead>Timestamp</TableHead>
                <TableHead>Errors Found</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {analyses.map((analysis) => (
                <TableRow key={analysis.id}>
                  <TableCell>
                    <Link href={`/analysis/${analysis.id}`} className="font-medium text-violet-300 hover:underline">
                      {repoNameFromUrl(analysis.repo)}
                    </Link>
                  </TableCell>
                  <TableCell>{new Date(analysis.created_at).toLocaleString()}</TableCell>
                  <TableCell>{analysis.errors.length}</TableCell>
                  <TableCell>
                    <Badge
                      variant={
                        analysis.status === "completed" ? "success" : analysis.status === "failed" ? "error" : "warning"
                      }
                    >
                      {analysis.status === "running" ? "Running" : analysis.status === "completed" ? "Completed" : "Failed"}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
              {!analyses.length ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-muted">
                    No analyses found.
                  </TableCell>
                </TableRow>
              ) : null}
            </TableBody>
          </Table>
        </div>
      </Card>
    </main>
  );
}
