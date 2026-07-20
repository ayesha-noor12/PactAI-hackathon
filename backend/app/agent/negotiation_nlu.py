import json
from dataclasses import dataclass

from app.prompts.negotiation_nlu_prompt import NEGOTIATION_NLU_PROMPT


@dataclass
class NLUResult:
    intent: str
    price_offer: float | None
    timeline_days_offer: float | None
    platform_update: list[str] | None
    is_final_agreement: bool
    wants_scope_change: bool


class NegotiationNLU:
    """
    Uses the LLM itself to understand a client's message during negotiation, instead of
    regex/keyword matching. This is what a real negotiator does naturally: reads intent
    from context, not from spotting magic words. It's also what kept breaking — "okhay",
    "extent" (typo for extend), "we can extend the timeline" all needed individual regex
    patches because keyword matching has no actual understanding of what's being said.

    Falls back to the regex-based AgreementDetector/IntentAnalyzer (passed in by the
    caller) if this LLM call fails or returns something unparseable, so a flaky response
    never breaks a negotiation turn outright.
    """

    def __init__(self, llm):
        self.llm = llm

    def analyze(self, message: str, memory) -> NLUResult | None:

        context = f"""
Current standing offer on the table: {memory.counter_offers[-1] if memory.counter_offers else 'none yet — no counter has been made'}
Recommended price: {memory.pricing.recommended_price if memory.pricing else 'unknown'}

Client message:
{message}
"""

        try:
            raw = self.llm.chat(
                system_prompt=NEGOTIATION_NLU_PROMPT,
                messages=[{"role": "user", "content": context}],
                temperature=0.1,  # classification should be consistent, not creative
            )

            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.strip("`")
                if cleaned.lower().startswith("json"):
                    cleaned = cleaned[4:].strip()

            data = json.loads(cleaned)

            return NLUResult(
                intent=data.get("intent", "GENERAL"),
                price_offer=data.get("price_offer"),
                timeline_days_offer=data.get("timeline_days_offer"),
                platform_update=data.get("platform_update"),
                is_final_agreement=bool(data.get("is_final_agreement", False)),
                wants_scope_change=bool(data.get("wants_scope_change", False)),
            )

        except Exception:
            return None