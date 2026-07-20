from openai import OpenAI

from app.config import settings
from app.llm.base import BaseLLM


class QwenLLM(BaseLLM):

    def __init__(self):

        self.client = OpenAI(
            api_key=settings.QWEN_API_KEY,
            base_url=settings.QWEN_BASE_URL,
        )

        self.model = settings.QWEN_MODEL

    def chat(self, system_prompt: str, messages: list, temperature: float = 0.2):

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                *messages
            ]
        )

        return response.choices[0].message.content