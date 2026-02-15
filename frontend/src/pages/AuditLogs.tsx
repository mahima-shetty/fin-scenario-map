import { useEffect, useState } from "react";
import { apiClient, toApiError } from "../services/apiClient";

export interface AuditLogEntry {
  id: number;
  user_email: string;
  action: string;
  resource: string;
  details: string;
  created_at: string;
}

export default function AuditLogs() {
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        setLoading(true);
        setError("");
        const res = await apiClient.get<{ audit_logs: AuditLogEntry[] }>(
          "/api/audit/logs",
          { params: { limit: 100 } },
        );
        if (!cancelled) setLogs(res.data.audit_logs ?? []);
      } catch (err) {
        if (!cancelled) setError(toApiError(err).message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div>
      <h1>Audit logs</h1>
      <p style={{ color: "var(--muted)", marginBottom: 14 }}>
        Admin-only view of recent actions (login, scenario create/upload).
      </p>
      {loading && <div className="badge">Loading…</div>}
      {error && (
        <div className="badge badgeWarn" style={{ marginBottom: 10 }}>
          {error}
        </div>
      )}
      {!loading && !error && (
        <div className="card" style={{ marginTop: 10 }}>
          <div className="cardBody">
            {logs.length === 0 ? (
              <div className="badge">No audit entries yet.</div>
            ) : (
              <table className="table">
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>User</th>
                    <th>Action</th>
                    <th>Resource</th>
                    <th>Details</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((entry) => (
                    <tr key={entry.id}>
                      <td style={{ color: "var(--muted)", fontSize: 12 }}>
                        {entry.created_at}
                      </td>
                      <td>{entry.user_email}</td>
                      <td>
                        <span className="badge">{entry.action}</span>
                      </td>
                      <td>{entry.resource || "—"}</td>
                      <td>{entry.details || "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
