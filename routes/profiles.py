from fastapi import APIRouter

from models.profiles import ProfileResponse
from services.hackerrank_service import HackerRankService

router = APIRouter()


@router.get("/{username}/profile", response_model=ProfileResponse)
async def get_user_profile(username: str) -> ProfileResponse:
    profile_response, error = await HackerRankService.get_user_profile(username)
    if error:
        return ProfileResponse.error("error", error)
    return profile_response
