from datetime import datetime


class ProposalGenerator:

    def generate(
        self,
        requirements,
        estimation,
        pricing,
        timeline,
        freelancer=None,
        agreed_price=None,
        agreed_timeline=None,
    ):

        freelancer_name = (
            freelancer.name
            if freelancer else
            "PactAI Freelancer"
        )

        skills = (
            ", ".join(freelancer.skills)
            if freelancer else
            "Full Stack Development"
        )

        final_price = agreed_price if agreed_price is not None else pricing.recommended_price
        final_timeline = agreed_timeline if agreed_timeline is not None else timeline.estimated_days

        # Falls back to a short generated line only if the client never actually
        # described anything beyond bare keywords (rare, but possible if discovery was
        # answered in single words the whole way through).
        description = requirements.description or (
            f"A {requirements.project_type or 'project'} for "
            f"{'/'.join(requirements.platform) or 'the requested platform'}, covering "
            f"{', '.join(requirements.features) or 'the features discussed'}."
        )

        proposal = f"""
==========================================
            PROJECT PROPOSAL
==========================================

Prepared By:
{freelancer_name}

Skills:
{skills}

Date:
{datetime.now().strftime("%d %B %Y")}

------------------------------------------
PROJECT
------------------------------------------

Type:
{requirements.project_type}

Platform:
{", ".join(requirements.platform)}

Features:
"""

        for feature in requirements.features:
            proposal += f"\n  • {feature}"

        proposal += f"""

Description:
{description.strip()}

------------------------------------------
ESTIMATION
------------------------------------------

Estimated Hours:
{estimation.estimated_hours}

Timeline:
{final_timeline} Days

------------------------------------------
PRICE
------------------------------------------

Agreed Price:
${final_price}

(Originally recommended: ${pricing.recommended_price}, floor: ${pricing.minimum_price})

------------------------------------------
DELIVERABLES
------------------------------------------

✓ Complete Source Code

✓ Documentation

✓ Deployment Support

✓ Bug Fixes

------------------------------------------
PAYMENT TERMS
------------------------------------------

30% Advance

70% On Completion

------------------------------------------
Thank you for choosing PactAI.
"""

        return proposal