import { useEffect, useMemo, useState } from "react";
import { fetchHistoricalCases } from "../services/scenarioService";
import type { HistoricalCase } from "../types/scenario";
import { toApiError } from "../services/apiClient";

const RISK_TYPES = ["Market", "Credit", "Liquidity", "Operational"] as const;

function riskBadgeClass(riskType: string): string {
  const r = riskType?.toLowerCase() || "";
  if (r.includes("market")) return "badge badgeOk";
  if (r.includes("credit")) return "badge badgeWarn";
  if (r.includes("liquidity")) return "badge";
  if (r.includes("operational")) return "badge";
  return "badge";
}

const HistoricalCases = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [cases, setCases] = useState<HistoricalCase[]>([]);
  const [filterRisk, setFilterRisk] = useState<string>("");

  useEffect(() => {
    let cancelled = false;
    const run = async () => {
      try {
        setLoading(true);
        setError("");
        const res = await fetchHistoricalCases();
        if (!cancelled) setCases(res.cases ?? []);
      } catch (err) {
        if (!cancelled) {
          setError(toApiError(err).message);
          setCases([]);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    void run();
    return () => {
      cancelled = true;
    };
  }, []);

  const filtered = useMemo(() => {
    if (!filterRisk.trim()) return cases;
    const q = filterRisk.trim().toLowerCase();
    return cases.filter((c) => (c.riskType || "").toLowerCase().includes(q));
  }, [cases, filterRisk]);

  return (
    <div>
      <div style={{ marginBottom: 20 }}>
        <h1>Historical cases</h1>
        <p style={{ color: "var(--muted)", marginTop: 6 }}>
          50 reference cases from the database: what happened, impact, and
          recommendations. Use these for comparative analysis and audit context.
        </p>
      </div>

      {loading ? (
        <div className="badge" style={{ padding: 14 }}>
          Loading historical cases…
        </div>
      ) : error ? (
        <div className="badge badgeWarn" style={{ padding: 14 }}>
          {error}
        </div>
      ) : (
        <>
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: 10,
              alignItems: "center",
              marginBottom: 20,
            }}
          >
            <span style={{ color: "var(--muted)", fontWeight: 600 }}>
              Filter by risk:
            </span>
            {RISK_TYPES.map((r) => (
              <button
                key={r}
                type="button"
                className={filterRisk === r ? "badge badgeOk" : "badge"}
                style={{
                  cursor: "pointer",
                  border: "1px solid var(--border)",
                  background:
                    filterRisk === r
                      ? "rgba(34, 211, 238, 0.15)"
                      : "rgba(255,255,255,0.04)",
                }}
                onClick={() => setFilterRisk(filterRisk === r ? "" : r)}
              >
                {r}
              </button>
            ))}
            {filterRisk ? (
              <button
                type="button"
                className="badge"
                style={{
                  cursor: "pointer",
                  border: "1px solid var(--border)",
                }}
                onClick={() => setFilterRisk("")}
              >
                Clear
              </button>
            ) : null}
            <span style={{ color: "var(--muted)", marginLeft: 8 }}>
              Showing {filtered.length} of {cases.length}
            </span>
          </div>

          <div
            className="grid2"
            style={{
              gap: 16,
              gridTemplateColumns: "repeat(auto-fill, minmax(420px, 1fr))",
            }}
          >
            {filtered.map((c) => (
              <article
                key={c.id}
                className="card"
                style={{
                  border: "1px solid var(--border)",
                  borderRadius: "var(--radius-md)",
                  overflow: "hidden",
                  boxShadow: "var(--shadow-soft)",
                }}
              >
                <div className="cardBody" style={{ padding: 18 }}>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "flex-start",
                      gap: 10,
                      marginBottom: 12,
                    }}
                  >
                    <div>
                      <span
                        style={{
                          fontSize: 12,
                          color: "var(--muted)",
                          fontWeight: 600,
                        }}
                      >
                        {c.id}
                      </span>
                      <h3
                        style={{
                          margin: "4px 0 0",
                          fontSize: 17,
                          fontWeight: 700,
                          lineHeight: 1.3,
                        }}
                      >
                        {c.name || "Unnamed case"}
                      </h3>
                    </div>
                    <span className={riskBadgeClass(c.riskType)}>
                      {c.riskType || "—"}
                    </span>
                  </div>

                  <section style={{ marginBottom: 14 }}>
                    <div
                      style={{
                        fontSize: 11,
                        textTransform: "uppercase",
                        letterSpacing: "0.06em",
                        color: "var(--muted)",
                        marginBottom: 4,
                      }}
                    >
                      What happened
                    </div>
                    <p
                      style={{
                        margin: 0,
                        fontSize: 14,
                        lineHeight: 1.5,
                        color: "var(--text)",
                      }}
                    >
                      {c.issueDescription || "—"}
                    </p>
                  </section>

                  <section style={{ marginBottom: 14 }}>
                    <div
                      style={{
                        fontSize: 11,
                        textTransform: "uppercase",
                        letterSpacing: "0.06em",
                        color: "var(--muted)",
                        marginBottom: 4,
                      }}
                    >
                      Impact
                    </div>
                    <p
                      style={{
                        margin: 0,
                        fontSize: 14,
                        lineHeight: 1.5,
                        color: "var(--text)",
                      }}
                    >
                      {c.impact || "—"}
                    </p>
                  </section>

                  {c.recommendations?.length > 0 ? (
                    <section>
                      <div
                        style={{
                          fontSize: 11,
                          textTransform: "uppercase",
                          letterSpacing: "0.06em",
                          color: "var(--muted)",
                          marginBottom: 6,
                        }}
                      >
                        Recommendations
                      </div>
                      <ul
                        style={{
                          margin: 0,
                          paddingLeft: 18,
                          fontSize: 14,
                          lineHeight: 1.55,
                          color: "var(--text)",
                        }}
                      >
                        {c.recommendations.map((rec, i) => (
                          <li key={i}>{rec}</li>
                        ))}
                      </ul>
                    </section>
                  ) : null}
                </div>
              </article>
            ))}
          </div>

          {filtered.length === 0 ? (
            <div className="badge" style={{ padding: 14 }}>
              No cases match the filter.
            </div>
          ) : null}
        </>
      )}
    </div>
  );
};

export default HistoricalCases;
