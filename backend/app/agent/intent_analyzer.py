import re
from dataclasses import dataclass


@dataclass
class IntentResult:

    intent: str

    offer: float | None = None


class IntentAnalyzer:

    PRICE_WORDS = [
        "budget",
        "price",
        "cost",
        "offer",
        "$",
        "usd",
        "dollar",
    ]

    ACCEPT_WORDS = [
        r"\bdeal\b",
        r"\bagreed\b",
        r"\baccept\b",
        r"\bsounds good\b",
        r"\blet'?s do it\b",
        r"\bokay\b",
        r"\bokhay\b",
        r"\bok\b",
        r"\bsure\b",
    ]

    SCOPE_WORDS = [
        r"\bremove\b",
        r"\bfeature\b",
        r"\bscope\b",
        r"\bless\b",
        r"\bwithout\b",
    ]

    # A bare decline ("no", "nah") carries no new information about what the client
    # actually wants — repeating the same pitch verbatim (which is what happened in
    # testing) isn't useful. Recognizing it lets the workflow ask a clarifying question
    # instead of re-pitching identical text.
    DECLINE_PATTERNS = [
        r"^no\.?$",
        r"^nah\.?$",
        r"^nope\.?$",
        r"^not really\.?$",
        r"^no thanks\.?$",
    ]

    # Fixed: \bmonth\b / \bweek\b never matched "months" / "weeks" (plural) since \b
    # requires a boundary right after the word — "month" followed by "s" has no boundary
    # there. This is exactly why "3 months" got read as a $3 price offer. Added `s?`.
    TIMELINE_WORDS = [
        r"\bdeadline\b",
        r"\bweeks?\b",
        r"\bmonths?\b",
        r"\bdays?\b",
        r"\bextend\b",
        r"\blater\b",
    ]

    def analyze(self, message):

        text = message.lower().strip()

        has_currency_marker = any(w in text for w in self.PRICE_WORDS)
        has_timeline_marker = any(re.search(p, text) for p in self.TIMELINE_WORDS)

        number_match = re.search(r"\$?\s*(\d+(?:\.\d+)?)", text)

        if number_match and has_timeline_marker and not has_currency_marker:
            return IntentResult("TIMELINE")

        if number_match and (has_currency_marker or not has_timeline_marker):
            return IntentResult("PRICE", float(number_match.group(1)))

        if any(re.search(p, text) for p in self.DECLINE_PATTERNS):
            return IntentResult("DECLINE")

        if any(re.search(p, text) for p in self.ACCEPT_WORDS):
            return IntentResult("ACCEPT")

        if any(re.search(p, text) for p in self.SCOPE_WORDS):
            return IntentResult("SCOPE")

        if has_timeline_marker:
            return IntentResult("TIMELINE")

        if "?" in text:
            return IntentResult("QUESTION")

        return IntentResult("GENERAL")