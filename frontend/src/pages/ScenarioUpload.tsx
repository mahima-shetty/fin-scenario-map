import { useState } from "react";
import Button from "../components/Button";
import { uploadScenario } from "../services/scenarioService";
import { toApiError } from "../services/apiClient";

const ScenarioUpload = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 MB

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;

    const selectedFile = e.target.files[0];

    const allowedTypes = ["text/csv", "application/pdf", "application/json"];

    if (!allowedTypes.includes(selectedFile.type)) {
      alert("Only CSV, PDF or JSON files are allowed");
      return;
    }

    if (selectedFile.size > MAX_FILE_SIZE) {
      alert("File size must be less than 5MB");
      return;
    }

    setError("");
    setSuccess("");
    setFile(selectedFile);
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file first");
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const res = await uploadScenario(file);
      setSuccess(`Uploaded successfully: ${res.filename}`);
      setFile(null);
    } catch (error) {
      setError(toApiError(error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: 12 }}>
        <h1>Upload scenario</h1>
        <p>
          Upload a scenario file for ingestion (CSV/Excel/PDF can be supported
          later).
        </p>
      </div>

      <div className="card" style={{ maxWidth: 760 }}>
        <div className="cardBody">
          <div className="form">
            <div>
              <label className="fieldLabel">Scenario file</label>
              <input
                type="file"
                accept=".csv,.json,.pdf"
                onChange={handleFileChange}
                className="input"
              />
              <div className="helper">
                {file ? (
                  <span>
                    Selected:{" "}
                    <span style={{ fontWeight: 700 }}>{file.name}</span>{" "}
                    <span style={{ color: "rgba(226, 232, 240, 0.62)" }}>
                      ({Math.ceil(file.size / 1024)} KB)
                    </span>
                  </span>
                ) : (
                  "Choose a file to upload."
                )}
              </div>
            </div>

            {error ? <div className="error">{error}</div> : null}
            {success ? <div className="badge badgeOk">{success}</div> : null}

            <div
              style={{
                display: "flex",
                gap: 10,
                alignItems: "center",
                marginTop: 4,
              }}
            >
              <Button
                disabled={loading || !file}
                onClick={() => void handleUpload()}
              >
                {loading ? "Uploading..." : "Upload scenario"}
              </Button>
              <span className="helper">Posts to `/api/scenarios/upload`.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScenarioUpload;
