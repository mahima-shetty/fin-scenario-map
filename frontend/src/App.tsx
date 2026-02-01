import { Routes, Route } from "react-router-dom";
import LoginPage from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import ScenarioInput from "./pages/ScenarioInput";
import ScenarioUpload from "./pages/ScenarioUpload";

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<Dashboard />} />
      <Route path="/scenarios/new" element={<ScenarioInput />} />
      <Route path="/scenarios/upload" element={<ScenarioUpload />} />
    </Routes>
  );
}

export default App;
