import { Routes, Route } from "react-router-dom";
import LoginPage from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import ScenarioInput from "./pages/ScenarioInput";
import ScenarioUpload from "./pages/ScenarioUpload";
import AppLayout from "./components/AppLayout";

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<AppLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/scenarios/new" element={<ScenarioInput />} />
        <Route path="/scenarios/upload" element={<ScenarioUpload />} />
      </Route>
    </Routes>
  );
}

export default App;
