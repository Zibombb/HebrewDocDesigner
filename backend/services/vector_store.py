import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from typing import List
from backend.config import CHROMA_DIR
from backend.models.schemas import ContentChunk, SearchResult

_client = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _collection = _client.get_or_create_collection(
            name="book_content",
            embedding_function=DefaultEmbeddingFunction(),
            metadata={"hnsw:space": "cosine"}
        )
    return _collection


def add_chunks(chunks: List[ContentChunk]):
    collection = _get_collection()
    collection.add(
        ids=[c.id for c in chunks],
        documents=[c.text for c in chunks],
        metadatas=[{
            "topic": c.topic,
            "concepts": ", ".join(c.concepts),
            "chunk_type": c.chunk_type,
            "source_name": c.source_name,
        } for c in chunks]
    )


def search(query: str, n_results: int = 8, where: dict = None) -> List[SearchResult]:
    collection = _get_collection()
    count = collection.count()
    if count == 0:
        return []

    kwargs = {
        "query_texts": [query],
        "n_results": min(n_results, count),
    }
    if where:
        kwargs["where"] = where

    results = collection.query(**kwargs)
    output = []
    for i, doc in enumerate(results["documents"][0]):
        meta = results["metadatas"][0][i]
        distance = results["distances"][0][i]
        output.append(SearchResult(
            text=doc,
            topic=meta.get("topic", ""),
            source_name=meta.get("source_name", ""),
            relevance=round(1 - distance, 3),
        ))
    return output


def get_all_topics() -> List[str]:
    collection = _get_collection()
    if collection.count() == 0:
        return []
    results = collection.get(include=["metadatas"])
    topics = {m.get("topic", "") for m in results["metadatas"]}
    return sorted([t for t in topics if t])


def delete_source(source_name: str):
    collection = _get_collection()
    results = collection.get(
        where={"source_name": source_name},
        include=["metadatas"]
    )
    if results["ids"]:
        collection.delete(ids=results["ids"])


def get_collection_count() -> int:
    return _get_collection().count()
