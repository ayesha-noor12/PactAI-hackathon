from dataclasses import dataclass
import math
from app.agent.profile_manager import ProfileManager


@dataclass
class TimelineResult:

    estimated_days: int
    requested_days: int

    developers_required: int

    status: str

    feasible: bool

    rush_multiplier: float

    recommendation: str


class TimelineEngine:

    def calculate(self, estimation, requirements, user_email):

        # Load the CURRENT profile on every call — same reasoning as PricingEngine,
        # now per-user for the same reason (see pricing_engine.py).
        profile = ProfileManager(user_email).load()

        estimated_days = math.ceil(
            estimation.estimated_hours /
            profile.working_hours_per_day
        )

        requested_days = requirements.deadline_days

        if requested_days is None:

            return TimelineResult(
                estimated_days=estimated_days,
                requested_days=estimated_days,
                developers_required=1,
                status="UNKNOWN",
                feasible=True,
                rush_multiplier=1.0,
                recommendation="Client has not specified a deadline."
            )

        ratio = requested_days / estimated_days

        developers = max(
            1,
            math.ceil(
                estimation.estimated_hours /
                (requested_days * profile.working_hours_per_day)
            )
        )

        if ratio >= 1.5:

            status = "COMFORTABLE"
            rush = 1.0
            feasible = True

            recommendation = (
                "Comfortable timeline. No rush fee required."
            )

        elif ratio >= 1.15:

            status = "TIGHT"
            rush = 1.10
            feasible = True

            recommendation = (
                "Timeline is slightly tight. Small scheduling buffer recommended."
            )

        elif ratio >= 0.85:

            status = "RUSH"
            rush = 1.25
            feasible = True

            recommendation = (
                "Rush project. Additional charges are recommended."
            )

        else:

            status = "IMPOSSIBLE"
            rush = 1.50
            feasible = False

            recommendation = (
                f"The requested deadline requires "
                f"{developers} developers "
                f"or a longer delivery schedule."
            )

        return TimelineResult(
            estimated_days=estimated_days,
            requested_days=requested_days,
            developers_required=developers,
            status=status,
            feasible=feasible,
            rush_multiplier=rush,
            recommendation=recommendation
        )