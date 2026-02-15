export interface ScenarioSubmitRequest {
  name: string;
  description: string;
  riskType: string;
}

// Matches current backend response in `backend/main.py`
export interface ScenarioSubmitResponse {
  status: string;
  data: Record<string, unknown>;
}

// Matches current backend response in `backend/main.py`
export interface ScenarioUploadResponse {
  filename: string;
  content_type?: string | null;
  size_bytes?: number;
  scenario_ids: string[];
}

/** One reference case from GET /api/historical-cases */
export interface HistoricalCase {
  id: string;
  name: string;
  issueDescription: string;
  impact: string;
  recommendations: string[];
  riskType: string;
}

export interface HistoricalCasesResponse {
  cases: HistoricalCase[];
}

/** One row from GET /api/scenarios/recent */
export interface RecentScenario {
  id: string;
  name: string;
  risk: string;
  createdAt: string;
  status: string;
}

export interface RecentScenariosResponse {
  scenarios: RecentScenario[];
}

/** One workflow step from backend step_log (step, status, ts, detail?). */
export interface WorkflowStepEntry {
  step: string;
  status: string;
  ts?: string;
  detail?: string;
}

// Matches backend result; confidenceScore may be null when missing (UI shows NA).
export interface ScenarioResultResponse {
  scenarioName: string;
  riskType: string;
  description?: string;
  confidenceScore: number | null;
  createdAt: string;
  recommendations: string[];
  historicalCases: Array<{
    id: string;
    name: string;
    similarity: string;
  }>;
  step_log?: WorkflowStepEntry[];
}
