"""
Recommendation Engine: generate actionable recommendations using Groq (LLM).
Uses scenario name/description/risk type + matched historical cases to produce
a short list of concrete recommendations.
"""
from __future__ import annotations

from typing import Any

# Default model: fast and capable for short structured output
DEFAULT_MODEL = "llama-3.1-8b-instant"
MAX_RECOMMENDATIONS = 6


def _get_logger():
    try:
        from .run_log import get_run_logger
        return get_run_logger()
    except ImportError:
        from run_log import get_run_logger
        return get_run_logger()


def generate_recommendations(
    scenario_name: str,
    scenario_description: str,
    risk_type: str,
    historical_cases: list[dict[str, Any]],
    *,
    api_key: str | None = None,
    model: str = DEFAULT_MODEL,
) -> list[str]:
    """
    Call Groq to generate 3–6 actionable recommendations for the given scenario
    and similar historical cases. Returns a list of recommendation strings.

    If api_key is missing/empty or the API call fails, returns [] and logs.
    """
    if not (api_key or "").strip():
        _get_logger().info("recommendation_engine: GROQ_API_KEY not set; skipping AI recommendations")
        return []

    cases_text = ""
    if historical_cases:
        parts = []
        for i, c in enumerate(historical_cases[:10], 1):
            name = c.get("name") or c.get("id") or "Case"
            sim = c.get("similarity", "")
            parts.append(f"  {i}. {name}" + (f" (similarity: {sim})" if sim else ""))
        cases_text = "\n".join(parts) if parts else "None provided."

    system_prompt = """You are a banking risk and compliance advisor. Given a hypothetical scenario and a list of similar historical cases, you produce a short list of clear, actionable recommendations (controls, mitigations, or next steps). Output only the recommendations, one per line, as short bullet-style lines. No numbering, no preamble, no explanation. Each line should be one recommendation (max 1–2 sentences). Produce between 3 and 6 recommendations."""

    user_content = f"""Scenario name: {scenario_name or 'Unnamed'}\nRisk type: {risk_type or 'Not specified'}\nDescription: {scenario_description or 'No description.'}\n\nSimilar historical cases:\n{cases_text}\n\nList 3 to 6 actionable recommendations, one per line."""

    try:
        from groq import Groq
        client = Groq(api_key=api_key.strip())
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            model=model,
            temperature=0.3,
            max_tokens=512,
        )
        raw = (completion.choices[0].message.content or "").strip()
        if not raw:
            return []
        lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
        # Normalize: remove leading bullets/dashes/numbers
        result = []
        for ln in lines[:MAX_RECOMMENDATIONS]:
            ln = ln.lstrip("0123456789.-)>•* \t")
            if ln:
                result.append(ln)
        _get_logger().info("recommendation_engine: generated %s recommendations", len(result))
        return result
    except Exception as e:
        _get_logger().warning("recommendation_engine: Groq API failed: %s", e, exc_info=True)
        return []
