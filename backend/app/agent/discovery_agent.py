from app.agent.llm_extractor import LLMExtractor


class DiscoveryAgent:

    REQUIRED_FIELDS = [
        "project_type",
        "platform",
        "features",
        "deadline_days",
        "budget_min",
    ]

    def __init__(self, llm):

        self.extractor = LLMExtractor(llm)

    def process(self, conversation, memory):

        req = memory.requirements

        # Capture the client's own description while we're still asking about WHAT
        # they want — before deadline/budget exist, since those turn the conversation
        # numeric rather than descriptive. Used later in the proposal so it reads like
        # a real project brief instead of just extracted keywords.
        if req.deadline_days is None and req.budget_min is None:
            req.description = (
                (req.description + " " if req.description else "") + conversation.strip()
            )

        memory.add_client_message(conversation)

        extracted = self.extractor.extract(conversation)

        memory.update(extracted)

        missing = self.get_missing(memory)

        if not missing:

            return {
                "status": "READY_FOR_ESTIMATION",
                "requirements": memory.requirements
            }

        question = self.next_question(memory, missing)

        return {
            "status": "DISCOVERY",
            "requirements": memory.requirements,
            "missing": missing,
            "question": question
        }

    def get_missing(self, memory):

        req = memory.requirements

        missing = []

        if not req.project_type:
            missing.append("project_type")

        if not req.platform:
            missing.append("platform")

        if not req.features:
            missing.append("features")

        if req.deadline_days is None:
            missing.append("deadline_days")

        if req.budget_min is None:
            missing.append("budget_min")

        return missing

    def next_question(self, memory, missing):

        req = memory.requirements

        # Phrased more openly on purpose — a broad question ("tell me about the idea,
        # any specific requirements") often gets project_type AND some features AND
        # sometimes platform in one answer, since extraction runs on the full message
        # every turn regardless of which single field this question is nominally
        # asking about. That means fewer total back-and-forth turns, not just nicer
        # wording.
        if "project_type" in missing:
            return (
                "Tell me a bit about the project — what's the idea, and what kind of "
                "site or app are you thinking? Any specific requirements you already "
                "have in mind?"
            )

        if "platform" in missing:
            return "Got it — is this for web, mobile (Android/iOS), or desktop?"

        if "features" in missing:

            if req.project_type == "Ecommerce Website":
                return (
                    "What are the must-have features for the store? Things like "
                    "customer login, cart, payment, an admin dashboard, order "
                    "tracking — whatever's core to what you have in mind."
                )

            if req.project_type == "Portfolio Website":
                return (
                    "What should it include — a contact form, blog, gallery, or "
                    "something you can update yourself later on?"
                )

            if req.project_type == "Mobile App":
                return "What are the main things the app needs to do?"

            return "What are the must-have features for this?"

        if "deadline_days" in missing:
            return "What's your timeline — when would you like this live?"

        if "budget_min" in missing:
            return (
                "What's your budget range for this project? "
                "(e.g. \"$500 to $800\" — or just one number if you have a fixed budget)"
            )

        return "Anything else I should know before I put together the numbers?"