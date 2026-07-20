import json
import os
import re

from app.schemas.freelancer import FreelancerProfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
PROFILES_DIR = os.path.join(BASE_DIR, "storage", "profiles")


def _safe_filename(email: str) -> str:
    # Emails contain characters that aren't safe in filenames (@, .) — replace them
    # rather than trying to escape them.
    return re.sub(r"[^a-zA-Z0-9]", "_", email.lower()) + ".json"


class ProfileManager:
    """
    NOTE: I'm rewriting this from scratch — I've never actually seen your original
    profile_manager.py, only inferred its two-method interface (load/save) from how
    other files call it. The behavior should match (returns a FreelancerProfile,
    accepts one to save), but if your original had extra functionality I don't know
    about, tell me and I'll fold it in.
    """

    def __init__(self, user_email: str):
        os.makedirs(PROFILES_DIR, exist_ok=True)
        self.path = os.path.join(PROFILES_DIR, _safe_filename(user_email))

    def load(self) -> FreelancerProfile:
        if not os.path.exists(self.path):
            return FreelancerProfile()  # schema defaults — this user hasn't saved one yet
        with open(self.path, "r") as f:
            data = json.load(f)
        return FreelancerProfile(**data)

    def save(self, profile: FreelancerProfile):
        with open(self.path, "w") as f:
            json.dump(profile.model_dump(), f, indent=2)