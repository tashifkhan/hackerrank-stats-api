from fastapi import APIRouter

from models.profiles import ProfileResponse
from models.unified import make_envelope
from services import unified_mapper
from services.hackerrank_service import HackerRankService

router = APIRouter()


@router.get("/{username}/profile")
async def get_user_profile(username: str):
    profile_response, error = await HackerRankService.get_user_profile(username)
    if error:
        return make_envelope(
            username,
            None,
            legacy=ProfileResponse.error("error", error),
            status="error",
            message=error,
        )

    data = unified_mapper.profile_from(profile_response, username)
    return make_envelope(username, data, legacy=profile_response)
