import { Navigate, Outlet } from "react-router-dom";
import { getAuthState } from "../services/authStorage";

export default function RequireAdmin() {
  const auth = getAuthState();

  if (!auth.isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  if (auth.role !== "admin") {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}
