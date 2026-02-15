import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import ButtonLink from "../components/ButtonLink";
import { fetchScenarioResult } from "../services/scenarioService";
import type { ScenarioResultResponse } from "../types/scenario";
import { toApiError } from "../services/apiClient";

const NA_DEFAULT: ScenarioResultResponse = {
  scenarioName: "NA",
  riskType: "NA",
  confidenceScore: null,
  createdAt: "NA",
  recommendations: [],
  historicalCases: [],
  step_log: [],
};

const ScenarioResult = () => {
  const { id } = useParams();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [result, setResult] = useState<ScenarioResultResponse>(NA_DEFAULT);

  useEffect(() => {
    if (!id) return;

    let cancelled = false;

    const run = async () => {
      try {
        setLoading(true);
        setError("");
        const res = await fetchScenarioResult(id);
        let toShow = res;
        const isNaOnly =
          (res.scenarioName === "NA" || !res.scenarioName?.trim()) &&
          (res.riskType === "NA" || !res.riskType?.trim());
        if (id && isNaOnly) {
          try {
            const stored = sessionStorage.getItem(`scenario_input_${id}`);
            if (stored) {
              const parsed = JSON.parse(stored) as Partial<ScenarioResultResponse>;
              toShow = {
                ...res,
                scenarioName: parsed.scenarioName ?? res.scenarioName,
                riskType: parsed.riskType ?? res.riskType,
                description: parsed.description ?? res.description ?? "",
                createdAt: parsed.createdAt ?? res.createdAt,
              };
            }
          } catch {
            // ignore
          }
        }
        if (!cancelled) setResult(toShow);
      } catch (err) {
        if (!cancelled) {
          setError(toApiError(err).message);
          let fallback: ScenarioResultResponse = NA_DEFAULT;
          if (id) {
            try {
              const stored = sessionStorage.getItem(`scenario_input_${id}`);
              if (stored) {
                const parsed = JSON.parse(stored) as Partial<ScenarioResultResponse>;
                fallback = {
                  ...NA_DEFAULT,
                  scenarioName: parsed.scenarioName ?? "NA",
                  riskType: parsed.riskType ?? "NA",
                  description: parsed.description ?? "",
                  createdAt: parsed.createdAt ?? "NA",
                };
              }
            } catch {
              // ignore
            }
          }
          setResult(fallback);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    void run();

    return () => {
      cancelled = true;
    };
  }, [id]);

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
                Result API not available: {error}
              </div>
            ) : null}

            <div style={{ display: "grid", gap: 10, marginTop: 10 }}>
              <div className="badge">
                <span style={{ color: "rgba(226, 232, 240, 0.72)" }}>Name</span>
                &nbsp;—&nbsp;
                <span style={{ fontWeight: 700 }}>
                  {result.scenarioName?.trim() || "—"}
                </span>
              </div>
              <div className="badge">
                <span style={{ color: "rgba(226, 232, 240, 0.72)" }}>Risk</span>
                &nbsp;—&nbsp;
                <span style={{ fontWeight: 700 }}>
                  {result.riskType?.trim() || "—"}
                </span>
              </div>
              {result.description != null && result.description !== "" ? (
                <div className="badge">
                  <span style={{ color: "rgba(226, 232, 240, 0.72)" }}>
                    Description
                  </span>
                  &nbsp;—&nbsp;
                  <span style={{ fontWeight: 600 }}>{result.description}</span>
                </div>
              ) : null}
              <div className="badge badgeOk">
                <span style={{ color: "rgba(226, 232, 240, 0.72)" }}>
                  Confidence
                </span>
                &nbsp;—&nbsp;
                <span style={{ fontWeight: 800 }}>
                  {result.confidenceScore != null
                    ? `${(result.confidenceScore * 100).toFixed(0)}%`
                    : "—"}
                </span>
              </div>
              <div className="badge">
                <span style={{ color: "rgba(226, 232, 240, 0.72)" }}>
                  Created
                </span>
                &nbsp;—&nbsp;
                <span style={{ fontWeight: 700 }}>
                  {result.createdAt?.trim() || "—"}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="cardBody">
            <h2>Recommendations</h2>
            <p>Suggested actions based on scenario analysis.</p>

            <div style={{ display: "grid", gap: 10, marginTop: 10 }}>
              {result.recommendations?.length
                ? result.recommendations.map((rec, idx) => (
                    <div key={idx} className="badge">
                      <span style={{ color: "rgba(226, 232, 240, 0.72)" }}>
                        REC-{String(idx + 1).padStart(2, "0")}
                      </span>
                      <span style={{ fontWeight: 650 }}>{rec}</span>
                    </div>
                  ))
                : "NA"}
            </div>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginTop: 14 }}>
        <div className="cardBody">
          <h2>Historical reference cases</h2>
          <p>Closest historical events for comparative analysis.</p>

          {result.historicalCases?.length ? (
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
          ) : (
            <div className="badge" style={{ marginTop: 10 }}>NA</div>
          )}
        </div>
      </div>

      {(result.step_log?.length ?? 0) > 0 && (
        <div className="card" style={{ marginTop: 14 }}>
          <div className="cardBody">
            <h2>Workflow</h2>
            <p>Steps executed for mapping and recommendations.</p>

            <div className="workflowPipeline" style={{ marginTop: 14 }}>
              <div className="workflowStep workflowStepStart">
                <span className="workflowStepLabel">Input</span>
              </div>
              {(result.step_log ?? []).map((entry, idx) => (
                <React.Fragment key={idx}>
                  <div className="workflowStepConnector" aria-hidden />
                  <div
                    className={`workflowStep workflowStepNode workflowStep--${entry.status}`}
                >
                  <span className="workflowStepLabel">
                    {entry.step === "scenario_processor"
                      ? "Parse & validate"
                      : entry.step === "orchestrator"
                        ? "Match & recommend"
                        : entry.step}
                  </span>
                  <span className={`workflowStepStatus workflowStepStatus--${entry.status}`}>
                    {entry.status}
                  </span>
                </div>
                </React.Fragment>
              ))}
              <div className="workflowStepConnector" aria-hidden />
              <div className="workflowStep workflowStepEnd">
                <span className="workflowStepLabel">Result</span>
              </div>
            </div>

            <div className="workflowTimeline" style={{ marginTop: 20 }}>
              <h3 style={{ fontSize: 14, color: "var(--muted)", marginBottom: 10 }}>
                Step log
              </h3>
              {(result.step_log ?? []).map((entry, idx) => (
                <div key={idx} className="workflowTimelineItem">
                  <div className="workflowTimelineItemHeader">
                    <span className="workflowTimelineStep">{entry.step}</span>
                    <span className={`badge workflowTimelineStatus workflowTimelineStatus--${entry.status}`}>
                      {entry.status}
                    </span>
                  </div>
                  {entry.ts ? (
                    <div className="workflowTimelineTs">{entry.ts}</div>
                  ) : null}
                  {entry.detail ? (
                    <div className="workflowTimelineDetail">{entry.detail}</div>
                  ) : null}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScenarioResult;
