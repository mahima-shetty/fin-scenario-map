import { Link } from "react-router-dom";

const Dashboard = () => {
  // Mock data for now
  const recentScenarios = [
    { id: "scn-001", name: "Credit Risk Stress Test", status: "Completed" },
    { id: "scn-002", name: "Liquidity Shock Scenario", status: "Processing" },
  ];

  return (
    <div style={{ padding: "24px" }}>
      {/* Header */}
      <h1>Fin Scenario Map</h1>
      <p>
        Analyze financial scenarios, map risks, and generate recommendations.
      </p>

      <hr />

      {/* Quick Actions */}
      <section>
        <h2>Quick Actions</h2>
        <div style={{ display: "flex", gap: "12px" }}>
          <Link to="/scenarios/upload">
            <button>Upload Scenario</button>
          </Link>

          <Link to="/scenarios/new">
            <button>Create Scenario</button>
          </Link>
        </div>
      </section>

      <hr />

      {/* Recent Scenarios */}
      <section>
        <h2>Recent Scenarios</h2>

        {recentScenarios.length === 0 ? (
          <p>No scenarios yet</p>
        ) : (
          <ul>
            {recentScenarios.map((scn) => (
              <li key={scn.id}>
                <strong>{scn.name}</strong> — {scn.status}
              </li>
            ))}
          </ul>
        )}
      </section>

      <hr />

      {/* System Status */}
      <section>
        <h2>System Status</h2>
        <p>Backend: ✅ Connected</p>
        <p>Audit Logging: ✅ Enabled</p>
      </section>
    </div>
  );
};

export default Dashboard;
