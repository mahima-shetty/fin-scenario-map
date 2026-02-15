"""
Embedding service using Groq (nomic-embed-text-v1_5) for agentic-AI / vector similarity.
Uses the same GROQ_API_KEY as the recommendation engine.
"""
from __future__ import annotations

MODEL = "nomic-embed-text-v1_5"
BATCH_SIZE = 50  # Groq accepts list of inputs; chunk to avoid rate limits / timeouts


def _log():
    try:
        from .run_log import get_run_logger
        return get_run_logger()
    except ImportError:
        from run_log import get_run_logger
        return get_run_logger()


def get_embedding(text: str, api_key: str | None) -> list[float] | None:
    """Return embedding vector for one text, or None if key missing or API fails."""
    if not (api_key or "").strip():
        return None
    text = (text or "").strip() or " "
    try:
        from groq import Groq
        client = Groq(api_key=api_key.strip())
        response = client.embeddings.create(input=text, model=MODEL)
        if response.data and len(response.data) > 0:
            d0 = response.data[0]
            emb = getattr(d0, "embedding", None)
            if emb is not None:
                return list(emb)
            if isinstance(d0, dict):
                return list(d0.get("embedding") or [])
    except Exception as e:
        _log().warning("embeddings get_embedding failed: %s", e, exc_info=True)
    return None


def get_embeddings_batch(
    texts: list[str],
    api_key: str | None,
    batch_size: int = BATCH_SIZE,
) -> list[list[float]] | None:
    """
    Return list of embedding vectors for many texts (batched). None if key missing or API fails.
    Preserves order; failed batches yield no vectors for that chunk (caller can fall back).
    """
    if not (api_key or "").strip() or not texts:
        return None
    out: list[list[float]] = []
    try:
        from groq import Groq
        client = Groq(api_key=api_key.strip())
        for i in range(0, len(texts), batch_size):
            chunk = [t.strip() or " " for t in texts[i : i + batch_size]]
            if not chunk:
                continue
            response = client.embeddings.create(input=chunk, model=MODEL)
            for j, item in enumerate(response.data or []):
                emb = getattr(item, "embedding", None)
                if emb is None and isinstance(item, dict):
                    emb = item.get("embedding")
                if emb is not None:
                    out.append(list(emb))
        return out if len(out) == len(texts) else None
    except Exception as e:
        _log().warning("embeddings get_embeddings_batch failed: %s", e, exc_info=True)
    return None
