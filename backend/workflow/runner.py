"""Run the scenario workflow with retries and logging."""
from datetime import date
from .state import WorkflowState
from .graph import build_graph

try:
    from ..run_log import get_run_logger
except ImportError:
    from run_log import get_run_logger

logger = get_run_logger()

MAX_RETRIES = 2


def _default_created_at(step_log: list) -> str:
    if step_log and isinstance(step_log[0], dict):
        ts = step_log[0].get("ts") or ""
        if len(ts) >= 10:
            return ts[:10]
    return date.today().isoformat()


def run_scenario_workflow(scenario_id: str, input_data: dict) -> dict:
    """
    Run the LangGraph workflow for one scenario.
    Returns a result dict with recommendations, historical_cases, step_log, error.
    """
    initial: WorkflowState = {
        "scenario_id": scenario_id,
        "input": input_data,
        "step_log": [],
        "retry_count": 0,
    }
    graph = build_graph()
    last_state: WorkflowState = initial
    for attempt in range(MAX_RETRIES + 1):
        try:
            logger.info("workflow invoke attempt=%s scenario_id=%s", attempt + 1, scenario_id)
            last_state = graph.invoke(initial if attempt == 0 else last_state)
            if last_state.get("error") and attempt < MAX_RETRIES:
                logger.warning("workflow error scenario_id=%s retrying", scenario_id)
                last_state["retry_count"] = (last_state.get("retry_count") or 0) + 1
                continue
            break
        except Exception as e:
            logger.exception("workflow invoke failed scenario_id=%s attempt=%s", scenario_id, attempt + 1)
            last_state["error"] = str(e)
            last_state["step_log"] = last_state.get("step_log") or []
            last_state["step_log"].append({
                "step": "runner",
                "status": "error",
                "detail": str(e),
            })
            if attempt >= MAX_RETRIES:
                break
            last_state["retry_count"] = (last_state.get("retry_count") or 0) + 1

    processed = last_state.get("processed") or {}
    step_log = last_state.get("step_log") or []
    return {
        "scenario_id": scenario_id,
        "scenarioName": processed.get("name") or scenario_id,
        "riskType": processed.get("riskType") or "Market Risk",
        "confidenceScore": 0.82,
        "createdAt": _default_created_at(step_log),
        "recommendations": last_state.get("recommendations") or [],
        "historicalCases": last_state.get("historical_cases") or [],
        "step_log": step_log,
        "error": last_state.get("error"),
    }
