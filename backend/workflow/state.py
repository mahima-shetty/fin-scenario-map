"""Graph state for the scenario mapping workflow."""
from typing import TypedDict


class WorkflowState(TypedDict, total=False):
    scenario_id: str
    input: dict
    processed: dict
    recommendations: list
    historical_cases: list
    error: str
    step_log: list
    retry_count: int
