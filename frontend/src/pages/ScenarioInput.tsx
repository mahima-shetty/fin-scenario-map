import { useState } from "react";
import { Link } from "react-router-dom";
import Button from "../components/Button";
import InputField from "../components/InputField";
import { submitScenario } from "../services/scenarioService";
import { toApiError } from "../services/apiClient";

const ScenarioInput = () => {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [riskType, setRiskType] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [lastScenarioId, setLastScenarioId] = useState<string | null>(null);

  const handleSubmit = async () => {
    try {
      setSubmitting(true);
      setError("");
      setSuccess("");
      setLastScenarioId(null);
      const response = await submitScenario({
        name,
        description,
        riskType,
      });

      const scenarioId = response?.data?.scenario_id;
      if (typeof scenarioId === "string") {
        setLastScenarioId(scenarioId);
        try {
          sessionStorage.setItem(
            `scenario_input_${scenarioId}`,
            JSON.stringify({
              scenarioName: name.trim() || "NA",
              riskType: riskType.trim() || "NA",
              description: description?.trim() || "",
              createdAt: new Date().toISOString().slice(0, 10),
            })
          );
        } catch {
          // ignore storage errors
        }
      }
      setSuccess("Scenario submitted successfully.");
      setName("");
      setDescription("");
      setRiskType("");
    } catch (err) {
      setError(toApiError(err).message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: 12 }}>
        <h1>Create scenario</h1>
        <p>
          Capture a scenario with consistent metadata and submit for analysis.
        </p>
      </div>

      <div className="card" style={{ maxWidth: 760 }}>
        <div className="cardBody">
          <div className="form">
            <InputField
              label="Scenario name"
              value={name}
              onChange={(value) => setName(value)}
              placeholder="e.g. Interest Rate Shock"
              helperText="Use a short, audit-friendly title."
              required
            />

            <InputField
              label="Description"
              value={description}
              onChange={(value) => setDescription(value)}
              placeholder="Describe triggers, assumptions, and expected impacts"
              helperText="Keep it specific enough for reviewers and model owners."
            />

            <InputField
              label="Risk type"
              value={riskType}
              onChange={(value) => setRiskType(value)}
              placeholder="Credit / Market / Liquidity"
              helperText="Helps route workflows, approvals, and reporting."
              required
            />

            {error ? <div className="error">{error}</div> : null}
            {success ? <div className="badge badgeOk">{success}</div> : null}
            {lastScenarioId ? (
              <div style={{ marginTop: 8 }}>
                <span className="helper">Scenario ID: </span>
                <span style={{ fontWeight: 700, color: "rgba(241, 245, 249, 0.92)" }}>
                  {lastScenarioId}
                </span>
                {" · "}
                <Link to={`/scenarios/${lastScenarioId}/result`} style={{ color: "var(--accent)" }}>
                  View result
                </Link>
              </div>
            ) : null}

            <div
              style={{
                display: "flex",
                gap: 10,
                alignItems: "center",
                marginTop: 4,
              }}
            >
              <Button
                disabled={submitting || !name || !riskType}
                onClick={() => void handleSubmit()}
              >
                {submitting ? "Submitting..." : "Submit scenario"}
              </Button>
              <span className="helper">Posts to `/api/scenarios/input`.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScenarioInput;
