from pydantic import BaseModel


class ChatRequest(BaseModel):

    session_id: str

    message: str


class ChatResponse(BaseModel):

    stage: str

    reply: str

    decision: str | None = None

    recommended_price: float | None = None

    minimum_price: float | None = None

    estimated_hours: int | None = None

    timeline_days: int | None = None