from app.prompts.negotiation_prompt import NEGOTIATION_PROMPT


class NegotiationAgent:

    def __init__(self, llm):
        self.llm = llm

    def negotiate(
        self,
        requirements,
        estimation,
        timeline,
        pricing,
        decision,
        client_message,
        intent,
        analysis=None,
        counter_offer=None,
        added_features=None,
        removed_features=None,
        current_standing_offer=None,
        timeline_changed=False,
        platform_changed=False,
        old_recommended_price=None,
        is_final_round=False,
    ):

        facts = f"""
PROJECT — use ONLY these exact facts. Never mention a platform, feature, or number that
isn't listed here — if only "Android" is listed, never say "iOS" or "cross-platform".

Type: {requirements.project_type}

Platform: {requirements.platform}

Features: {requirements.features}

Recommended Price: ${pricing.recommended_price}

Client's requested timeline: {requirements.deadline_days if requirements.deadline_days is not None else 'not specified'} days
"""

        # This is the actual fix for the "5 days" confusion that kept appearing despite
        # the client saying 30/90 days: this used to say `Timeline: {timeline.estimated_days}
        # days`, which is OUR OWN internal effort-days (hours ÷ working_hours_per_day) —
        # completely different from what the client asked for, and not something that
        # should ever reach the client-facing conversation. The LLM wasn't confused; it
        # was accurately repeating exactly what we told it every turn. Only the client's
        # actual stated deadline belongs in this prompt now.

        # The actual fix for "invented a discount for the extended timeline": the price
        # here is only allowed to change when we've genuinely recalculated it (workflow.py
        # updates memory.pricing for real when a new deadline is detected). This tells the
        # LLM exactly what changed and why, instead of leaving it to guess/fabricate a
        # justification.
        if timeline_changed:
            facts += f"""

TIMELINE JUST CHANGED — this is real, already recalculated, not something to invent

The client proposed a new deadline: {requirements.deadline_days} days.
Previous recommended price: ${old_recommended_price}
New recommended price (recalculated for the new timeline): ${pricing.recommended_price}

Explain this change honestly and briefly — the price moved because the timeline did,
not because of an arbitrary "discount." If the new price didn't actually change much,
don't invent a reason why it should have.
"""

        if platform_changed:
            facts += f"""

PLATFORM JUST CHANGED — this is real, already recalculated, not something to invent

The client narrowed the platform to: {requirements.platform}.
Previous recommended price: ${old_recommended_price}
New recommended price (recalculated for the new platform scope): ${pricing.recommended_price}

Explain this honestly and briefly — the price moved because the platform scope did.
Never mention a platform that isn't in the list above.
"""

        if current_standing_offer is not None:
            facts += f"""

CURRENT STANDING OFFER (this is what's actually on the table right now — not the
original recommended price above)

${current_standing_offer}
"""

        if added_features:

            facts += f"""

FEATURES ADDED

{', '.join(added_features)}

Updated Price

${pricing.recommended_price}
"""

        if removed_features:

            facts += f"""

FEATURES REMOVED

{', '.join(removed_features)}

Updated Price

${pricing.recommended_price}
"""

        if analysis:

            stance_guidance = {
                "ACCEPT": "Their offer meets your price. Accept warmly and confirm next steps.",
                "COUNTER": (
                    f"Their offer of ${analysis.client_offer} is below what you can accept. "
                    f"Counter at ${counter_offer} — explain the reasoning briefly. Never say "
                    f"the word 'decision', 'minimum', or 'floor' — just negotiate naturally "
                    f"without revealing where your walk-away point actually is."
                ),
                "REJECT": (
                    f"Their offer of ${analysis.client_offer} is quite low. Counter at "
                    f"${counter_offer} instead — explain briefly why, without stating any "
                    f"number as a fixed 'minimum' or hard floor. Just negotiate."
                ),
            }.get(analysis.decision, "")

            # This is what makes the tone actually firm/closing instead of sounding
            # like there's still room to move, once we've genuinely reached the last
            # round of the concession ladder without an agreement.
            if is_final_round:
                stance_guidance = (
                    f"This is the last round — you're not going to move further than "
                    f"${counter_offer}. Say plainly that this is your final offer: "
                    f"something like \"I hear you, but ${counter_offer} is the best I "
                    f"can do — let me know if that works.\" Don't soften it with more "
                    f"justification than a brief sentence, and don't invite further "
                    f"back-and-forth on the price specifically."
                )

            facts += f"""

INTERNAL GUIDANCE (do not repeat these numbers or labels verbatim — speak naturally)

Client's stated offer: ${analysis.client_offer}
{stance_guidance}
"""

        return self.llm.chat(
            system_prompt=NEGOTIATION_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": facts + "\n\nClient Message:\n" + client_message,
                }
            ],
            # Higher than the 0.2 default used for structured extraction — negotiation
            # replies benefit from more natural variation. This is part of the fix for
            # replies sounding robotic/repetitive.
            temperature=0.7,
        )