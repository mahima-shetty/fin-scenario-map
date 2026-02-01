import { LoginRequest, LoginResponse } from "../types/auth";

export async function loginUser(data: LoginRequest): Promise<LoginResponse> {
  const res = await fetch("http://127.0.0.1:8000/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  const responseData: LoginResponse = await res.json();
  return responseData;
}
