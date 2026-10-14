import json
import time
from pathlib import Path

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent.parent
KB_DIR = BASE_DIR / "knowledge_base"
INDEX_DIR = BASE_DIR / "index"
CHROMA_DIR = INDEX_DIR / "chroma_db"
CHUNKS_FILE = INDEX_DIR / "chunks.jsonl"
STATS_FILE = INDEX_DIR / "index_stats.json"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_NAME = "knowledge_base"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 75


def load_documents():
    """Читает все .md из knowledge_base, возвращает список (path, text)."""
    docs = []
    for md_file in KB_DIR.rglob("*.md"):
        if md_file.name == "README.md":
            continue
        with open(md_file, "r", encoding="utf-8") as f:
            text = f.read()
        if text.strip():
            rel_path = md_file.relative_to(KB_DIR)
            docs.append((str(rel_path), text))
    return docs


def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=300,
        separators=["\n## ", "\n\n", "\n", ". ", " ", ""],
    )

    chunks = []
    for rel_path, text in docs:
        title = text.split("\n", 1)[0].lstrip("# ").strip()

        for i, chunk_text in enumerate(splitter.split_text(text)):
            chunks.append({
                "id": f"{rel_path}::{i}",
                "text": chunk_text,
                "metadata": {
                    "source": rel_path,
                    "title": title,
                    "chunk_index": i,
                },
            })
    return chunks


def build_embeddings(chunks, model):
    texts = [c["text"] for c in chunks]
    print(f"Генерация эмбеддингов для {len(texts)} чанков...")

    start = time.time()
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    elapsed = time.time() - start
    print(f"Готово за {elapsed:.1f} с ({len(texts)/elapsed:.1f} чанков/с)")
    return embeddings, elapsed


def save_chunks_jsonl(chunks):
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")


def build_chroma_index(chunks, embeddings):
    if CHROMA_DIR.exists():
        import shutil
        shutil.rmtree(CHROMA_DIR)

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    collection.add(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks],
        embeddings=embeddings.tolist(),
    )

    print(f"ChromaDB: {collection.count()} записей в {CHROMA_DIR}")
    return collection


def save_stats(chunks, embedding_time, model_name, dim):
    stats = {
        "model": model_name,
        "embedding_dim": dim,
        "total_chunks": len(chunks),
        "embedding_time_sec": round(embedding_time, 2),
        "chunk_size_tokens": CHUNK_SIZE,
        "chunk_overlap_tokens": CHUNK_OVERLAP,
        "documents": len(set(c["metadata"]["source"] for c in chunks)),
    }
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    return stats


def main():
    print("Создание векторного индекса")

    print("\n[1/5] Загрузка документов...")
    docs = load_documents()
    print(f"  Найдено {len(docs)} документов")

    print("\n[2/5] Чанкинг...")
    chunks = split_documents(docs)
    print(f"  Получено {len(chunks)} чанков")

    print(f"\n[3/5] Загрузка модели {EMBEDDING_MODEL}...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    dim = model.get_sentence_embedding_dimension()
    print(f"  Размерность: {dim}")

    print("\n[4/5] Генерация эмбеддингов...")
    embeddings, emb_time = build_embeddings(chunks, model)

    print("\n[5/5] Сохранение...")
    save_chunks_jsonl(chunks)
    print(f"  Чанки: {CHUNKS_FILE}")
    build_chroma_index(chunks, embeddings)
    stats = save_stats(chunks, emb_time, EMBEDDING_MODEL, dim)
    print(f"  Статистика: {STATS_FILE}")

    print("\n" + "=" * 60)
    print("Готово!")
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
