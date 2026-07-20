from typing import List, Optional
from pydantic import BaseModel, Field


class ProjectRequirements(BaseModel):

    project_type: Optional[str] = None

    platform: List[str] = Field(default_factory=list)

    features: List[str] = Field(default_factory=list)

    deadline_days: Optional[int] = None

    # A range is more useful than one number — it gives the negotiation engine the
    # client's real ceiling immediately instead of guessing at it through several
    # rounds of back-and-forth. If the client only gives one number, budget_min and
    # budget_max are both set to it.
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None

    # Kept for backward compatibility with anything still reading requirements.budget
    # directly — always mirrors budget_max (the client's real ceiling).
    budget: Optional[float] = None

    # The client's own words describing the project, captured while discovery is still
    # asking about WHAT they want (before deadline/budget turn the conversation
    # numeric) — used in the proposal so it reads like a real project brief, not just a
    # list of extracted keywords.
    description: Optional[str] = None

