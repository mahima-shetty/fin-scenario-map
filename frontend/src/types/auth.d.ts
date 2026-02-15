export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  success: boolean;
  message: string;
  access_token?: string;
  token_type?: string;
  role?: string;
}

export type Role = "user" | "admin";
