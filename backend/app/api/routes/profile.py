from fastapi import APIRouter, Depends

from app.schemas.freelancer import FreelancerProfile
from app.agent.profile_manager import ProfileManager
from app.api.routes.deps import get_current_user_email

router = APIRouter()


@router.get("/profile")
def get_profile(user_email: str = Depends(get_current_user_email)):
    return ProfileManager(user_email).load()


@router.post("/profile")
def update_profile(
    profile: FreelancerProfile,
    user_email: str = Depends(get_current_user_email),
):
    ProfileManager(user_email).save(profile)
    return {
        "message": "Profile updated successfully.",
        "profile": profile,
    }