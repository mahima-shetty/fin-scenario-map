import { useState } from "react";
import Button from "../components/Button";
import InputField from "../components/InputField";
import { submitScenario } from "../services/scenarioService";

const ScenarioInput = () => {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [riskType, setRiskType] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    try {
      setSubmitting(true);
      await submitScenario({
        name,
        description,
        riskType,
      });
  
      alert("Scenario submitted successfully");
    } catch (error) {
      alert("Submission failed");
    } finally {
      setSubmitting(false);
    }
  };
  

  return (
    <div>
      <div style={{ marginBottom: 12 }}>
        <h1>Create scenario</h1>
        <p>Capture a scenario with consistent metadata and submit for analysis.</p>
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

            <div style={{ display: "flex", gap: 10, alignItems: "center", marginTop: 4 }}>
              <Button disabled={submitting || !name || !riskType} onClick={() => void handleSubmit()}>
                {submitting ? "Submitting..." : "Submit scenario"}
              </Button>
              <span className="helper">Backend endpoint currently returns 404 until implemented.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScenarioInput;
