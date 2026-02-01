import { useState } from "react";
import Button from "../components/Button";

const ScenarioUpload = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
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
    <div style={{ padding: "24px", maxWidth: "600px" }}>
      <h1>Upload Scenario</h1>
      <p>Upload a scenario file for analysis.</p>

      <input type="file" onChange={handleFileChange} />

      <div style={{ marginTop: "16px" }}>
      <Button onClick={() => void handleUpload()}>{loading ? "Uploading..." : "Upload Scenario"}</Button>
      </div>
    </div>
  );
};

export default ScenarioUpload;
