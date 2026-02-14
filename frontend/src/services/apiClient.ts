import axios from "axios";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30_000,
  headers: {
    Accept: "application/json",
  },
});

/** Longer timeout for scenario submit (dataset + workflow can be slow on first run). */
export const SCENARIO_SUBMIT_TIMEOUT_MS = 90_000;

export type ApiError = {
  message: string;
  status?: number;
  data?: unknown;
};

export function toApiError(error: unknown): ApiError {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;
    const data = error.response?.data;

    const message =
      typeof data === "string"
        ? data
        : typeof (data as { message?: unknown } | undefined)?.message ===
          "string"
        ? (data as { message: string }).message
        : error.message || "Request failed";

    return { message, status, data };
  }

  if (error instanceof Error) {
    return { message: error.message };
  }

  return { message: "Unknown error" };
}
