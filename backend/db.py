"""
PostgreSQL persistence for scenarios. All collected details are stored and used as historical data.
Sensitive fields (input_description, audit_log.details) are encrypted at rest when DATA_ENCRYPTION_KEY is set (PRD FR9).
"""
from __future__ import annotations

import json
from contextlib import contextmanager
from typing import Any


def _encrypt(s: str) -> str:
    try:
        from .encryption import encrypt_value
        return encrypt_value(s or "") or ""
    except Exception:
        return s or ""


def _decrypt(s: str) -> str:
    if not s:
        return ""
    try:
        from .encryption import decrypt_value
        return decrypt_value(s) or ""
    except Exception:
        return s

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None  # type: ignore
    RealDictCursor = None  # type: ignore

_SCHEMA = """
CREATE TABLE IF NOT EXISTS scenarios (
    id SERIAL PRIMARY KEY,
    scenario_id TEXT UNIQUE NOT NULL,
    input_name TEXT NOT NULL,
    input_description TEXT,
    input_risk_type TEXT NOT NULL,
    result_scenario_name TEXT,
    result_risk_type TEXT,
    confidence_score REAL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    recommendations JSONB DEFAULT '[]',
    historical_cases JSONB DEFAULT '[]',
    step_log JSONB DEFAULT '[]',
    error TEXT
);
CREATE INDEX IF NOT EXISTS idx_scenarios_scenario_id ON scenarios(scenario_id);

CREATE TABLE IF NOT EXISTS reference_cases (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    issue_description TEXT NOT NULL,
    impact TEXT NOT NULL,
    recommendations JSONB DEFAULT '[]',
    risk_type TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_reference_cases_risk_type ON reference_cases(risk_type);

CREATE TABLE IF NOT EXISTS scenario_cases (
    id SERIAL PRIMARY KEY,
    scenario_id TEXT NOT NULL,
    source TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    risk_type TEXT NOT NULL,
    file_name TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_scenario_cases_scenario_id ON scenario_cases(scenario_id);
CREATE INDEX IF NOT EXISTS idx_scenario_cases_source ON scenario_cases(source);
CREATE INDEX IF NOT EXISTS idx_scenario_cases_created_at ON scenario_cases(created_at DESC);

CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    user_email TEXT NOT NULL,
    action TEXT NOT NULL,
    resource TEXT,
    details TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at DESC);

CREATE TABLE IF NOT EXISTS upload_files (
    id SERIAL PRIMARY KEY,
    file_name TEXT NOT NULL,
    object_key TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_upload_files_created_at ON upload_files(created_at DESC);
"""


def _get_connection():
    try:
        from .settings import get_settings
        url = get_settings().database_url
    except ImportError:
        from settings import get_settings
        url = get_settings().database_url
    return psycopg2.connect(url)


@contextmanager
def _cursor():
    if psycopg2 is None:
        raise RuntimeError("psycopg2 not installed; pip install psycopg2-binary")
    conn = _get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            yield cur
            conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """Create scenarios and reference_cases tables if they do not exist. Call at app startup."""
    try:
        with _cursor() as cur:
            cur.execute(_SCHEMA)
        seed_reference_cases()
    except Exception as e:
        # Log but do not fail startup if DB is unavailable (e.g. no PostgreSQL running)
        try:
            from .run_log import get_run_logger
            get_run_logger().warning("db init_db failed: %s", e)
        except ImportError:
            from run_log import get_run_logger
            get_run_logger().warning("db init_db failed: %s", e)


