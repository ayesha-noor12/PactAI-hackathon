import re

DOLLAR_PATTERN = re.compile(r"\$\s?([\d,]+(?:\.\d+)?)")


def extract_dollar_amounts(text: str) -> list[float]:
    return [float(m.replace(",", "")) for m in DOLLAR_PATTERN.findall(text)]


def _close(a: float, b: float, tolerance_ratio: float = 0.02) -> bool:
    return abs(a - b) <= max(b * tolerance_ratio, 1)


def reply_is_grounded(reply: str, allowed_values: list[float | None], tolerance_ratio=0.02) -> bool:
    """Every dollar figure in the reply must match a real number we actually provided."""

    amounts = extract_dollar_amounts(reply)

    if not amounts:
        return True

    allowed = [v for v in allowed_values if v is not None]

    if not allowed:
        return False

    return all(any(_close(a, v, tolerance_ratio) for v in allowed) for a in amounts)


def reply_matches_current_offer(
    reply: str,
    current_standing_offer: float | None,
    recommended_price: float | None,
    tolerance_ratio: float = 0.02,
) -> bool:
    """
    Catches a subtler failure than reply_is_grounded: the LLM reverting to the ORIGINAL
    recommended price after we've already conceded to a lower counter. $744 is a "real"
    number (it passes the basic grounding check above) but it's contextually wrong once
    negotiation has moved past it — this is what happened when "$327.36 on the table"
    silently became "$744" again in the same reply.
    """

    if current_standing_offer is None or recommended_price is None:
        return True

    if _close(current_standing_offer, recommended_price, tolerance_ratio):
        return True  # no concession has happened yet, nothing to regress from

    amounts = extract_dollar_amounts(reply)

    if not amounts:
        return True

    mentions_recommended = any(_close(a, recommended_price, tolerance_ratio) for a in amounts)
    mentions_current = any(_close(a, current_standing_offer, tolerance_ratio) for a in amounts)

    # Reverting to the original price WITHOUT even mentioning the current standing
    # offer is the regression we're guarding against.
    return not (mentions_recommended and not mentions_current)


def safe_fallback_reply(pricing, counter_offer=None, client_offer=None) -> str:
    """Deterministic, always-correct reply used when the LLM's response fails validation."""

    if counter_offer is not None:
        return (
            f"I hear you, but I can only work within the numbers we've actually discussed. "
            f"My current offer stands at ${counter_offer}. Let me know if that works, or if "
            f"you'd like to adjust scope or timeline instead."
        )

    # No counter established yet — reference the recommended price only. Never mention
    # the floor/minimum here; that number should never be stated to the client outright.
    return (
        f"Thanks for the details. Based on the scope, my price for this is "
        f"${pricing.recommended_price}. Let me know how you'd like to proceed."
    )