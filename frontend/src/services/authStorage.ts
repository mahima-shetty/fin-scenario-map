const AUTH_KEY = "fsm_auth";

export type AuthState = {
  isAuthenticated: boolean;
  email?: string;
  role?: string;
};

export function getAuthState(): AuthState {
  try {
    const raw = localStorage.getItem(AUTH_KEY);
    if (!raw) return { isAuthenticated: false };
    const parsed = JSON.parse(raw) as Partial<AuthState & { token?: string }>;
    const hasToken = typeof parsed.token === "string" && parsed.token.length > 0;
    return {
      isAuthenticated: hasToken,
      email: typeof parsed.email === "string" ? parsed.email : undefined,
      role: typeof parsed.role === "string" ? parsed.role : undefined,
    };
  } catch {
    return { isAuthenticated: false };
  }
}

export function getToken(): string | null {
  try {
    const raw = localStorage.getItem(AUTH_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as { token?: string };
    return typeof parsed.token === "string" ? parsed.token : null;
  } catch {
    return null;
  }
}

export function isAuthenticated(): boolean {
  return !!getToken();
}

export function signIn(accessToken: string, email: string, role?: string) {
  localStorage.setItem(
    AUTH_KEY,
    JSON.stringify({ token: accessToken, email, role: role ?? "user" }),
  );
}

export function signOut() {
  localStorage.removeItem(AUTH_KEY);
}

