from typing import List, Dict
from pydantic import BaseModel, Field


class FreelancerProfile(BaseModel):

    name: str = "PactAI Freelancer"

    title: str = "Full Stack Developer"

    experience: int = 3

    skills: List[str] = [
        "Python",
        "FastAPI",
        "React"
    ]

    hourly_rate: float = 40

    working_hours_per_day: int = 8

    minimum_profit_margin: float = 0.80

    preferred_projects: List[str] = [
        "Web Application",
        "Mobile App"
    ]

    currency: str = "USD"

    # "hourly" = price is calculated from estimated hours × hourly_rate (the original
    # model). "fixed_range" = price comes from the platform's min/max below, positioned
    # by project complexity — closer to real-world freelance-platform pricing, where you
    # set "web projects: $200-$800" once rather than reasoning about hours per feature.
    pricing_mode: str = "hourly"

    platform_price_ranges: Dict[str, Dict[str, float]] = Field(
        default_factory=lambda: {
            "Web": {"min": 200, "max": 1000},
            "Android": {"min": 300, "max": 1500},
            "iOS": {"min": 300, "max": 1500},
            "Desktop": {"min": 250, "max": 1200},
        }
    )