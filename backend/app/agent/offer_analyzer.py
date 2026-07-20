from dataclasses import dataclass


@dataclass
class OfferAnalysis:

    client_offer: float

    minimum_price: float

    recommended_price: float

    difference: float

    ratio: float

    decision: str


class OfferAnalyzer:

    def analyze(self, client_offer, pricing, last_counter=None):

        # If we've already conceded to some counter-offer in an earlier round, a client
        # meeting THAT number should close the deal — comparing only against the original
        # recommended_price meant the negotiation could never actually converge, since the
        # client meeting our own concession still looked like "below recommended -> COUNTER".
        accept_threshold = last_counter if last_counter is not None else pricing.recommended_price

        ratio = client_offer / pricing.recommended_price

        if client_offer >= accept_threshold:

            decision = "ACCEPT"

        elif client_offer >= pricing.minimum_price:

            decision = "COUNTER"

        else:

            decision = "REJECT"

        return OfferAnalysis(
            client_offer=client_offer,
            minimum_price=pricing.minimum_price,
            recommended_price=pricing.recommended_price,
            difference=pricing.recommended_price - client_offer,
            ratio=ratio,
            decision=decision,
        )