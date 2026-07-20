class CounterOfferGenerator:

    # How many rounds of pushback before we settle at the floor.
    MAX_ROUNDS = 5

    def generate(self, analysis, round_number: int = 1):

        if analysis.decision == "ACCEPT":
            return analysis.client_offer

        # Both COUNTER and low REJECT-level offers get the SAME gradual step-down
        # toward the floor — we no longer jump straight to minimum_price the instant
        # someone lowballs us. That was revealing the floor number in one move instead
        # of negotiating down to it, which is exactly what a real negotiator wouldn't
        # do ("if total is $50 and they say $20, cut to $40 and negotiate from there").
        progress = min(round_number, self.MAX_ROUNDS) / self.MAX_ROUNDS
        span = analysis.recommended_price - analysis.minimum_price
        counter = analysis.recommended_price - (span * progress)

        # Never go below our floor, and never counter below the client's own offer.
        counter = max(counter, analysis.minimum_price, analysis.client_offer)

        return round(counter, 2)