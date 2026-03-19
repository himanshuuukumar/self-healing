"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { startAnalysis } from "@/lib/api";
import { useAnalysisStore } from "@/lib/store";
import { Analysis } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

const analysisSchema = z.object({
  github_url: z
    .string()
    .min(1, "Repo URL is required")
    .refine(
      (value) => value === "demo://quickcart" || value === "local://quickcart" || value.startsWith("https://github.com/"),
      "Use https://github.com/..., demo://quickcart, or local://quickcart",
    ),
  github_token: z.string(),
  mongo_uri: z.string(),
  mongo_db: z.string(),
  mongo_collection: z.string(),
});

type AnalysisFormValues = z.infer<typeof analysisSchema>;

export function AnalysisForm() {
  const router = useRouter();
  const upsertAnalysis = useAnalysisStore((state) => state.upsertAnalysis);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<AnalysisFormValues>({
    resolver: zodResolver(analysisSchema),
    defaultValues: {
      github_url: "demo://quickcart",
      github_token: "ghp_demo_token",
      mongo_uri: "",
      mongo_db: "",
      mongo_collection: "",
    },
  });

  const onSubmit = async (values: AnalysisFormValues) => {
    setSubmitError(null);
    try {
      const payload = {
        github_url: values.github_url,
        github_token: values.github_token || "ghp_demo_token",
        mongo_uri: values.mongo_uri || "",
        mongo_db: values.mongo_db || "",
        mongo_collection: values.mongo_collection || "",
      };
      const response = await startAnalysis(payload);
      const optimistic: Analysis = {
        id: response.analysis_id,
        repo: payload.github_url,
        status: "running",
        created_at: new Date().toISOString(),
        errors: [],
        diagnoses: [],
      };

      upsertAnalysis(optimistic);
      router.push(`/analysis/${response.analysis_id}`);
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : "Failed to start analysis");
    }
  };

  const runDemoAnalysis = async () => {
    setSubmitError(null);
    try {
      const payload = {
        github_url: "demo://quickcart",
        github_token: "ghp_demo_token",
        mongo_uri: "",
        mongo_db: "",
        mongo_collection: "",
      };
      const response = await startAnalysis(payload);
      upsertAnalysis({
        id: response.analysis_id,
        repo: payload.github_url,
        status: "running",
        created_at: new Date().toISOString(),
        errors: [],
        diagnoses: [],
      });
      router.push(`/analysis/${response.analysis_id}`);
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : "Failed to start analysis");
    }
  };

  const errorFor = (field: keyof AnalysisFormValues) => errors[field]?.message;

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <Card className="glass">
        <CardHeader>
          <CardTitle>Section 1 - Repository</CardTitle>
          <CardDescription>Provide source access so Proctor can clone and index your codebase.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4">
          <div className="space-y-2">
            <label className="text-sm">GitHub Repo URL</label>
            <Input
              placeholder="https://github.com/owner/repo or demo://quickcart"
              {...register("github_url")}
              className={errorFor("github_url") ? "border-error focus-visible:ring-error" : ""}
            />
            {errorFor("github_url") ? <p className="text-xs text-error font-medium">{errorFor("github_url")}</p> : null}
            <p className="text-xs text-muted">Quick demo: use demo://quickcart</p>
          </div>
          <div className="space-y-2">
            <label className="text-sm">GitHub Personal Access Token</label>
            <Input type="password" placeholder="ghp_..." {...register("github_token")} />
            <p className="text-xs text-muted">Optional for demo/public repos.</p>
          </div>
        </CardContent>
      </Card>

      <Card className="glass">
        <CardHeader>
          <CardTitle>Section 2 - Logs</CardTitle>
          <CardDescription>Point to MongoDB logs used for error extraction (optional in demo mode).</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2 sm:col-span-2">
            <label className="text-sm">MongoDB Connection String</label>
            <Input type="password" placeholder="mongodb+srv://..." {...register("mongo_uri")} />
            <p className="text-xs text-muted">Leave empty to use local demo logs.</p>
          </div>
          <div className="space-y-2">
            <label className="text-sm">MongoDB Database Name</label>
            <Input placeholder="quickcart" {...register("mongo_db")} />
          </div>
          <div className="space-y-2">
            <label className="text-sm">MongoDB Collection Name</label>
            <Input placeholder="logs" {...register("mongo_collection")} />
          </div>
        </CardContent>
      </Card>

      <Card className="glass">
        <CardHeader>
          <CardTitle>Ready To Analyze</CardTitle>
          <CardDescription>Run analysis using repository and log configuration.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4" />
      </Card>

      <div className="flex flex-col gap-3 sm:flex-row">
        <Button size="lg" className="w-full sm:w-auto" disabled={isSubmitting}>
          {isSubmitting ? "Initializing..." : "Run Analysis"}
        </Button>
        <Button type="button" size="lg" variant="outline" className="w-full sm:w-auto" onClick={runDemoAnalysis}>
          Run Demo Analysis
        </Button>
      </div>
      {submitError ? <p className="text-sm text-error">{submitError}</p> : null}
    </form>
  );
}
