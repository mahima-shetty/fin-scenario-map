import { LoginRequest, LoginResponse } from "../types/auth";
import { apiClient } from "./apiClient";

export async function loginUser(data: LoginRequest): Promise<LoginResponse> {
  const res = await apiClient.post<LoginResponse>("/login", data);
  return res.data;
}
