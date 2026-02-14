// src/pages/Login.tsx
import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import InputField from "../components/InputField";
import Button from "../components/Button";
import { loginUser } from "../services/authService";
import { isAuthenticated, signIn } from "../services/authStorage";
import { toApiError } from "../services/apiClient";

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isAuthenticated()) {
      navigate("/", { replace: true });
    }
  }, [navigate]);

  const handleLogin = async () => {
    try {
      setLoading(true);
      const res = await loginUser({ email, password });
      if (res.success) {
        signIn(email);
        const from = (location.state as { from?: string } | null)?.from;
        navigate(from || "/", { replace: true });
      } else {
        setError(res.message);
      }
    } catch (err) {
      setError(toApiError(err).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="authWrap">
      <div className="card authCard">
        <div className="cardBody">
          <div className="authHeader">
            <div>
              <h1 style={{ marginBottom: 4 }}>Sign in</h1>
              <p style={{ marginBottom: 0 }}>
                Access your scenario workspace with a secure banking-style
                interface.
              </p>
            </div>
            <div
              className="brandMark"
              aria-hidden="true"
              style={{ width: 48, height: 48 }}
            >
              <svg
                width="22"
                height="22"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="M4 19V9" />
                <path d="M9 19V5" />
                <path d="M14 19v-7" />
                <path d="M19 19V11" />
              </svg>
            </div>
          </div>

          <div className="form" style={{ marginTop: 14 }}>
            <InputField
              label="Email"
              value={email}
              onChange={(value) => setEmail(value)}
              placeholder="name@bank.com"
            />
            <InputField
              label="Password"
              type="password"
              value={password}
              onChange={(value) => setPassword(value)}
              placeholder="••••••••"
            />

            {error ? <div className="error">{error}</div> : null}

            <div
              style={{
                display: "flex",
                gap: 10,
                alignItems: "center",
                marginTop: 4,
              }}
            >
              <Button
                disabled={loading || !email || !password}
                onClick={() => void handleLogin()}
              >
                {loading ? "Signing in..." : "Sign in"}
              </Button>
              <span className="helper">
                Demo auth only.
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
