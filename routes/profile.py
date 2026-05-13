from fastapi import APIRouter

from models.profiles import ProfileResponse
from models.canonical import make_envelope
from services import canonical_mapper
from services.profile import get_user_profile as fetch_user_profile


router = APIRouter(tags=["Canonical"])


@router.get("/{username}/profile")
async def get_user_profile(username: str):
    profile_response, error = await fetch_user_profile(username)
    if error:
        return make_envelope(username, None, legacy=ProfileResponse.error("error", error), status="error", message=error)

    data = canonical_mapper.profile_from(profile_response, username)
    return make_envelope(username, data, legacy=profile_response)
