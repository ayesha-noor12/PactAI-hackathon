import re


class AgreementDetector:

    # \b word boundaries — this is the actual fix for the "okhay" bug: the old version
    # used `"ok" in text`, which matches inside "okhay", "okay-ish", "broken", etc.
    AGREEMENT_PATTERNS = [
        r"\bdeal\b",
        r"\bagreed\b",
        r"\bagree\b",
        r"\baccepted\b",
        r"\baccept\b",
        r"\bsounds good\b",
        r"\blooks good\b",
        r"\bperfect\b",
        r"\bokay\b",
        r"\bokhay\b",
        r"\bok\b",
        r"\bsure\b",
        r"\bgo ahead\b",
        r"\bproceed\b",
        r"\blet'?s proceed\b",
        r"\blet'?s do it\b",
        r"\bdone\b",
        r"\bconfirmed\b",
        r"\bconfirm\b",
        r"\bworks for me\b",
        r"\bi'?m happy\b",
        r"\bi am happy\b",
        r"\byes\b",
    ]

    NUMBER_PATTERN = re.compile(r"\d+(?:\.\d+)?")

    def is_agreement(self, message: str, memory=None) -> bool:

        text = message.lower().strip()

        has_agreement_word = any(
            re.search(pattern, text) for pattern in self.AGREEMENT_PATTERNS
        )

        if not has_agreement_word:
            return False

        # This is the second half of the fix: a message can contain an agreement word
        # AND a price that contradicts the current offer on the table (exactly what
        # happened in the transcript — "okhay ... within 200" after we'd countered at
        # $278.4). If the client states a number, it only counts as real agreement when
        # that number matches what's actually being offered right now.
        numbers = [float(n) for n in self.NUMBER_PATTERN.findall(text)]

        if numbers and memory is not None:

            current_offer = None

            if memory.counter_offers:
                current_offer = memory.counter_offers[-1]
            elif memory.pricing:
                current_offer = memory.pricing.recommended_price

            if current_offer is not None:
                tolerance = max(current_offer * 0.02, 1)  # ~2% wiggle room for rounding
                if not any(abs(n - current_offer) <= tolerance for n in numbers):
                    return False

        return True