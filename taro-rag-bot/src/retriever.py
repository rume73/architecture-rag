import re
from dataclasses import dataclass

import chromadb
from sentence_transformers import SentenceTransformer

from .config import (
    CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL,
    TOP_K, SCORE_THRESHOLD,
)


SUSPICIOUS_PATTERNS = [
    r"ignore\s+all\s+instructions",
    r"ignore\s+previous",
    r"output\s*:",
    r"system\s*:",
    r"password\s*:",
    r"secret\s*:",
    r"swordfish",
    r"root\s*:",
    r"<\|.*?\|>",
    r"```.*?```",
]


def is_suspicious(text: str) -> bool:
    """Проверяет, содержит ли чанк подозрительные конструкции."""
    text_lower = text.lower()
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False


def filter_chunks(chunks):
    safe = []
    for c in chunks:
        if is_suspicious(c.text):
            print(f"[SECURITY] Отфильтрован чанк: {c.source} (score={c.score:.3f})")
            continue
        safe.append(c)
    return safe


@dataclass
class RetrievedChunk:
    text: str
    source: str
    title: str
    chunk_index: int
    score: float


class Retriever:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.collection = client.get_collection(COLLECTION_NAME)

    def search(self, query: str, top_k: int = TOP_K) -> list[RetrievedChunk]:
        emb = self.model.encode(
            [query], normalize_embeddings=True
        )[0].tolist()

        results = self.collection.query(
            query_embeddings=[emb],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        chunks = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            chunks.append(RetrievedChunk(
                text=doc,
                source=meta["source"],
                title=meta["title"],
                chunk_index=meta["chunk_index"],
                score=1 - dist,
            ))
        return chunks

    def search_filtered(self, query: str, top_k: int = TOP_K) -> list[RetrievedChunk]:
        chunks = self.search(query, top_k)
        return [c for c in chunks if c.score >= SCORE_THRESHOLD]
