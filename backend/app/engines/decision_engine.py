from dataclasses import dataclass
from enum import Enum


class DecisionType(str, Enum):

    ACCEPT = "ACCEPT"

    COUNTER = "COUNTER"

    REJECT = "REJECT"


@dataclass
class DecisionResult:

    decision: DecisionType

    counter_offer: float | None

    confidence: float

    reasons: list[str]

    next_action: str


class DecisionEngine:

    def decide(
        self,
        requirements,
        estimation,
        pricing,
        timeline
    ):

        reasons = []

        # -----------------------
        # Impossible deadline
        # -----------------------

        if not timeline.feasible:

            reasons.append(
                "Requested deadline is not feasible."
            )

            return DecisionResult(
                decision=DecisionType.COUNTER,
                counter_offer=pricing.recommended_price,
                confidence=0.98,
                reasons=reasons,
                next_action="Suggest extending the deadline or increasing the budget."
            )

        # -----------------------
        # Client budget range
        # -----------------------

        # budget_max is the client's real ceiling — knowing it up front (instead of
        # discovering it through several rounds of counter-offers) is what makes the
        # negotiation faster. budget_min is informational: how much room they likely
        # have between what they'd prefer to pay and what they can actually stretch to.
        budget_max = requirements.budget_max if requirements.budget_max is not None else 0
        budget_min = requirements.budget_min if requirements.budget_min is not None else budget_max

        if budget_max >= pricing.recommended_price:

            reasons.append(
                "Client's budget ceiling fully covers the recommended price."
            )

            return DecisionResult(
                decision=DecisionType.ACCEPT,
                counter_offer=None,
                confidence=0.99,
                reasons=reasons,
                next_action="Accept the project."
            )

        if budget_max >= pricing.minimum_price:

            reasons.append(
                "Client's budget ceiling is within the negotiable range."
            )

            return DecisionResult(
                decision=DecisionType.COUNTER,
                # Counter close to their actual stated ceiling rather than the full
                # recommended price — we already know that number from the range they
                # gave us, no need to negotiate blind toward discovering it.
                counter_offer=round(
                    max(budget_max, pricing.minimum_price), 2
                ),
                confidence=0.95,
                reasons=reasons,
                next_action="Counter close to the client's stated budget ceiling."
            )

        gap = pricing.minimum_price - budget_max

        if gap < pricing.minimum_price * 0.20:

            reasons.append(
                "Client's budget ceiling is slightly below the minimum acceptable price."
            )

            return DecisionResult(
                decision=DecisionType.COUNTER,
                counter_offer=pricing.minimum_price,
                confidence=0.90,
                reasons=reasons,
                next_action="Counter at the lowest acceptable price."
            )

        reasons.append(
            "Client's budget range is far below the acceptable price."
        )

        return DecisionResult(
            decision=DecisionType.REJECT,
            counter_offer=None,
            confidence=0.99,
            reasons=reasons,
            next_action="Politely explain the gap and suggest reducing scope or extending timeline."
        )