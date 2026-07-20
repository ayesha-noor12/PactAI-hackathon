from app.llm.base import BaseLLM


class MockLLM(BaseLLM):

    def chat(self, system_prompt: str, messages: list):

        return """
Thanks for your project!

Before I estimate it, I need:

1. Required features
2. Target platform
3. Preferred deadline
4. Approximate budget
"""