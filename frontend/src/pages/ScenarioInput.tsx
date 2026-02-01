import { useState } from "react";
import Button from "../components/Button";
import InputField from "../components/InputField";
import { submitScenario } from "../services/scenarioService";

const ScenarioInput = () => {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [riskType, setRiskType] = useState("");

  const handleSubmit = async () => {
    try {
      await submitScenario({
        name,
        description,
        riskType,
      });
  
      alert("Scenario submitted successfully");
    } catch (error) {
      alert("Submission failed");
    }
  };
  

  return (
    <div style={{ padding: "24px", maxWidth: "600px" }}>
      <h1>Create Scenario</h1>
      <p>Manually enter a financial scenario for analysis.</p>

      <InputField
        label="Scenario Name"
        value={name}
        onChange={(value) => setName(value)}
        placeholder="e.g. Interest Rate Shock"
      />

      <InputField
        label="Description"
        value={description}
        onChange={(value) => setDescription(value)}
        placeholder="Describe the scenario"
      />

      <InputField
        label="Risk Type"
        value={riskType}
        onChange={(value) => setRiskType(value)}
        placeholder="Credit / Market / Liquidity"
      />

      <div style={{ marginTop: "16px" }}>
        <Button onClick={handleSubmit}>Submit</Button>
      </div>
    </div>
  );
};

export default ScenarioInput;
