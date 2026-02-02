import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import ButtonLink from "../components/ButtonLink";
import { fetchScenarioResult } from "../services/scenarioService";
import type { ScenarioResultResponse } from "../types/scenario";
import { toApiError } from "../services/apiClient";

const ScenarioResult = () => {
  const { id } = useParams();

  const mockResult: ScenarioResultResponse = useMemo(
    () => ({
      scenarioName: "Interest Rate Shock",
      riskType: "Market Risk",
      confidenceScore: 0.82,
      createdAt: "2026-02-01",
      recommendations: [
        "Increase capital buffer by 10%",
        "Reprice floating-rate products",
        "Hedge long-term exposure",
      ],
      historicalCases: [
        {
          id: "HC-001",
          name: "2018 Rate Hike",
          similarity: "87%",
        },
        {
          id: "HC-002",
          name: "2020 Inflation Spike",
          similarity: "79%",
        },
      ],
    }),
    []
  );

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [result, setResult] = useState<ScenarioResultResponse>(mockResult);

  useEffect(() => {
    if (!id) return;

    let cancelled = false;

    const run = async () => {
      try {
        setLoading(true);
        setError("");
        const res = await fetchScenarioResult(id);
        if (!cancelled) setResult(res);
      } catch (err) {
        if (!cancelled) {
          setError(toApiError(err).message);
          setResult(mockResult);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    void run();

    return () => {
      cancelled = true;
    };
  }, [id, mockResult]);

  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: 12,
          flexWrap: "wrap",
        }}
      >
        <div>
          <h1>Scenario result</h1>
          <p>
            Scenario ID:{" "}
            <span
              style={{ fontWeight: 700, color: "rgba(241, 245, 249, 0.92)" }}
            >
              {id}
            </span>
          </p>
        </div>
        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <ButtonLink to="/" variant="secondary">
            Back to dashboard
          </ButtonLink>
        </div>
      </div>

      <div className="grid2" style={{ marginTop: 14 }}>
        <div className="card">
          <div className="cardBody">
            <h2>Scenario overview</h2>
            <p>Key metadata used for audit trails and reviewer context.</p>

            {loading ? <div className="badge">Loading result…</div> : null}
            {error ? (
              <div className="badge badgeWarn">
                Result API not available: {error} (showing mock data)
              </div>
            ) : null}

            <div style={{ display: "grid", gap: 10, marginTop: 10 }}>
              <div className="badge">
                <span style={{ color: "rgba(226, 232, 240, 0.72)" }}>Name</span>
                &nbsp;—&nbsp;
                <span style={{ fontWeight: 700 }}>{result.scenarioName}</span>
              </div>
              <div className="badge">
                <span style={{ color: "rgba(226, 232, 240, 0.72)" }}>Risk</span>
                &nbsp;—&nbsp;
                <span style={{ fontWeight: 700 }}>{result.riskType}</span>
              </div>
              <div className="badge badgeOk">
                <span style={{ color: "rgba(226, 232, 240, 0.72)" }}>
                  Confidence
                </span>
                &nbsp;—&nbsp;
                <span style={{ fontWeight: 800 }}>
                  {(result.confidenceScore * 100).toFixed(0)}%
                </span>
              </div>
              <div className="badge">
                <span style={{ color: "rgba(226, 232, 240, 0.72)" }}>
                  Created
                </span>
                &nbsp;—&nbsp;
                <span style={{ fontWeight: 700 }}>{result.createdAt}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="cardBody">
            <h2>Recommendations</h2>
            <p>Suggested actions based on scenario analysis (mock).</p>

            <div style={{ display: "grid", gap: 10, marginTop: 10 }}>
              {result.recommendations.map((rec, idx) => (
                <div key={idx} className="badge">
                  <span style={{ color: "rgba(226, 232, 240, 0.72)" }}>
                    REC-{String(idx + 1).padStart(2, "0")}
                  </span>
                  <span style={{ fontWeight: 650 }}>{rec}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginTop: 14 }}>
        <div className="cardBody">
          <h2>Historical reference cases</h2>
          <p>Closest historical events for comparative analysis (mock).</p>

          <table className="table" style={{ marginTop: 10 }}>
            <thead>
              <tr>
                <th>Case ID</th>
                <th>Name</th>
                <th>Similarity</th>
              </tr>
            </thead>
            <tbody>
              {result.historicalCases.map((hc) => (
                <tr key={hc.id}>
                  <td style={{ color: "rgba(226, 232, 240, 0.78)" }}>
                    {hc.id}
                  </td>
                  <td style={{ fontWeight: 700 }}>{hc.name}</td>
                  <td>
                    <span className="badge badgeOk">{hc.similarity}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ScenarioResult;
