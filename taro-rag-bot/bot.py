import sys
from src.rag_bot import RAGBot


def main():
    print("RAG-бот: The Paths")
    print("Введите вопрос или 'exit' для выхода")

    bot = RAGBot()
    from src.config import CHROMA_DIR, COLLECTION_NAME
    print(f"[DEBUG] CHROMA_DIR = {CHROMA_DIR}")
    print(f"[DEBUG] Существует: {CHROMA_DIR.exists()}")

    import chromadb
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    col = client.get_collection(COLLECTION_NAME)
    print(f"[DEBUG] Записей в коллекции: {col.count()}")

    while True:
        try:
            query = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nПока!")
            sys.exit(0)

        if not query:
            continue
        if query.lower() in ("exit", "quit", "выход"):
            print("Пока!")
            break

        result = bot.answer(query)

        print(result["answer"])

        if result["found"]:
            print("\nИсточники:")
            for i, c in enumerate(result["chunks"], 1):
                print(f"  [{i}] {c.source} (chunk {c.chunk_index}, score={c.score:.3f})")


if __name__ == "__main__":
    main()
