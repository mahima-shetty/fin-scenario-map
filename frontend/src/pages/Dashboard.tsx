import { useEffect, useState } from "react";
import ButtonLink from "../components/ButtonLink";
import { fetchRecentScenarios } from "../services/scenarioService";
import type { RecentScenario } from "../types/scenario";
import { toApiError } from "../services/apiClient";

const Dashboard = () => {
  const [recentScenarios, setRecentScenarios] = useState<RecentScenario[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        setLoading(true);
        setError("");
        const res = await fetchRecentScenarios(20);
        if (!cancelled) setRecentScenarios(res.scenarios ?? []);
      } catch (err) {
        if (!cancelled) {
          setError(toApiError(err).message);
          setRecentScenarios([]);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div>
      <div style={{ marginBottom: 12 }}>
        <h1>Operational overview</h1>
        <p>
          Upload or create scenarios, track processing, and keep an audit-ready
          trail of results.
        </p>
      </div>

      <div className="grid3" style={{ marginBottom: 14 }}>
        <div className="card">
          <div className="cardBody">
            <div className="topbarTitle">Scenarios processed</div>
            <div style={{ fontSize: 28, fontWeight: 800, marginTop: 8 }}>
              {loading ? "—" : recentScenarios.length}
            </div>
            <div className="helper">From stored scenarios (no mock data)</div>
          </div>
        </div>
        <div className="card">
          <div className="cardBody">
            <div className="topbarTitle">In progress</div>
            <div style={{ fontSize: 28, fontWeight: 800, marginTop: 8 }}>—</div>
            <div className="helper">Processing queue</div>
          </div>
        </div>
        <div className="card">
          <div className="cardBody">
            <div className="topbarTitle">Controls status</div>
            <div
              style={{
                display: "flex",
                gap: 10,
                flexWrap: "wrap",
                marginTop: 10,
              }}
            >
              <span className="badge badgeOk">CORS enabled</span>
              <span className="badge badgeOk">Auth ready</span>
              <span className="badge badgeOk">
                Scenario API: input/upload ready
              </span>
            </div>
            <div className="helper">
              Result/list endpoints can be added next.
            </div>
          </div>
        </div>
      </div>

      <div className="grid2" style={{ marginBottom: 14 }}>
        <div className="card">
          <div className="cardBody">
            <h2>Quick actions</h2>
            <p>Start a new workflow with bank-grade defaults.</p>
            <div
              style={{
                display: "flex",
                gap: 10,
                flexWrap: "wrap",
                marginTop: 8,
              }}
            >
              <ButtonLink to="/scenarios/upload">Upload scenario</ButtonLink>
              <ButtonLink to="/scenarios/new" variant="secondary">
                Create scenario
              </ButtonLink>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="cardBody">
            <h2>System health</h2>
            <p>High-level service indicators for local development.</p>
            <div style={{ display: "grid", gap: 8, marginTop: 6 }}>
              <div className="badge badgeOk">Frontend: running</div>
              <div className="badge badgeOk">Backend: running</div>
              <div className="badge badgeOk">
                Scenario endpoints: input/upload OK
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="cardBody">
          <h2>Recent scenarios</h2>
          <p>Most recent submissions. Create a scenario to see entries here.</p>

          {error ? (
            <div className="badge badgeWarn" style={{ marginTop: 8 }}>
              {error}
            </div>
          ) : loading ? (
            <div className="badge" style={{ marginTop: 8 }}>
              Loading…
            </div>
          ) : recentScenarios.length > 0 ? (
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Risk</th>
                  <th>Created</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {recentScenarios.map((scn) => (
                  <tr key={scn.id}>
                    <td style={{ color: "rgba(226, 232, 240, 0.78)" }}>
                      {scn.id}
                    </td>
                    <td style={{ fontWeight: 700 }}>{scn.name}</td>
                    <td>{scn.risk}</td>
                    <td style={{ color: "rgba(226, 232, 240, 0.78)" }}>
                      {scn.createdAt}
                    </td>
                    <td>
                      <span
                        className={`badge ${
                          scn.status === "Completed"
                            ? "badgeOk"
                            : scn.status === "Processing"
                            ? "badgeWarn"
                            : ""
                        }`}
                      >
                        {scn.status}
                      </span>
                    </td>
                    <td>
                      <ButtonLink
                        to={`/scenarios/${scn.id}/result`}
                        variant="secondary"
                      >
                        View result
                      </ButtonLink>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="badge" style={{ marginTop: 8 }}>
              No submissions yet
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
