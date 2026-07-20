from abc import ABC, abstractmethod


class BaseLLM(ABC):

    @abstractmethod
    def chat(self, system_prompt: str, messages: list, temperature: float = 0.2):
        """
        Send a conversation to an LLM and return its response.

        temperature defaults to 0.2 (good for structured extraction, which needs
        reliable, repeatable JSON). Callers that want more natural, varied phrasing —
        like negotiation replies — should pass a higher value explicitly.
        """
        pass