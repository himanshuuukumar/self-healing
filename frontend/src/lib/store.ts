import { create } from "zustand";
import { Analysis, DiagnosisResult, StageStatus, StreamEvent } from "@/lib/types";

interface StageState {
  fetching_logs: StageStatus;
  retrieving_code: StageStatus;
  diagnosing: StageStatus;
  generating_fix: StageStatus;
}

interface AnalysisState {
  analyses: Record<string, Analysis>;
  selectedErrorIdByAnalysis: Record<string, string | null>;
  stageByAnalysis: Record<string, StageState>;
  liveDiagnosisByAnalysis: Record<string, DiagnosisResult | null>;
  setAnalyses: (analyses: Analysis[]) => void;
  upsertAnalysis: (analysis: Analysis) => void;
  selectError: (analysisId: string, errorId: string) => void;
  applyStreamEvent: (analysisId: string, event: StreamEvent) => void;
}

const initialStageState: StageState = {
  fetching_logs: "idle",
  retrieving_code: "idle",
  diagnosing: "idle",
  generating_fix: "idle",
};

export const useAnalysisStore = create<AnalysisState>((set, get) => ({
  analyses: {},
  selectedErrorIdByAnalysis: {},
  stageByAnalysis: {},
  liveDiagnosisByAnalysis: {},
  setAnalyses: (analyses) => {
    const mapped = analyses.reduce<Record<string, Analysis>>((acc, analysis) => {
      acc[analysis.id] = analysis;
      return acc;
    }, {});

    set({ analyses: mapped });
  },
  upsertAnalysis: (analysis) => {
    const current = get();
    const selected = current.selectedErrorIdByAnalysis[analysis.id] ?? analysis.errors[0]?.id ?? null;
    
    let stageMap = current.stageByAnalysis[analysis.id] ?? { ...initialStageState };
    if (analysis.status === "completed") {
      stageMap = {
        fetching_logs: "completed",
        retrieving_code: "completed",
        diagnosing: "completed",
        generating_fix: "completed",
      };
    } else if (analysis.status === "failed") {
      // If failed, at least mark the first stage as failed if none are active
      if (stageMap.fetching_logs === "idle") {
        stageMap = { ...stageMap, fetching_logs: "failed" };
      }
    }

    set({
      analyses: { ...current.analyses, [analysis.id]: analysis },
      selectedErrorIdByAnalysis: {
        ...current.selectedErrorIdByAnalysis,
        [analysis.id]: selected,
      },
      liveDiagnosisByAnalysis: {
        ...current.liveDiagnosisByAnalysis,
        [analysis.id]: analysis.diagnoses[0] ?? current.liveDiagnosisByAnalysis[analysis.id] ?? null,
      },
      stageByAnalysis: {
        ...current.stageByAnalysis,
        [analysis.id]: stageMap,
      },
    });
  },
  selectError: (analysisId, errorId) => {
    const currentSelected = get().selectedErrorIdByAnalysis[analysisId];
    if (currentSelected === errorId) {
      return;
    }
    const analysis = get().analyses[analysisId];
    const diagnosis = analysis?.diagnoses.find((item) => item.error_id === errorId) ?? null;
    set((state) => ({
      selectedErrorIdByAnalysis: {
        ...state.selectedErrorIdByAnalysis,
        [analysisId]: errorId,
      },
      liveDiagnosisByAnalysis: {
        ...state.liveDiagnosisByAnalysis,
        [analysisId]: diagnosis,
      },
    }));
  },
  applyStreamEvent: (analysisId, event) => {
    const nextStage: StageStatus =
      event.status === "started" ? "running" : event.status === "completed" ? "completed" : "failed";

    set((state) => {
      // Process Errors
      let nextAnalyses = state.analyses;
      let nextSelectedErrorId = state.selectedErrorIdByAnalysis;

      if (event.data?.errors) {
        const currentAnalysis = state.analyses[analysisId];
        if (currentAnalysis) {
          const updatedAnalysis = { ...currentAnalysis, errors: event.data.errors };
          const newSelectedId = state.selectedErrorIdByAnalysis[analysisId] ?? event.data.errors[0]?.id ?? null;
          nextAnalyses = { ...state.analyses, [analysisId]: updatedAnalysis };
          nextSelectedErrorId = { ...state.selectedErrorIdByAnalysis, [analysisId]: newSelectedId };
        }
      }

      // Process Live Diagnosis
      const currentLive = state.liveDiagnosisByAnalysis[analysisId] ?? {
        error_id: nextSelectedErrorId[analysisId] ?? "",
        root_cause: "",
        affected_file: "",
        affected_line: 0,
        fix_suggestion: { before: "", after: "", explanation: "" },
        confidence: 0,
      };

      const mergedDiagnosis = event.data
        ? {
            ...currentLive,
            ...event.data,
            fix_suggestion: {
              ...currentLive.fix_suggestion,
              ...(event.data.fix_suggestion ?? {}),
            },
          }
        : currentLive;
      
      if ("errors" in mergedDiagnosis) {
        delete (mergedDiagnosis as any).errors;
      }

      // Process Stage Map (using fresh state)
      const currentStageMap = state.stageByAnalysis[analysisId] ?? { ...initialStageState };
      
      return {
        analyses: nextAnalyses,
        selectedErrorIdByAnalysis: nextSelectedErrorId,
        stageByAnalysis: {
          ...state.stageByAnalysis,
          [analysisId]: {
            ...currentStageMap,
            [event.stage]: nextStage,
          },
        },
        liveDiagnosisByAnalysis: {
          ...state.liveDiagnosisByAnalysis,
          [analysisId]: mergedDiagnosis as DiagnosisResult,
        },
      };
    });
  },
}));
