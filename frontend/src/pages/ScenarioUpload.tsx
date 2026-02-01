import { useState } from "react";
import Button from "../components/Button";

const ScenarioUpload = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
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

  setFile(selectedFile);
};

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file first");
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(
        "http://127.0.0.1:8000/api/scenarios/upload",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      alert("Scenario uploaded successfully");
      setFile(null);
    } catch (error) {
      alert("Upload error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: 12 }}>
        <h1>Upload scenario</h1>
        <p>Upload a scenario file for ingestion (CSV/Excel/PDF can be supported later).</p>
      </div>

      <div className="card" style={{ maxWidth: 760 }}>
        <div className="cardBody">
          <div className="form">
            <div>
              <label className="fieldLabel">Scenario file</label>
              <input type="file" accept=".csv,.json,.pdf" onChange={handleFileChange} className="input" />
              <div className="helper">
                {file ? (
                  <span>
                    Selected: <span style={{ fontWeight: 700 }}>{file.name}</span>{" "}
                    <span style={{ color: "rgba(226, 232, 240, 0.62)" }}>
                      ({Math.ceil(file.size / 1024)} KB)
                    </span>
                  </span>
                ) : (
                  "Choose a file to upload."
                )}
              </div>
            </div>

            <div style={{ display: "flex", gap: 10, alignItems: "center", marginTop: 4 }}>
              <Button disabled={loading || !file} onClick={() => void handleUpload()}>
                {loading ? "Uploading..." : "Upload scenario"}
              </Button>
              <span className="helper">Backend endpoint currently returns 404 until implemented.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScenarioUpload;
