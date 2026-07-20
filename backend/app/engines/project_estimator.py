from dataclasses import dataclass


@dataclass
class EstimationResult:
    estimated_hours: int
    complexity_tier: str
    risk: str


class ProjectEstimator:

    # Base hours for a bare-bones version of each project type — this is the starting
    # point before complexity and platform are factored in.
    BASE_PROJECT_HOURS = {
        "Landing Page": 12,
        "Portfolio Website": 20,
        "Dashboard": 35,
        "Ecommerce Website": 45,
        "CRM": 70,
        "ERP": 120,
        "SaaS": 80,
        "AI Application": 90,
        "Mobile App": 40,
        "Chat Application": 60,
        "LMS": 75,
    }

    # Instead of summing an hours cost per individual feature (which meant every new
    # feature name needed its own hand-tuned number, and made the price hard to explain
    # — "why does Wishlist cost exactly 6 hours?"), complexity is judged as a whole:
    # how many features there are, and whether any of them are inherently
    # harder-than-average to build well.
    COMPLEXITY_MULTIPLIER = {
        "Simple": 1.0,
        "Medium": 1.4,
        "Complex": 1.9,
        "Very Complex": 2.6,
    }

    PLATFORM_MULTIPLIER = {
        "Web": 1.0,
        "Android": 1.15,
        "iOS": 1.20,
        "Desktop": 1.05,
    }

    # Features that meaningfully raise complexity on their own — security-critical,
    # real-time, or AI/ML components genuinely take disproportionately longer to build
    # and test properly, regardless of how many OTHER features exist alongside them.
    HIGH_COMPLEXITY_SIGNALS = [
        "payment", "gateway", "ai", "chatbot", "machine learning", "recommendation",
        "real-time", "realtime", "video", "call", "booking", "inventory",
        "analytics", "notification",
    ]

    def estimate(self, requirements):

        base_hours = self.BASE_PROJECT_HOURS.get(requirements.project_type, 40)

        complexity_tier = self._complexity_tier(requirements)
        complexity_multiplier = self.COMPLEXITY_MULTIPLIER[complexity_tier]

        platform_multiplier = 1.0
        if requirements.platform:
            for platform in requirements.platform:
                platform_multiplier = max(
                    platform_multiplier,
                    self.PLATFORM_MULTIPLIER.get(platform, 1.0),
                )

        hours = int(base_hours * complexity_multiplier * platform_multiplier)

        risk = self._risk(hours)

        return EstimationResult(
            estimated_hours=hours,
            complexity_tier=complexity_tier,
            risk=risk,
        )

    def _complexity_tier(self, requirements) -> str:

        feature_count = len(requirements.features)

        high_complexity_count = sum(
            1
            for feature in requirements.features
            if any(signal in feature.lower() for signal in self.HIGH_COMPLEXITY_SIGNALS)
        )

        if feature_count <= 1 and high_complexity_count == 0:
            return "Simple"

        if feature_count <= 3 and high_complexity_count <= 1:
            return "Medium"

        if feature_count <= 6 and high_complexity_count <= 3:
            return "Complex"

        return "Very Complex"

    def _risk(self, hours):

        if hours < 50:
            return "Low"

        if hours < 120:
            return "Medium"

        return "High"