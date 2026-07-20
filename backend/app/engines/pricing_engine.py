from dataclasses import dataclass

from app.agent.profile_manager import ProfileManager


@dataclass
class PricingResult:
    estimated_hours: int
    hourly_rate: float
    base_price: float
    rush_multiplier: float
    recommended_price: float
    minimum_price: float
    discount_limit: float


# Where each complexity tier lands within the freelancer's platform min/max range.
# Simple sits right at the floor, Very Complex sits at the ceiling, the middle tiers
# interpolate between them.
COMPLEXITY_POSITION = {
    "Simple": 0.0,
    "Medium": 0.35,
    "Complex": 0.65,
    "Very Complex": 1.0,
}

DEFAULT_PRICE_RANGE = {"min": 200, "max": 1000}


class PricingEngine:

    def calculate(self, estimation, requirements, timeline, user_email):

        # Loaded fresh every call, not cached at construction time — see the earlier
        # fix for why (profile edits weren't reaching pricing when this was cached in
        # __init__). Now also per-user, since ProfileManager needs to know whose
        # profile to load — otherwise every account would price off the same profile.
        profile = ProfileManager(user_email).load()

        if getattr(profile, "pricing_mode", "hourly") == "fixed_range":
            return self._calculate_fixed_range(profile, estimation, requirements, timeline)

        return self._calculate_hourly(profile, estimation, timeline)

    def _calculate_hourly(self, profile, estimation, timeline):

        hourly_rate = profile.hourly_rate

        base_price = estimation.estimated_hours * hourly_rate

        rush_multiplier = timeline.rush_multiplier

        recommended_price = base_price * rush_multiplier

        minimum_price = recommended_price * profile.minimum_profit_margin

        discount_limit = recommended_price - minimum_price

        return PricingResult(
            estimated_hours=estimation.estimated_hours,
            hourly_rate=hourly_rate,
            base_price=round(base_price, 2),
            rush_multiplier=rush_multiplier,
            recommended_price=round(recommended_price, 2),
            minimum_price=round(minimum_price, 2),
            discount_limit=round(discount_limit, 2),
        )

    def _calculate_fixed_range(self, profile, estimation, requirements, timeline):

        platform = requirements.platform[0] if requirements.platform else "Web"

        price_range = profile.platform_price_ranges.get(platform, DEFAULT_PRICE_RANGE)
        range_min = price_range.get("min", DEFAULT_PRICE_RANGE["min"])
        range_max = price_range.get("max", DEFAULT_PRICE_RANGE["max"])

        position = COMPLEXITY_POSITION.get(estimation.complexity_tier, 0.5)
        base_price = range_min + (range_max - range_min) * position

        rush_multiplier = timeline.rush_multiplier
        recommended_price = base_price * rush_multiplier

        # The freelancer's own stated floor for this platform IS the minimum — no
        # separate margin calculation needed, since they already told us the lowest
        # they'd take for a project on this platform.
        minimum_price = range_min

        discount_limit = recommended_price - minimum_price

        return PricingResult(
            estimated_hours=estimation.estimated_hours,
            hourly_rate=profile.hourly_rate,  # kept for display; not what drives price here
            base_price=round(base_price, 2),
            rush_multiplier=rush_multiplier,
            recommended_price=round(recommended_price, 2),
            minimum_price=round(minimum_price, 2),
            discount_limit=round(discount_limit, 2),
        )