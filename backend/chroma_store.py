"""
ChromaDB vector store for historical case embeddings.
Persists embeddings on disk so they can be reused across restarts (optional re-sync when corpus changes).
"""
from __future__ import annotations

import os
from typing import Any

COLLECTION_NAME = "historical_cases"
# Chroma cosine: distance 0 = identical; similarity = 1 - distance (in [0,1])
CHROMA_METADATA = {"hnsw:space": "cosine"}


def _log():
    try:
        from .run_log import get_run_logger
        return get_run_logger()
    except ImportError:
        from run_log import get_run_logger
        return get_run_logger()


def _persist_path() -> str:
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "data", "chromadb")


def get_client():
    """Return a persistent Chroma client. Creates data/chromadb if needed."""
    import chromadb
    path = _persist_path()
    os.makedirs(path, exist_ok=True)
    return chromadb.PersistentClient(path=path)


def get_or_create_collection():
    """Get or create the historical_cases collection with cosine similarity."""
    client = get_client()
    try:
        coll = client.get_collection(name=COLLECTION_NAME)
        # Ensure we use cosine (existing collection may have been created with default)
        return coll
    except Exception:
        pass
    return client.create_collection(name=COLLECTION_NAME, metadata=CHROMA_METADATA)


def sync_collection(
    ids: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict[str, Any]],
) -> bool:
    """
    Replace collection contents with the given ids, embeddings, metadatas.
    Use when corpus has changed or first load. Returns True on success.
    """
    if not ids or len(ids) != len(embeddings) or len(ids) != len(metadatas):
        return False
    try:
        client = get_client()
        try:
            client.delete_collection(name=COLLECTION_NAME)
        except Exception:
            pass
        coll = client.create_collection(name=COLLECTION_NAME, metadata=CHROMA_METADATA)
        coll.add(ids=ids, embeddings=embeddings, metadatas=metadatas)
        _log().info("chroma_store synced %s documents to %s", len(ids), _persist_path())
        return True
    except Exception as e:
        _log().warning("chroma_store sync failed: %s", e, exc_info=True)
    return False


def query_similar(
    query_embedding: list[float],
    n_results: int = 5,
) -> list[dict[str, str]]:
    """
    Query Chroma for nearest documents by cosine similarity.
    Returns list of {"id": "...", "name": "...", "similarity": "87%"}.
    """
    if not query_embedding or n_results < 1:
        return []
    try:
        coll = get_or_create_collection()
        count = coll.count()
        if count == 0:
            return []
        result = coll.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, count),
            include=["metadatas", "distances"],
        )
        ids = result.get("ids")
        metadatas = result.get("metadatas")
        distances = result.get("distances")
        if not ids or not ids[0]:
            return []
        out = []
        for i, doc_id in enumerate(ids[0]):
            # Chroma cosine: distance in [0, 2], lower = more similar. Often 1 - cos_sim.
            dist = float(distances[0][i]) if distances and distances[0] else 1.0
            similarity = max(0.0, min(1.0, 1.0 - dist))
            score_pct = max(0, min(100, int(round(similarity * 100))))
            meta = (metadatas[0][i] if metadatas and metadatas[0] and i < len(metadatas[0]) else {}) or {}
            name = (meta.get("name") or str(doc_id)).strip() or "—"
            out.append({
                "id": str(doc_id),
                "name": name,
                "similarity": f"{score_pct}%",
            })
        return out
    except Exception as e:
        _log().warning("chroma_store query failed: %s", e, exc_info=True)
    return []
