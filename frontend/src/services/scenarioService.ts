const API_BASE_URL = "http://127.0.0.1:8000";

export async function submitScenario(data: {
  name: string;
  description: string;
  riskType: string;
}) {
  const response = await fetch(`${API_BASE_URL}/api/scenarios/input`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error("Failed to submit scenario");
  }

  return response.json();
}
