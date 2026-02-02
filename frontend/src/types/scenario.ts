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

// For future result endpoint wiring.
export interface ScenarioResultResponse {
  scenarioName: string;
  riskType: string;
  confidenceScore: number;
  createdAt: string;
  recommendations: string[];
  historicalCases: Array<{
    id: string;
    name: string;
    similarity: string;
  }>;
}
