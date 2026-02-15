"""
Historical case matching: vector similarity via ChromaDB (Groq or Hugging Face embeddings) with TF-IDF fallback.
Tries in order: (1) Groq embeddings if GROQ_API_KEY set, (2) Hugging Face (sentence-transformers),
(3) TF-IDF. When embeddings are used, vectors are stored in ChromaDB for persistence and querying.
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

# Lazy load: vector path (ChromaDB + Groq/HF) or TF-IDF path
_vectorizer: Any = None
_corpus_matrix: Any = None
_corpus_embeddings: list[list[float]] | None = None  # in-memory fallback when Chroma not used
_corpus_meta: list[dict] = []  # [{"id", "name", "text"}, ...]
_loaded = False
_use_vector_path = False  # True when any embeddings are used
_use_chroma = False  # True when ChromaDB is the vector store
_vector_backend: str = ""  # "groq" | "hf" when vector path active
_groq_api_key: str = ""  # set at load when available

MAX_TEXT_CHARS = 5000  # truncate document text
TOP_K_DEFAULT = 5


def _truncate(s: str, max_chars: int) -> str:
    s = (s or "").strip()
    s = re.sub(r"\s+", " ", s)
    return s[:max_chars] if len(s) > max_chars else s


def _path_to_cases_file() -> str:
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "data", "historical_cases.json")


def _get_settings():
    try:
        from .settings import get_settings
        return get_settings()
    except ImportError:
        from settings import get_settings
        return get_settings()


def _load_documents() -> None:
    global _vectorizer, _corpus_matrix, _corpus_embeddings, _corpus_meta, _loaded, _use_vector_path, _use_chroma, _vector_backend, _groq_api_key
    if _loaded:
        return
    _loaded = True
    _corpus_meta = []
    _corpus_embeddings = None
    _use_vector_path = False
    _use_chroma = False
    _vector_backend = ""
    _groq_api_key = (_get_settings().groq_api_key or "").strip()

    try:
        # Load document list from DB or JSON (same as before)
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
        else:
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

        if not _corpus_meta or not corpus_texts:
            return

        # 1) Vector path: try Groq when API key is set → store in ChromaDB
        if _groq_api_key:
            try:
                try:
                    from .embeddings import get_embeddings_batch
                except ImportError:
                    from embeddings import get_embeddings_batch
                embs = get_embeddings_batch(corpus_texts, _groq_api_key)
                if embs is not None and len(embs) == len(_corpus_meta):
                    try:
                        from .chroma_store import sync_collection
                    except ImportError:
                        from chroma_store import sync_collection
                    ids = [m["id"] for m in _corpus_meta]
                    metadatas = [{"name": m["name"]} for m in _corpus_meta]
                    if sync_collection(ids, embs, metadatas):
                        _use_vector_path = True
                        _use_chroma = True
                        _vector_backend = "groq"
                        _log().info(
                            "historical_matcher vector store=ChromaDB only (Groq) docs=%s",
                            len(_corpus_meta),
                        )
                        return
                    _log().warning("historical_matcher Chroma sync failed for Groq; falling back to TF-IDF")
                _log().warning("historical_matcher Groq embedding failed; trying Hugging Face")
            except Exception as e:
                _log().warning("historical_matcher Groq vector path failed: %s; trying Hugging Face", e)

        # 2) Vector path: try Hugging Face (sentence-transformers) → store in ChromaDB
        _log().info("historical_matcher embedding corpus with Hugging Face (first run may download model)...")
        try:
            try:
                from .embeddings_hf import get_embeddings_batch_hf
            except ImportError:
                from embeddings_hf import get_embeddings_batch_hf
            embs = get_embeddings_batch_hf(corpus_texts)
            if embs is not None and len(embs) == len(_corpus_meta):
                try:
                    from .chroma_store import sync_collection
                except ImportError:
                    from chroma_store import sync_collection
                ids = [m["id"] for m in _corpus_meta]
                metadatas = [{"name": m["name"]} for m in _corpus_meta]
                if sync_collection(ids, embs, metadatas):
                    _use_vector_path = True
                    _use_chroma = True
                    _vector_backend = "hf"
                    _log().info(
                        "historical_matcher vector store=ChromaDB only (Hugging Face) docs=%s",
                        len(_corpus_meta),
                    )
                    return
                _log().warning("historical_matcher Chroma sync failed for HF; falling back to TF-IDF")
            _log().warning("historical_matcher Hugging Face embedding failed; falling back to TF-IDF")
        except Exception as e:
            _log().warning("historical_matcher Hugging Face path failed: %s; falling back to TF-IDF", e)

        # 3) TF-IDF path (fallback)
        from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore[import-untyped]
        vectorizer = TfidfVectorizer(max_features=10000, stop_words="english", ngram_range=(1, 2))
        _corpus_matrix = vectorizer.fit_transform(corpus_texts)
        _vectorizer = vectorizer
        _corpus_embeddings = None
        _use_vector_path = False
        _vector_backend = ""
        _log().info("historical_matcher loaded TF-IDF path docs=%s", len(_corpus_meta))
    except Exception as e:
        _log().warning("historical_matcher load failed: %s", e, exc_info=True)
        _vectorizer = None
        _corpus_matrix = None
        _corpus_embeddings = None
        _corpus_meta = []


def preload_dataset() -> None:
    """Call at app startup so first scenario submit is fast."""
    _load_documents()


def get_vector_store_status() -> dict[str, str]:
    """Return current matcher status so callers can verify ChromaDB is in use. Call after load."""
    _load_documents()
    if _use_vector_path and _use_chroma:
        return {"vector_store": "chromadb", "embedding_backend": _vector_backend or "—"}
    if _use_vector_path:
        return {"vector_store": "in_memory", "embedding_backend": _vector_backend or "—"}
    return {"vector_store": "tfidf", "embedding_backend": ""}


def _cosine_similarity_vec(query_vec: list[float], corpus_embeddings: list[list[float]]) -> list[float]:
    """Return cosine similarity between query_vec and each row of corpus_embeddings."""
    import math
    q = query_vec
    q_norm = math.sqrt(sum(x * x for x in q)) or 1e-10
    out = []
    for row in corpus_embeddings:
        dot = sum(a * b for a, b in zip(q, row))
        r_norm = math.sqrt(sum(x * x for x in row)) or 1e-10
        out.append(dot / (q_norm * r_norm))
    return out


def find_similar_cases(query_text: str, top_k: int = TOP_K_DEFAULT) -> list[dict[str, str]]:
    """
    Return top_k historical cases most similar to query_text.
    Uses Groq or Hugging Face embeddings + vector similarity when available; else TF-IDF.
    Each item: {"id": "HC-001", "name": "...", "similarity": "87%"}.
    """
    _load_documents()
    if not _corpus_meta:
        return []

    query_clean = _truncate(query_text, 5000) or " "

    # Vector path: embed query, then ChromaDB or in-memory similarity
    if _use_vector_path:
        query_emb = None
        if _vector_backend == "groq" and _groq_api_key:
            try:
                try:
                    from .embeddings import get_embedding
                except ImportError:
                    from embeddings import get_embedding
                query_emb = get_embedding(query_clean, _groq_api_key)
            except Exception as e:
                _log().warning("historical_matcher Groq query embed failed: %s", e)
        elif _vector_backend == "hf":
            try:
                try:
                    from .embeddings_hf import get_embedding_hf
                except ImportError:
                    from embeddings_hf import get_embedding_hf
                query_emb = get_embedding_hf(query_clean)
            except Exception as e:
                _log().warning("historical_matcher HF query embed failed: %s", e)
        if query_emb is not None:
            if _use_chroma:
                _log().info("historical_matcher querying ChromaDB for top-%s similar cases", top_k)
                try:
                    try:
                        from .chroma_store import query_similar
                    except ImportError:
                        from chroma_store import query_similar
                    return query_similar(query_emb, n_results=top_k)
                except Exception as e:
                    _log().warning("historical_matcher Chroma query failed: %s", e, exc_info=True)
            elif _corpus_embeddings and len(_corpus_embeddings) > 0 and len(query_emb) == len(_corpus_embeddings[0]):
                try:
                    sims = _cosine_similarity_vec(query_emb, _corpus_embeddings)
                    top_indices = sorted(range(len(sims)), key=lambda i: sims[i], reverse=True)[:top_k]
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
                except Exception as e:
                    _log().warning("historical_matcher vector similarity failed: %s", e, exc_info=True)
        if _vectorizer is not None and _corpus_matrix is not None:
            pass  # fall through to TF-IDF
        else:
            return []

    # TF-IDF path
    if _vectorizer is None or _corpus_matrix is None:
        return []
    from sklearn.metrics.pairwise import cosine_similarity  # type: ignore[import-untyped]
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