# 50 preloaded reference cases: issue, impact, recommendations (for historical matching)
_REFERENCE_CASES = [
    ("HC-001", "2018 Interest Rate Hike", "Central bank raised policy rates sharply. Funding costs rose; bond yields spiked.", "Mark-to-market losses on fixed income; NIM compression; refinancing stress.", ["Increase capital buffer", "Reprice floating-rate products", "Hedge long-term rate exposure"], "Market"),
    ("HC-002", "2020 Inflation Spike", "Rapid inflation surge; supply chain disruption and energy shock.", "Real asset values eroded; credit quality deterioration; margin pressure.", ["Stress test portfolios for stagflation", "Review counterparty limits", "Enhance operational resilience"], "Market"),
    ("HC-003", "Liquidity Crisis", "Severe funding stress; wholesale and interbank markets seized.", "Asset fire sales; inability to meet outflows; contagion risk.", ["Maintain HQLA buffer", "Diversify funding sources", "Update contingency funding plan"], "Liquidity"),
    ("HC-004", "Credit Default Wave", "Widespread corporate defaults; recession and rising unemployment.", "Credit portfolio losses; provisions spike; capital erosion.", ["Increase provisions", "Tighten underwriting", "Reduce single-name concentration"], "Credit"),
    ("HC-005", "Fraud and Unauthorized Trading", "Internal control failure; unauthorized positions and concealment.", "Large losses; reputational damage; regulatory sanctions.", ["Strengthen segregation of duties", "Improve audit trails", "Deploy fraud detection tools"], "Operational"),
    ("HC-006", "Equity and Bond Market Crash", "Sharp fall in equity and bond prices; volatility spike.", "VaR breaches; margin calls; collateral shortfalls.", ["Reduce leverage", "Hedge key exposures", "Diversify across uncorrelated assets"], "Market"),
    ("HC-007", "Regulatory Capital Shortfall", "Risk-weighted assets increased; capital ratio fell below minimum.", "PRA intervention; restrictions on distributions; funding cost rise.", ["Raise capital or optimize RWA", "Retain earnings", "Review model assumptions"], "Credit"),
    ("HC-008", "Counterparty Default", "Major counterparty defaulted on derivatives and repo.", "CVA losses; replacement cost; liquidity strain to rehedge.", ["Collateralise OTC exposure", "Reduce concentration", "Monitor credit limits"], "Credit"),
    ("HC-009", "Cyber Attack and Data Breach", "Ransomware and exfiltration of customer data.", "Operational disruption; regulatory fines; customer churn.", ["Harden systems and access controls", "Incident response plan", "Cyber insurance"], "Operational"),
    ("HC-010", "FX Volatility and Devaluation", "Sudden currency move; emerging market devaluation.", "Translation and transaction losses; sovereign risk.", ["Hedge material FX exposure", "Limit EM concentration", "Scenario test devaluation"], "Market"),
    ("HC-011", "Property Market Collapse", "Commercial and residential real estate crash.", "Collateral shortfall; default spike in mortgage book.", ["Stress property portfolios", "Limit LTV and concentration", "Increase provisions"], "Credit"),
    ("HC-012", "Commodity Shock", "Oil and gas price spike; supply disruption.", "Funding cost; hedging losses; sector concentration risk.", ["Diversify energy exposure", "Review margin and collateral", "Scenario test commodity spike"], "Market"),
    ("HC-013", "Payment System Outage", "Core payment system failed; prolonged downtime.", "Settlement failure; liquidity gridlock; regulatory scrutiny.", ["Invest in resilience and DR", "Test recovery procedures", "Liaise with central bank"], "Operational"),
    ("HC-014", "Sovereign Debt Crisis", "Sovereign default or restructuring in key jurisdiction.", "Hold-to-maturity losses; contagion; funding stress.", ["Limit sovereign concentration", "Stress sovereign portfolio", "Diversify sovereign exposure"], "Credit"),
    ("HC-015", "Margin and Collateral Spiral", "Rising margin calls; collateral shortage; CCP default.", "Liquidity drain; forced sales; systemic stress.", ["Optimise collateral usage", "Maintain collateral buffer", "Monitor CCP exposure"], "Liquidity"),
    ("HC-016", "Conduct and Mis-Selling", "Mis-selling and inappropriate advice; culture failures.", "Customer redress; fines; reputational harm.", ["Strengthen conduct framework", "Improve training and incentives", "Independent review"], "Operational"),
    ("HC-017", "Pandemic and Lockdown", "Pandemic led to lockdowns; supply and demand shock.", "Credit losses; market volatility; operational disruption.", ["Scenario test pandemic", "Remote working resilience", "Review sector exposure"], "Credit"),
    ("HC-018", "Money Laundering Failure", "AML controls failed; suspicious activity not reported.", "Regulatory fines; deferred prosecution; licence risk.", ["Enhance AML systems", "Improve SAR processes", "Training and governance"], "Operational"),
    ("HC-019", "Concentration in Single Sector", "Over-exposure to one sector; sector-wide downturn.", "Concentrated losses; capital impact; rating pressure.", ["Set sector limits", "Diversify across sectors", "Stress sector exposure"], "Credit"),
    ("HC-020", "Model Error and Wrong Pricing", "Pricing or risk model error; incorrect hedges.", "Trading losses; incorrect risk metrics; capital miscalculation.", ["Model validation and governance", "Independent price verification", "Limit model-dependent positions"], "Operational"),
    ("HC-021", "Funding Run on Bank", "Retail and wholesale depositors withdrew funds rapidly.", "Liquidity crisis; fire sales; resolution risk.", ["Maintain stable funding mix", "LCR and NSFR buffers", "Communication and contingency plan"], "Liquidity"),
    ("HC-022", "Legal and Litigation Shock", "Major litigation; class action; regulatory enforcement.", "Settlement cost; provisions; reputational damage.", ["Reserve for litigation", "Improve documentation", "Legal risk governance"], "Operational"),
    ("HC-023", "Climate and Transition Risk", "Policy and technology shift; stranded assets; physical damage.", "Valuation losses; credit migration; reputational risk.", ["Assess climate exposure", "Scenario analysis", "Disclosure and targets"], "Credit"),
    ("HC-024", "Third-Party and Outsourcing Failure", "Critical outsourced service failed or was compromised.", "Operational disruption; data loss; regulatory findings.", ["Map critical third parties", "Contract and exit rights", "Ongoing due diligence"], "Operational"),
    ("HC-025", "Interest Rate Floor at Zero", "Rates at or below zero; margin and profitability pressure.", "NIM compression; model and system adjustments.", ["Reprice products", "Cost reduction", "Diversify revenue"], "Market"),
    ("HC-026", "Concentration in Single Counterparty", "Large exposure to one counterparty; counterparty default.", "Major loss; capital impact; liquidity strain.", ["Enforce single-name limits", "Collateral and netting", "Regular exposure reporting"], "Credit"),
    ("HC-027", "Trade Settlement Failure", "Settlement fails spiked; operational and market disruption.", "Buy-in risk; liquidity; regulatory penalties.", ["Improve settlement processes", "Reduce fail rates", "Monitor agent performance"], "Operational"),
    ("HC-028", "Structured Product Blow-Up", "Complex product lost value; mis-selling and suitability.", "Client claims; losses; regulatory scrutiny.", ["Simplify product set", "Suitability and disclosure", "Stress complex products"], "Market"),
    ("HC-029", "Breach of Sanctions", "Transactions with sanctioned entities or jurisdictions.", "Fines; enforcement; licence and relationship risk.", ["Sanctions screening and governance", "Training", "Periodic review"], "Operational"),
    ("HC-030", "Pension and Benefit Liability", "Underfunded pension; longevity or rate shock.", "Balance sheet impact; sponsor support; covenant risk.", ["Hedge pension risk", "Funding plan", "Scenario test"], "Credit"),
    ("HC-031", "Run on Money Market Fund", "MMF broke the buck or suspended redemptions.", "Liquidity stress; reputational impact; regulatory change.", ["Limit MMF exposure", "Diversify liquidity", "Monitor fund metrics"], "Liquidity"),
    ("HC-032", "Conduct of Staff in Trading", "Manipulation; front-running; inappropriate behaviour.", "Fines; bans; culture and control overhaul.", ["Surveillance and controls", "Tone from top", "Remuneration and accountability"], "Operational"),
    ("HC-033", "IT System Failure", "Core banking or trading system outage; data corruption.", "Unable to transact; incorrect data; recovery cost.", ["Resilience and DR", "Change and testing", "Capacity planning"], "Operational"),
    ("HC-034", "Real Estate Concentration", "Large exposure to real estate; property crash.", "Collateral shortfall; default wave; capital hit.", ["Limit real estate concentration", "Stress test", "LTV and covenant review"], "Credit"),
    ("HC-035", "Emerging Market Crisis", "EM currency and debt crisis; capital flight.", "Sovereign and corporate losses; funding stress.", ["Limit EM exposure", "Hedge FX", "Scenario test EM stress"], "Market"),
    ("HC-036", "Insurance and Reinsurance Failure", "Major claim or reinsurer default; model error.", "Unexpected losses; capital impact; reputation.", ["Reinsurer diversification", "Stress underwriting", "Reserve adequacy"], "Credit"),
    ("HC-037", "Reputational Event", "Scandal; adverse media; loss of trust.", "Deposit and funding outflow; business loss.", ["Crisis communication", "Governance and culture", "Stakeholder engagement"], "Operational"),
    ("HC-038", "Clearing Member Default", "Clearing member default; CCP loss allocation.", "Financial loss; liquidity call; operational disruption.", ["Monitor CCP exposure", "Default fund and margin", "Member resilience"], "Liquidity"),
    ("HC-039", "Valuation and Fair Value Dispute", "Material uncertainty in fair value; audit qualification.", "Capital and P&L impact; regulatory focus.", ["Independent valuation", "Documentation", "Governance"], "Operational"),
    ("HC-040", "Concentration in High Yield", "Large high-yield exposure; spread widening and defaults.", "Mark-to-market and credit losses.", ["Limit high-yield concentration", "Stress test", "Diversify credit"], "Credit"),
    ("HC-041", "Regulatory Change and Compliance", "New regulation; interpretation change; enforcement.", "Remediation cost; fines; business model impact.", ["Horizon scanning", "Compliance by design", "Training and controls"], "Operational"),
    ("HC-042", "Funding Maturity Mismatch", "Short-term funding of long-term assets; rollover risk.", "Liquidity stress when funding dries up.", ["Match maturity profile", "Diversify funding", "Contingency funding"], "Liquidity"),
    ("HC-043", "Geopolitical Shock", "War; sanctions; supply chain disruption.", "Market and credit stress; operational disruption.", ["Scenario analysis", "Limit affected exposures", "Crisis planning"], "Market"),
    ("HC-044", "Algorithm and Trading Glitch", "Algo malfunction; erroneous orders; market impact.", "Trading losses; market disruption; regulatory scrutiny.", ["Kill switches and limits", "Testing and monitoring", "Governance"], "Operational"),
    ("HC-045", "Concentration in Auto and Consumer", "Auto and consumer credit overexposure; recession.", "Default spike; collateral shortfall.", ["Sector limits", "Stress test", "Underwriting review"], "Credit"),
    ("HC-046", "Benchmark and Index Discontinuation", "Key benchmark discontinued or reformed.", "Contract and system changes; valuation impact.", ["Monitor benchmark reform", "Fallbacks and renegotiation", "System and contract updates"], "Operational"),
    ("HC-047", "Natural Catastrophe", "Flood; earthquake; hurricane; physical damage.", "Property and business interruption; insurance claims.", ["Cat risk assessment", "Insurance and reinsurance", "Business continuity"], "Operational"),
    ("HC-048", "Credit Rating Downgrade", "Single or multiple notch downgrade; trigger events.", "Funding cost; collateral calls; covenant breach.", ["Monitor rating triggers", "Reduce trigger sensitivity", "Funding diversification"], "Credit"),
    ("HC-049", "Leverage and Balance Sheet Blow-Up", "Excessive leverage; margin call and forced deleveraging.", "Losses; fire sales; contagion.", ["Leverage limits", "Stress test", "Liquidity buffer"], "Market"),
    ("HC-050", "Data Quality and Governance Failure", "Poor data quality; wrong reporting; decision errors.", "Regulatory findings; wrong risk metrics; losses.", ["Data governance framework", "Data quality controls", "Single source of truth"], "Operational"),
]


