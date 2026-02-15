import { apiClient, SCENARIO_SUBMIT_TIMEOUT_MS } from "./apiClient";
import type {
  HistoricalCasesResponse,
  RecentScenariosResponse,
  ScenarioResultResponse,
  ScenarioSubmitRequest,
  ScenarioSubmitResponse,
  ScenarioUploadResponse,
} from "../types/scenario";

export async function submitScenario(
  data: ScenarioSubmitRequest
): Promise<ScenarioSubmitResponse> {
  const response = await apiClient.post<ScenarioSubmitResponse>(
    "/api/scenarios/input",
    data,
    { timeout: SCENARIO_SUBMIT_TIMEOUT_MS }
  );
  return response.data;
}

export async function uploadScenario(
  file: File
): Promise<ScenarioUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await apiClient.post<ScenarioUploadResponse>(
    "/api/scenarios/upload",
    formData,
    {
      headers: { "Content-Type": "multipart/form-data" },
    }
  );

  return response.data;
}

export async function fetchScenarioResult(
  id: string
): Promise<ScenarioResultResponse> {
  const response = await apiClient.get<ScenarioResultResponse>(
    `/api/scenarios/${encodeURIComponent(id)}/result`
  );
  return response.data;
}

export async function fetchHistoricalCases(): Promise<HistoricalCasesResponse> {
  const response = await apiClient.get<HistoricalCasesResponse>(
    "/api/historical-cases"
  );
  return response.data;
}

export async function fetchRecentScenarios(
  limit: number = 20
): Promise<RecentScenariosResponse> {
  const response = await apiClient.get<RecentScenariosResponse>(
    "/api/scenarios/recent",
    { params: { limit } }
  );
  return response.data;
}
