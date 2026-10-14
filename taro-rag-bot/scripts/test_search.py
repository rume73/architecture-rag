from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "index" / "chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_NAME = "knowledge_base"

QUERIES = [
    "What does the Rolling Vessel symbolize?",
    "Which element corresponds to Ember Staves?",
    "How does the Reckoning relate to transformation?",
]


def main():
    model = SentenceTransformer(EMBEDDING_MODEL)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_collection(COLLECTION_NAME)

    for query in QUERIES:
        print(f"\n{'=' * 60}")
        print(f"Запрос: {query}")
        print("=" * 60)

        emb = model.encode([query], normalize_embeddings=True)[0].tolist()

        results = collection.query(
            query_embeddings=[emb],
            n_results=5,
            include=["documents", "metadatas", "distances"],
        )

        for i, (doc, meta, dist) in enumerate(zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ), 1):
            score = 1 - dist
            print(f"\n[{i}] score={score:.4f} | {meta['source']} (chunk {meta['chunk_index']})")
            print(f"    {doc[:200]}...")


if __name__ == "__main__":
    main()
