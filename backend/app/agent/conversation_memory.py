from dataclasses import dataclass, field
from typing import List

from app.schemas.project import ProjectRequirements


@dataclass
class ConversationMemory:

    session_id: str | None = None  # set by SessionManager on creation

    owner_email: str | None = None  # which account this session belongs to

    stage: str = "DISCOVERY"

    messages: List[dict] = field(default_factory=list)

    requirements: ProjectRequirements = field(
        default_factory=ProjectRequirements
    )

    estimation = None
    timeline = None
    pricing = None
    decision = None

    offers: List[float] = field(default_factory=list)
    counter_offers: List[float] = field(default_factory=list)

    negotiation_round: int = 0
    decline_count: int = 0  # separate from negotiation_round — see workflow.py DECLINE branch
    agreement_reached: bool = False
    agreed_price: float | None = None
    agreed_timeline: int | None = None
    conversation_summary: str = ""

    proposal_id: str | None = None  # set once a proposal has been created for this session

    # Set when the client is offered a specific fork ("$570 with the chatbot, or $496
    # without it"). While this is set, a vague confirmation ("okay let's do it") gets
    # a clarifying question instead of silently locking onto whichever number happened
    # to be last in memory — that ambiguity was the actual bug being fixed here.
    pending_scope_offer: dict | None = None

    def add_client_message(self, text: str):

        self.messages.append(
            {
                "role": "user",
                "content": text
            }
        )

    def add_agent_message(self, text: str):

        self.messages.append(
            {
                "role": "assistant",
                "content": text
            }
        )

    def update(self, extracted):

        req = self.requirements

        if extracted.get("project_type"):
            req.project_type = extracted["project_type"]

        if extracted.get("platform"):
            req.platform = extracted["platform"]

        if extracted.get("features"):
            req.features = extracted["features"]

        if extracted.get("deadline_days") is not None:
            req.deadline_days = extracted["deadline_days"]

        if extracted.get("budget_min") is not None:
            req.budget_min = extracted["budget_min"]

        if extracted.get("budget_max") is not None:
            req.budget_max = extracted["budget_max"]

        # Legacy alias — always mirrors the client's real ceiling, for anything still
        # reading requirements.budget directly.
        if req.budget_max is not None:
            req.budget = req.budget_max