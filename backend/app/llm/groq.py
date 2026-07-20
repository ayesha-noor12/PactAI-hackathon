from groq import Groq

from app.config import settings
from app.llm.base import BaseLLM


class GroqLLM(BaseLLM):

    def __init__(self):

        self.client = Groq(
            api_key=settings.GROQ_API_KEY
        )

        self.model = settings.GROQ_MODEL

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