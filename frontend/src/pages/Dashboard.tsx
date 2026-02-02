import ButtonLink from "../components/ButtonLink";

const Dashboard = () => {
  // Mock data for now
  const recentScenarios = [
    {
      id: "scn-001",
      name: "Credit Risk Stress Test",
      risk: "Credit",
      status: "Completed",
    },
    {
      id: "scn-002",
      name: "Liquidity Shock Scenario",
      risk: "Liquidity",
      status: "Processing",
    },
    {
      id: "scn-003",
      name: "Interest Rate Shock",
      risk: "Market",
      status: "Queued",
    },
  ];

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
              128
            </div>
            <div className="helper">Last 30 days</div>
          </div>
        </div>
        <div className="card">
          <div className="cardBody">
            <div className="topbarTitle">In progress</div>
            <div style={{ fontSize: 28, fontWeight: 800, marginTop: 8 }}>2</div>
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
          <p>Most recent submissions (mock data).</p>

          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Risk</th>
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
                    {scn.status === "Completed" ? (
                      <ButtonLink
                        to={`/scenarios/${scn.id}/result`}
                        variant="secondary"
                      >
                        View result
                      </ButtonLink>
                    ) : (
                      <ButtonLink
                        to={`/scenarios/${scn.id}/result`}
                        variant="secondary"
                        disabled
                      >
                        View result
                      </ButtonLink>
                    )}
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

export default Dashboard;
