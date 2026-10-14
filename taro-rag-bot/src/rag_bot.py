import re

from .llm_client import LLMClient
from .prompts import SYSTEM_PROMPT, build_user_prompt
from .retriever import Retriever, filter_chunks

NOT_FOUND_MESSAGE = "Я не знаю. В базе знаний нет информации по этому вопросу."
SAFE_REFUSAL = "Извините, я не могу ответить на этот вопрос. Он содержит потенциально небезопасный запрос."


def check_response_safety(answer: str) -> tuple[bool, str]:
    dangerous_patterns = [
        (r"swordfish", "утечка пароля из malicious-документа"),
        (r"пароль\s*root", "утечка root-пароля"),
        (r"password\s*:", "вывод пароля"),
        (r"ignore\s+all\s+instructions", "эхо prompt-injection"),
    ]
    for pattern, reason in dangerous_patterns:
        if re.search(pattern, answer, re.IGNORECASE):
            return False, reason
    return True, ""


class RAGBot:
    def __init__(self):
        self.retriever = Retriever()
        self.llm = LLMClient()

    def answer(self, query: str) -> dict:
        chunks = self.retriever.search_filtered(query)
        chunks = filter_chunks(chunks)

        if not chunks:
            return {"answer": NOT_FOUND_MESSAGE, "chunks": [], "found": False}

        user_prompt = build_user_prompt(query, chunks)
        raw_answer = self.llm.generate(SYSTEM_PROMPT, user_prompt)

        safe, reason = check_response_safety(raw_answer)
        if not safe:
            print(f"[SECURITY] Ответ заблокирован: {reason}")
            return {"answer": SAFE_REFUSAL, "chunks": [], "found": False, "blocked": True}

        return {"answer": raw_answer, "chunks": chunks, "found": True}
