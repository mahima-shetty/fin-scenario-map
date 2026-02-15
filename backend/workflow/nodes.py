"""LangGraph nodes: scenario processor and orchestrator."""
from datetime import datetime
from .state import WorkflowState

try:
    from ..run_log import get_run_logger
except ImportError:
    from run_log import get_run_logger

logger = get_run_logger()


def _log_step(step_name: str, status: str, state: WorkflowState, detail: str = "") -> None:
    ts = datetime.utcnow().isoformat() + "Z"
    entry = {"step": step_name, "status": status, "ts": ts}
    if detail:
        entry["detail"] = detail
    logger.info("workflow step=%s status=%s scenario_id=%s %s", step_name, status, state.get("scenario_id", ""), detail)
    step_log = list(state.get("step_log") or [])
    step_log.append(entry)
    state["step_log"] = step_log


def scenario_processor(state: WorkflowState) -> WorkflowState:
    """Parse, validate, and normalize scenario input."""
    scenario_id = state.get("scenario_id") or ""
    logger.info("scenario_processor started scenario_id=%s", scenario_id)
    try:
        raw = state.get("input") or {}
        name = (raw.get("name") or "").strip()
        description = (raw.get("description") or "").strip()
        risk_type = raw.get("riskType") or "Market"
        if not name:
            state["error"] = "Scenario name is required"
            _log_step("scenario_processor", "error", state, state["error"])
            return state
        processed = {
            "name": name,
            "description": description,
            "riskType": risk_type,
        }
        state["processed"] = processed
        state["error"] = None
        _log_step("scenario_processor", "ok", state)
        return state
    except Exception as e:
        state["error"] = str(e)
        _log_step("scenario_processor", "error", state, str(e))
        logger.exception("scenario_processor failed scenario_id=%s", scenario_id)
        return state


def _get_historical_matcher():
    try:
        from ..historical_matcher import find_similar_cases
        return find_similar_cases
    except ImportError:
        from historical_matcher import find_similar_cases
        return find_similar_cases


def _get_recommendation_engine():
    try:
        from ..recommendation_engine import generate_recommendations
        return generate_recommendations
    except ImportError:
        from recommendation_engine import generate_recommendations
        return generate_recommendations


def _get_settings():
    try:
        from ..settings import get_settings
        return get_settings()
    except ImportError:
        from settings import get_settings
        return get_settings()


def orchestrator(state: WorkflowState) -> WorkflowState:
    """Match to historical cases (TF-IDF similarity), then generate AI recommendations via Groq."""
    scenario_id = state.get("scenario_id") or ""
    logger.info("orchestrator started scenario_id=%s", scenario_id)
    try:
        if state.get("error"):
            _log_step("orchestrator", "skipped", state, "previous error")
            return state
        processed = state.get("processed") or {}
        risk_type = processed.get("riskType") or ""
        # Historical cases from stored scenarios (DB) or JSON corpus via TF-IDF similarity
        query_text = f"{processed.get('name', '')} {processed.get('description', '')} {risk_type}"
        find_similar_cases = _get_historical_matcher()
        state["historical_cases"] = find_similar_cases(query_text.strip() or "risk", top_k=5)
        # AI-generated recommendations (Groq)
        settings = _get_settings()
        generate_recommendations = _get_recommendation_engine()
        state["recommendations"] = generate_recommendations(
            scenario_name=processed.get("name") or "",
            scenario_description=processed.get("description") or "",
            risk_type=risk_type,
            historical_cases=state.get("historical_cases") or [],
            api_key=settings.groq_api_key,
        )
        _log_step(
            "orchestrator", "ok", state,
            f"riskType={risk_type} historical={len(state['historical_cases'])} recommendations={len(state['recommendations'])}",
        )
        return state
    except Exception as e:
        state["error"] = str(e)
        _log_step("orchestrator", "error", state, str(e))
        logger.exception("orchestrator failed scenario_id=%s", scenario_id)
        return state
