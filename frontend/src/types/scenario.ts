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
}
