import json
import re

from app.prompts.extraction_prompt import REQUIREMENT_EXTRACTION_PROMPT


class LLMExtractor:

    def __init__(self, llm):
        self.llm = llm

    def extract(self, conversation):

        # Accept either a string or a list of messages
        if isinstance(conversation, str):

            messages = [
                {
                    "role": "user",
                    "content": conversation
                }
            ]

        else:

            messages = conversation

        response = self.llm.chat(
            system_prompt=REQUIREMENT_EXTRACTION_PROMPT,
            messages=messages
        )

        return self._parse_response(response)

    def _parse_response(self, response):

        cleaned = response.strip()

        cleaned = re.sub(r"^```json", "", cleaned)
        cleaned = re.sub(r"^```", "", cleaned)
        cleaned = re.sub(r"```$", "", cleaned)

        cleaned = cleaned.strip()

        try:

            data = json.loads(cleaned)

        except Exception:

            data = {
                "project_type": None,
                "platform": [],
                "features": [],
                "deadline_days": None,
                "budget": None,
                "missing": [
                    "project_type",
                    "platform",
                    "features",
                    "deadline_days",
                    "budget"
                ]
            }

        return self.normalize(data)

    def normalize(self, data):

        defaults = {
            "project_type": None,
            "platform": [],
            "features": [],
            "deadline_days": None,
            "budget": None,
            "missing": []
        }

        for key, value in defaults.items():

            if key not in data:
                data[key] = value

        if not isinstance(data["platform"], list):
            data["platform"] = [data["platform"]]

        if not isinstance(data["features"], list):
            data["features"] = [data["features"]]

        return data