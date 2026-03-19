import { AnalysisForm } from "@/components/AnalysisForm";

export default function AnalyzePage() {
  return (
    <main className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold tracking-tight">New Analysis</h1>
      <p className="mt-2 text-sm text-zinc-300">
        Phase 1: Observe and Recommend. Ingest codebase and logs, detect root cause, and generate a structured fix recommendation.
      </p>
      <div className="mt-6">
        <AnalysisForm />
      </div>
    </main>
  );
}
