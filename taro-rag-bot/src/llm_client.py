from openai import OpenAI

from .config import (
    LLM_PROVIDER,
    YANDEX_API_KEY,
    YANDEX_FOLDER_ID,
)


class LLMClient:
    def __init__(self):
        self.provider = LLM_PROVIDER
        self.client = OpenAI(
            api_key=YANDEX_API_KEY,
            base_url="https://llm.api.cloud.yandex.net/v1",
        )
        self.model = f"gpt://{YANDEX_FOLDER_ID}/yandexgpt/latest"

    def generate(self, system: str, user: str, temperature: float = 0.2) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_tokens=800,
        )
        return response.choices[0].message.content.strip()