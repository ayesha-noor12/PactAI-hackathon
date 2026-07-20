import re


class IntentGate:
    """
    Runs before discovery starts. Prevents the agent from launching into requirement
    questions the moment someone says "hi", and gives off-topic messages a polite
    deflection instead of forcing them through the negotiation pipeline.

    This is a cheap heuristic, not an LLM call — keeps the very first turn fast and free.
    If you want it smarter later, swap check() to a small Qwen classification call instead.
    """

    GREETING_PATTERN = re.compile(
        r"^\s*(hi+|hello+|hey+|hii+|salam|assalam|yo|good\s*(morning|evening|afternoon))\b",
        re.IGNORECASE,
    )

    PROJECT_INTENT_PATTERN = re.compile(
        r"\b(build|develop|create|design|need|want|looking for|make|working on)\b.*"
        r"\b(app|website|site|platform|system|project|application|dashboard|store|saas)\b",
        re.IGNORECASE,
    )

    GREETING_REPLY = "Hey! 👋 I'm PactAI. Tell me a bit about the project you'd like built and I'll help scope it out."
    OFF_TOPIC_REPLY = "That's a bit outside what I handle here — the freelancer will get back to you on that directly."

    def check(self, message: str, memory) -> str | None:
        """
        Returns a canned reply string if the message shouldn't go to discovery yet,
        or None if it should proceed normally.

        Only gates the very first turn of a session — once real requirements exist,
        every message goes through the normal pipeline even if it's short ("yes", "ok").
        """

        has_requirements = bool(
            memory.requirements.project_type or memory.requirements.features
        )
        if has_requirements:
            return None

        text = message.strip()

        if self.PROJECT_INTENT_PATTERN.search(text):
            return None  # looks like a real project request — let discovery handle it

        if self.GREETING_PATTERN.match(text):
            return self.GREETING_REPLY

        # Not a greeting and not project intent — likely small talk or unrelated.
        # Give discovery a chance on short, ambiguous first messages (e.g. "web app"
        # with no verb) rather than deflecting anything that isn't a perfect match.
        if len(text.split()) <= 3:
            return None

        return self.OFF_TOPIC_REPLY