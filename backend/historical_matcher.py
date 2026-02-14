"""
Historical case matching: similarity search over our own document set.
Uses TF-IDF + cosine similarity; no external datasets.
Documents are in backend/data/historical_cases.json.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

def _log():
    try:
        from .run_log import get_run_logger
        return get_run_logger()
    except ImportError:
        from run_log import get_run_logger
        return get_run_logger()

# Lazy load
_vectorizer: Any = None
_corpus_matrix: Any = None
_corpus_meta: list[dict] = []  # [{"id", "name", "text"}, ...]
_loaded = False

MAX_TEXT_CHARS = 5000  # truncate document text for TF-IDF
TOP_K_DEFAULT = 5


def _truncate(s: str, max_chars: int) -> str:
    s = (s or "").strip()
    s = re.sub(r"\s+", " ", s)
    return s[:max_chars] if len(s) > max_chars else s


def _path_to_cases_file() -> str:
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "data", "historical_cases.json")


def _load_documents() -> None:
    global _vectorizer, _corpus_matrix, _corpus_meta, _loaded
    if _loaded:
        return
    _loaded = True
    _corpus_meta = []
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore[import-untyped]
        # Load 50 preloaded reference cases from PostgreSQL, then add user scenarios
        try:
            from .db import get_reference_cases_for_historical, get_all_scenarios_for_historical
            ref_docs = get_reference_cases_for_historical()
            user_docs = get_all_scenarios_for_historical()
        except Exception:
            try:
                from db import get_reference_cases_for_historical, get_all_scenarios_for_historical
                ref_docs = get_reference_cases_for_historical()
                user_docs = get_all_scenarios_for_historical()
            except Exception:
                ref_docs = []
                user_docs = []
        db_docs = ref_docs + user_docs
        if db_docs:
            corpus_texts = [d["text"] for d in db_docs]
            _corpus_meta = [{"id": d["id"], "name": d["name"], "text": d["text"]} for d in db_docs]
            vectorizer = TfidfVectorizer(max_features=10000, stop_words="english", ngram_range=(1, 2))
            _corpus_matrix = vectorizer.fit_transform(corpus_texts)
            _vectorizer = vectorizer
            _log().info("historical_matcher loaded from DB ref=%s user=%s", len(ref_docs), len(user_docs))
            return
        # Fallback: JSON file
        path = _path_to_cases_file()
        if not os.path.isfile(path):
            _log().warning("historical_matcher file not found: %s", path)
            return
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
        if not isinstance(raw, list) or len(raw) == 0:
            _log().warning("historical_matcher no documents in %s", path)
            return
        corpus_texts = []
        for i, doc in enumerate(raw):
            if not isinstance(doc, dict):
                continue
            doc_id = doc.get("id") or f"HC-{i + 1:03d}"
            name = (doc.get("name") or "").strip() or f"Case {i + 1}"
            text = _truncate(str(doc.get("text") or ""), MAX_TEXT_CHARS) or " "
            corpus_texts.append(text)
            _corpus_meta.append({"id": doc_id, "name": name, "text": text})
        if not corpus_texts:
            return
        vectorizer = TfidfVectorizer(max_features=10000, stop_words="english", ngram_range=(1, 2))
        _corpus_matrix = vectorizer.fit_transform(corpus_texts)
        _vectorizer = vectorizer
        _log().info("historical_matcher loaded documents rows=%s path=%s", len(_corpus_meta), path)
    except Exception as e:
        _log().warning("historical_matcher load failed: %s", e, exc_info=True)
        _vectorizer = None
        _corpus_matrix = None
        _corpus_meta = []


def preload_dataset() -> None:
    """Call at app startup so first scenario submit is fast."""
    _load_documents()


def find_similar_cases(query_text: str, top_k: int = TOP_K_DEFAULT) -> list[dict[str, str]]:
    """
    Return top_k historical cases most similar to query_text.
    Each item: {"id": "HC-001", "name": "...", "similarity": "87%"}.
    """
    _load_documents()
    if _vectorizer is None or _corpus_matrix is None or not _corpus_meta:
        return []
    from sklearn.metrics.pairwise import cosine_similarity  # type: ignore[import-untyped]

    query_clean = _truncate(query_text, 5000) or " "
    query_vec = _vectorizer.transform([query_clean])
    sims = cosine_similarity(query_vec, _corpus_matrix).ravel()
    top_indices = sims.argsort()[-top_k:][::-1]
    result = []
    for idx in top_indices:
        if idx >= len(_corpus_meta):
            continue
        meta = _corpus_meta[idx]
        score = float(sims[idx])
        score_pct = max(0, min(100, int(round(score * 100))))
        result.append({
            "id": meta["id"],
            "name": meta["name"],
            "similarity": f"{score_pct}%",
        })
    return result
