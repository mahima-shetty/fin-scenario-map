// src/pages/LoginPage.tsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import InputField from "../components/InputField";
import Button from "../components/Button";
import { loginUser } from "../services/authService";

export default function LoginPage() {
  const navigate = useNavigate();  // <-- initialize here
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async () => {
    try {
      const res = await loginUser({ email, password });
      if (res.success) {
        // ✅ redirect on successful login
        navigate("/");  
      } else {
        setError(res.message);
      }
    } catch (err) {
      setError("Something went wrong");
    }
  };

  return (
    <div>
      <h1>Login</h1>
      <InputField
        label="Email"
        value={email}
        onChange={(value) => setEmail(value)}
      />
      <InputField
        label="Password"
        type="password"
        value={password}
        onChange={(value) => setPassword(value)}
      />
      <Button onClick={handleLogin}>Login</Button>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}