def seed_reference_cases() -> None:
    """Insert 50 reference cases if table is empty. Idempotent."""
    try:
        with _cursor() as cur:
            cur.execute("SELECT COUNT(*) AS n FROM reference_cases")
            row = cur.fetchone()
            if row and (row["n"] or 0) >= 50:
                return
            cur.execute("DELETE FROM reference_cases")
            for case in _REFERENCE_CASES:
                case_id, name, issue_desc, impact, recs, risk_type = case
                cur.execute(
                    """
                    INSERT INTO reference_cases (id, name, issue_description, impact, recommendations, risk_type)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (case_id, name, issue_desc, impact, json.dumps(recs), risk_type),
                )
    except Exception as e:
        try:
            from .run_log import get_run_logger
            get_run_logger().warning("db seed_reference_cases failed: %s", e)
        except ImportError:
            from run_log import get_run_logger
            get_run_logger().warning("db seed_reference_cases failed: %s", e)


def save_scenario(
    scenario_id: str,
    input_name: str,
    input_description: str,
    input_risk_type: str,
    result: dict[str, Any],
) -> None:
    """Persist scenario input and workflow result to PostgreSQL."""
    with _cursor() as cur:
        cur.execute(
            """
            INSERT INTO scenarios (
                scenario_id, input_name, input_description, input_risk_type,
                result_scenario_name, result_risk_type, confidence_score,
                recommendations, historical_cases, step_log, error
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (scenario_id) DO UPDATE SET
                input_name = EXCLUDED.input_name,
                input_description = EXCLUDED.input_description,
                input_risk_type = EXCLUDED.input_risk_type,
                result_scenario_name = EXCLUDED.result_scenario_name,
                result_risk_type = EXCLUDED.result_risk_type,
                confidence_score = EXCLUDED.confidence_score,
                recommendations = EXCLUDED.recommendations,
                historical_cases = EXCLUDED.historical_cases,
                step_log = EXCLUDED.step_log,
                error = EXCLUDED.error
            """,
            (
                scenario_id,
                input_name or "",
                _encrypt(input_description or ""),
                input_risk_type or "",
                result.get("scenarioName") or "",
                result.get("riskType") or "",
                result.get("confidenceScore"),
                json.dumps(result.get("recommendations") or []),
                json.dumps(result.get("historicalCases") or []),
                json.dumps(result.get("step_log") or []),
                result.get("error"),
            ),
        )


def save_scenario_case(
    scenario_id: str,
    source: str,
    name: str,
    description: str,
    risk_type: str,
    file_name: str | None = None,
) -> None:
    """Insert one row into scenario_cases (create or upload)."""
    with _cursor() as cur:
        cur.execute(
            """
            INSERT INTO scenario_cases (scenario_id, source, name, description, risk_type, file_name)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (scenario_id, source, (name or "").strip() or "—", description or "", risk_type or "Market", file_name),
        )


def save_scenario_cases_from_upload(
    cases: list[dict[str, Any]],
    file_name: str,
) -> None:
    """Insert multiple rows into scenario_cases from an upload. Each case: name, description, risk_type."""
    import uuid
    with _cursor() as cur:
        for i, case in enumerate(cases):
            scenario_id = f"scn-upload-{uuid.uuid4().hex[:8]}-{i}"
            name = (case.get("name") or "").strip() or "—"
            description = (case.get("description") or "").strip()
            risk_type = (case.get("riskType") or case.get("risk_type") or "Market").strip() or "Market"
            cur.execute(
                """
                INSERT INTO scenario_cases (scenario_id, source, name, description, risk_type, file_name)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (scenario_id, "upload", name, description, risk_type, file_name),
            )


def get_recent_scenarios(limit: int = 20) -> list[dict[str, Any]]:
    """Return most recent scenarios for dashboard: id, name, risk, createdAt, status. Ordered by created_at DESC."""
    with _cursor() as cur:
        cur.execute(
            """
            SELECT scenario_id, input_name, result_scenario_name, input_risk_type, result_risk_type, created_at
            FROM scenarios
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (max(1, min(limit, 100)),),
        )
        rows = cur.fetchall()
    out = []
    for row in rows or []:
        created_at = row.get("created_at")
        created_str = created_at.strftime("%Y-%m-%d %H:%M") if created_at else ""
        name = (row.get("result_scenario_name") or row.get("input_name") or "").strip() or "—"
        risk = (row.get("result_risk_type") or row.get("input_risk_type") or "").strip() or "—"
        out.append({
            "id": row.get("scenario_id") or "",
            "name": name,
            "risk": risk,
            "createdAt": created_str,
            "status": "Completed",
        })
    return out


def get_scenario_by_id(scenario_id: str) -> dict[str, Any] | None:
    """Load one scenario by scenario_id. Returns None if not found."""
    with _cursor() as cur:
        cur.execute(
            "SELECT * FROM scenarios WHERE scenario_id = %s",
            (scenario_id,),
        )
        row = cur.fetchone()
    if not row:
        return None
    # Use input as fallback so UI never shows empty/NA when we have submitted data
    scenario_name = (row.get("result_scenario_name") or row.get("input_name") or "").strip()
    risk_type = (row.get("result_risk_type") or row.get("input_risk_type") or "").strip()
    created_at = row.get("created_at")
    created_str = created_at.strftime("%Y-%m-%d %H:%M") if created_at else ""
    return {
        "scenario_id": row["scenario_id"],
        "scenarioName": scenario_name,
        "riskType": risk_type,
        "inputName": row["input_name"] or "",
        "inputDescription": _decrypt(row["input_description"] or ""),
        "inputRiskType": row["input_risk_type"] or "",
        "confidenceScore": row["confidence_score"],
        "createdAt": created_str,
        "recommendations": row["recommendations"] if isinstance(row["recommendations"], list) else (json.loads(row["recommendations"]) if row["recommendations"] else []),
        "historicalCases": row["historical_cases"] if isinstance(row["historical_cases"], list) else (json.loads(row["historical_cases"]) if row["historical_cases"] else []),
        "step_log": row["step_log"] if isinstance(row["step_log"], list) else (json.loads(row["step_log"]) if row["step_log"] else []),
    }


def get_reference_cases_list() -> list[dict[str, Any]]:
    """Return all 50 reference cases for UI: id, name, issue_description, impact, recommendations, risk_type."""
    with _cursor() as cur:
        cur.execute(
            "SELECT id, name, issue_description, impact, recommendations, risk_type FROM reference_cases ORDER BY id"
        )
        rows = cur.fetchall()
    out = []
    for row in rows or []:
        recs = row.get("recommendations")
        if not isinstance(recs, list):
            recs = json.loads(recs) if recs else []
        out.append({
            "id": row.get("id") or "",
            "name": row.get("name") or "",
            "issueDescription": row.get("issue_description") or "",
            "impact": row.get("impact") or "",
            "recommendations": recs,
            "riskType": row.get("risk_type") or "",
        })
    return out


def get_reference_cases_for_historical() -> list[dict[str, Any]]:
    """Return the 50 preloaded reference cases for TF-IDF corpus: [{ id, name, text }, ...]."""
    with _cursor() as cur:
        cur.execute(
            "SELECT id, name, issue_description, impact, risk_type FROM reference_cases ORDER BY id"
        )
        rows = cur.fetchall()
    out = []
    for row in rows or []:
        case_id = row.get("id") or ""
        name = (row.get("name") or "").strip() or "Case"
        issue = (row.get("issue_description") or "").strip()
        impact = (row.get("impact") or "").strip()
        risk = (row.get("risk_type") or "").strip()
        text = f"{name} {issue} {impact} {risk}".strip() or " "
        out.append({"id": case_id, "name": name[:80], "text": text[:5000]})
    return out


def get_all_scenarios_for_historical() -> list[dict[str, Any]]:
    """Return list of past user scenarios for historical corpus: [{ id, name, text }, ...]."""
    with _cursor() as cur:
        cur.execute(
            "SELECT scenario_id, input_name, input_description, input_risk_type FROM scenarios ORDER BY id"
        )
        rows = cur.fetchall()
    out = []
    for i, row in enumerate(rows or []):
        sid = row.get("scenario_id") or f"scn-{i + 1}"
        name = (row.get("input_name") or "").strip() or f"Scenario {i + 1}"
        desc = _decrypt(row.get("input_description") or "").strip()
        risk = (row.get("input_risk_type") or "").strip()
        text = f"{name} {desc} {risk}".strip() or " "
        out.append({"id": sid, "name": name[:80], "text": text[:5000]})
    return out


def insert_audit_log(user_email: str, action: str, resource: str | None = None, details: str | None = None) -> None:
    """Append an audit log entry. No-op if DB fails."""
    try:
        with _cursor() as cur:
            cur.execute(
                "INSERT INTO audit_log (user_email, action, resource, details) VALUES (%s, %s, %s, %s)",
                (user_email, action, resource or "", _encrypt(details or "")),
            )
    except Exception:
        pass


def get_audit_logs(limit: int = 100) -> list[dict[str, Any]]:
    """Return most recent audit log entries for admin. Returns [] on error."""
    try:
        with _cursor() as cur:
            cur.execute(
                "SELECT id, user_email, action, resource, details, created_at FROM audit_log ORDER BY created_at DESC LIMIT %s",
                (limit,),
            )
            rows = cur.fetchall()
        out = []
        for row in rows or []:
            d = dict(row)
            if d.get("details"):
                d["details"] = _decrypt(d["details"])
            if d.get("created_at") is not None and hasattr(d["created_at"], "isoformat"):
                d["created_at"] = d["created_at"].isoformat()
            out.append(d)
        return out
    except Exception:
        return []


def save_upload_file_record(file_name: str, object_key: str, size_bytes: int) -> None:
    """Record an S3 upload for audit. No-op on DB error."""
    try:
        with _cursor() as cur:
            cur.execute(
                "INSERT INTO upload_files (file_name, object_key, size_bytes) VALUES (%s, %s, %s)",
                (file_name, object_key, size_bytes),
            )
    except Exception:
        pass
