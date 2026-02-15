import { Navigate, Routes, Route } from "react-router-dom";
import LoginPage from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import ScenarioInput from "./pages/ScenarioInput";
import ScenarioUpload from "./pages/ScenarioUpload";
import ScenarioResult from "./pages/ScenarioResult";
import HistoricalCases from "./pages/HistoricalCases";
import AuditLogs from "./pages/AuditLogs";
import AppLayout from "./components/AppLayout";
import RequireAuth from "./components/RequireAuth";
import RequireAdmin from "./components/RequireAdmin";

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<RequireAuth />}>
        <Route element={<AppLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="scenarios">
            <Route path="new" element={<ScenarioInput />} />
            <Route path="upload" element={<ScenarioUpload />} />
            <Route path=":id/result" element={<ScenarioResult />} />
          </Route>
          <Route path="historical-cases" element={<HistoricalCases />} />
          <Route path="admin" element={<RequireAdmin />}>
            <Route index element={<Navigate to="/admin/audit-logs" replace />} />
            <Route path="audit-logs" element={<AuditLogs />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

export default App;
