"""
Hugging Face embeddings via sentence-transformers (runs locally, no API key).
Used for historical case vector similarity when Groq embeddings are unavailable.
"""
from __future__ import annotations

# Small, fast model; good for semantic similarity. First run downloads ~80MB.
DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

_model = None


def _log():
    try:
        from .run_log import get_run_logger
        return get_run_logger()
    except ImportError:
        from run_log import get_run_logger
        return get_run_logger()


def _get_model(model_name: str = DEFAULT_MODEL):
    """Lazy-load the sentence-transformers model."""
    global _model
    if _model is None:
        try:
            _log().info("embeddings_hf loading model=%s (first run may download ~80MB)...", model_name)
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(model_name)
            _log().info("embeddings_hf loaded model=%s", model_name)
        except Exception as e:
            _log().warning("embeddings_hf failed to load model: %s", e, exc_info=True)
    return _model


def get_embedding_hf(text: str, model_name: str = DEFAULT_MODEL) -> list[float] | None:
    """Return embedding vector for one text, or None if model fails."""
    text = (text or "").strip() or " "
    try:
        model = _get_model(model_name)
        if model is None:
            return None
        vec = model.encode(text, convert_to_numpy=True)
        return vec.tolist()
    except Exception as e:
        _log().warning("embeddings_hf get_embedding failed: %s", e, exc_info=True)
    return None


def get_embeddings_batch_hf(
    texts: list[str],
    model_name: str = DEFAULT_MODEL,
    batch_size: int = 32,
) -> list[list[float]] | None:
    """Return list of embedding vectors for many texts. None if model fails."""
    if not texts:
        return None
    texts = [t.strip() or " " for t in texts]
    try:
        model = _get_model(model_name)
        if model is None:
            return None
        import numpy as np
        vecs = model.encode(texts, batch_size=batch_size, convert_to_numpy=True)
        if isinstance(vecs, np.ndarray) and vecs.ndim == 2 and vecs.shape[0] == len(texts):
            return vecs.tolist()
    except Exception as e:
        _log().warning("embeddings_hf get_embeddings_batch failed: %s", e, exc_info=True)
    return None
