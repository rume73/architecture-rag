from .config import SCORE_THRESHOLD
from .llm_client import LLMClient
from .prompts import SYSTEM_PROMPT, build_user_prompt
from .retriever import Retriever


NOT_FOUND_MESSAGE = "Я не знаю. В базе знаний нет информации по этому вопросу."


class RAGBot:
    def __init__(self):
        self.retriever = Retriever()
        self.llm = LLMClient()

    def answer(self, query: str) -> dict:
        chunks_all = self.retriever.search(query)  # все чанки, без фильтра
        print(f"\n[DEBUG] Найдено чанков: {len(chunks_all)}")
        for i, c in enumerate(chunks_all, 1):
            print(f"  [{i}] score={c.score:.4f} | {c.source}")

        chunks = [c for c in chunks_all if c.score >= SCORE_THRESHOLD]
        print(f"[DEBUG] Прошли порог {SCORE_THRESHOLD}: {len(chunks)}")

        if not chunks:
            return {"answer": NOT_FOUND_MESSAGE, "chunks": [], "found": False}

        user_prompt = build_user_prompt(query, chunks)

        answer = self.llm.generate(SYSTEM_PROMPT, user_prompt)

        return {
            "answer": answer,
            "chunks": chunks,
            "found": True,
        }
