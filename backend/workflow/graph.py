"""LangGraph workflow: scenario_processor -> orchestrator -> end."""
from langgraph.graph import StateGraph, END
from .state import WorkflowState
from .nodes import scenario_processor, orchestrator

try:
    from ..run_log import get_run_logger
except ImportError:
    from run_log import get_run_logger

logger = get_run_logger()


def build_graph():
    """Build and compile the scenario mapping graph."""
    graph = StateGraph(WorkflowState)
    graph.add_node("scenario_processor", scenario_processor)
    graph.add_node("orchestrator", orchestrator)
    graph.set_entry_point("scenario_processor")
    graph.add_edge("scenario_processor", "orchestrator")
    graph.add_edge("orchestrator", END)
    compiled = graph.compile()
    logger.info("workflow graph compiled")
    return compiled
