"""
atom_store.py - ChromaDB persistence layer for KnowledgeAtoms.

All list fields (tags, source_names, related_to, conflicts_with) are stored
as comma-separated strings in ChromaDB metadata and parsed back on retrieval.
"""
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from typing import List, Optional, Dict, Any

from backend.config import CHROMA_DIR
from backend.models.schemas import KnowledgeAtom

_client = None
_atom_collection = None


def _get_collection():
    global _client, _atom_collection
    if _atom_collection is None:
        _client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _atom_collection = _client.get_or_create_collection(
            name="knowledge_atoms",
            embedding_function=DefaultEmbeddingFunction(),
            metadata={"hnsw:space": "cosine"},
        )
    return _atom_collection


def _serialize(atom: KnowledgeAtom) -> dict:
    return {
        "atom_type": atom.atom_type.value,
        "tags": ", ".join(atom.tags),
        "source_names": ", ".join(atom.source_names),
        "source_chunks": ", ".join(atom.source_chunks),
        "confidence": str(round(atom.confidence, 3)),
        "status": atom.status.value,
        "version": str(atom.version),
        "related_to": ", ".join(atom.related_to),
        "conflicts_with": ", ".join(atom.conflicts_with),
        "superseded_by": atom.superseded_by or "",
        "created_at": atom.created_at,
        "updated_at": atom.updated_at,
    }


def _parse_list(value: str) -> List[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def _to_dict(atom_id: str, content: str, meta: dict) -> dict:
    return {
        "id": atom_id,
        "content": content,
        "atom_type": meta.get("atom_type", "other"),
        "tags": _parse_list(meta.get("tags", "")),
        "source_names": _parse_list(meta.get("source_names", "")),
        "source_chunks": _parse_list(meta.get("source_chunks", "")),
        "confidence": float(meta.get("confidence", 1.0)),
        "status": meta.get("status", "active"),
        "version": int(meta.get("version", 1)),
        "related_to": _parse_list(meta.get("related_to", "")),
        "conflicts_with": _parse_list(meta.get("conflicts_with", "")),
        "superseded_by": meta.get("superseded_by") or None,
        "created_at": meta.get("created_at", ""),
        "updated_at": meta.get("updated_at", ""),
    }


def add_atom(atom: KnowledgeAtom):
    col = _get_collection()
    col.add(
        ids=[atom.id],
        documents=[atom.content],
        metadatas=[_serialize(atom)],
    )


def update_atom(atom: KnowledgeAtom):
    col = _get_collection()
    col.update(
        ids=[atom.id],
        documents=[atom.content],
        metadatas=[_serialize(atom)],
    )


def update_atom_meta(atom_id: str, content: str, meta_updates: Dict[str, Any]):
    """Partial metadata update: load existing, merge, write back."""
    col = _get_collection()
    existing = col.get(ids=[atom_id], include=["documents", "metadatas"])
    if not existing["ids"]:
        return
    current_meta = dict(existing["metadatas"][0])
    current_meta.update(meta_updates)
    col.update(
        ids=[atom_id],
        documents=[content],
        metadatas=[current_meta],
    )


def get_atom_by_id(atom_id: str) -> Optional[dict]:
    col = _get_collection()
    results = col.get(ids=[atom_id], include=["documents", "metadatas"])
    if not results["ids"]:
        return None
    return _to_dict(results["ids"][0], results["documents"][0], results["metadatas"][0])


def find_similar(content: str, n_results: int = 5, threshold: float = 0.85) -> List[dict]:
    col = _get_collection()
    count = col.count()
    if count == 0:
        return []
    results = col.query(
        query_texts=[content],
        n_results=min(n_results, count),
        include=["documents", "metadatas", "distances"],
    )
    similar = []
    for i, doc in enumerate(results["documents"][0]):
        similarity = round(1 - results["distances"][0][i], 3)
        if similarity >= threshold:
            similar.append({
                **_to_dict(results["ids"][0][i], doc, results["metadatas"][0][i]),
                "similarity": similarity,
            })
    return similar


def search_atoms(query: str, atom_type: Optional[str] = None, n_results: int = 10) -> List[dict]:
    col = _get_collection()
    count = col.count()
    if count == 0:
        return []
    kwargs: dict = {
        "query_texts": [query],
        "n_results": min(n_results, count),
        "include": ["documents", "metadatas", "distances"],
    }
    if atom_type:
        kwargs["where"] = {"atom_type": atom_type}
    results = col.query(**kwargs)
    return [
        {
            **_to_dict(results["ids"][0][i], doc, results["metadatas"][0][i]),
            "relevance": round(1 - results["distances"][0][i], 3),
        }
        for i, doc in enumerate(results["documents"][0])
    ]


def get_all_atoms(atom_type: Optional[str] = None, status: Optional[str] = None) -> List[dict]:
    col = _get_collection()
    if col.count() == 0:
        return []
    where: dict = {}
    if atom_type and status:
        where = {"$and": [{"atom_type": atom_type}, {"status": status}]}
    elif atom_type:
        where = {"atom_type": atom_type}
    elif status:
        where = {"status": status}
    kwargs: dict = {"include": ["documents", "metadatas"]}
    if where:
        kwargs["where"] = where
    results = col.get(**kwargs)
    return [
        _to_dict(results["ids"][i], results["documents"][i], results["metadatas"][i])
        for i in range(len(results["ids"]))
    ]


def delete_atom(atom_id: str):
    _get_collection().delete(ids=[atom_id])


def get_atom_count() -> int:
    return _get_collection().count()
