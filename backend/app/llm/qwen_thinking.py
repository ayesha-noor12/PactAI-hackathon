from openai import OpenAI

from app.config import settings
from app.llm.base import BaseLLM


class QwenThinkingLLM(BaseLLM):
    """
    Same interface as QwenLLM, but uses a deep-thinking Qwen model (e.g. qwen3.7-max)
    with enable_thinking=True. Thinking models stream by design and separate the
    reasoning trace (delta.reasoning_content) from the final answer (delta.content).

    We discard the reasoning trace entirely and return only the final content, so every
    caller in the app (NegotiationAgent, LLMExtractor, NegotiationNLU) keeps working
    unchanged — they just get a plain string back, same as before.

    Trade-off: thinking models are slower and cost more per call (they generate the
    hidden reasoning tokens too, even though we throw them away) — worth confirming
    it's actually producing better negotiation replies before switching over
    permanently, rather than assuming "thinking" automatically means "smarter phrasing."
    """

    def __init__(self):

        self.client = OpenAI(
            api_key=settings.QWEN_API_KEY,
            base_url=settings.QWEN_BASE_URL,
        )

        self.model = settings.QWEN_THINKING_MODEL

    def chat(self, system_prompt: str, messages: list, temperature: float = 0.2):

        stream = self.client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                *messages,
            ],
            extra_body={"enable_thinking": True},
            stream=True,
        )

        answer_parts = []

        for chunk in stream:

            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            # reasoning_content is intentionally ignored — we only want the final
            # answer, not the model's internal thinking trace.
            if hasattr(delta, "content") and delta.content:
                answer_parts.append(delta.content)

        return "".join(answer_parts)