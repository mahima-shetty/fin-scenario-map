const AUTH_KEY = "fsm_auth";

type AuthState = {
  isAuthenticated: boolean;
  email?: string;
};

export function getAuthState(): AuthState {
  try {
    const raw = localStorage.getItem(AUTH_KEY);
    if (!raw) return { isAuthenticated: false };
    const parsed = JSON.parse(raw) as Partial<AuthState>;
    return {
      isAuthenticated: parsed.isAuthenticated === true,
      email: typeof parsed.email === "string" ? parsed.email : undefined,
    };
  } catch {
    return { isAuthenticated: false };
  }
}

export function isAuthenticated(): boolean {
  return getAuthState().isAuthenticated;
}

export function signIn(email: string) {
  const state: AuthState = { isAuthenticated: true, email };
  localStorage.setItem(AUTH_KEY, JSON.stringify(state));
}

export function signOut() {
  localStorage.removeItem(AUTH_KEY);
}

