from fastapi import APIRouter

from models.badges import BadgesResponse
from models.canonical import make_envelope
from services import canonical_mapper
from services.badges import get_user_badges as fetch_user_badges

router = APIRouter(tags=["Canonical"])


@router.get("/{username}/badges")
async def get_user_badges(username: str):
    badges_response, error = await fetch_user_badges(username)
    if error:
        return make_envelope(
            username,
            None,
            legacy=BadgesResponse.error("error", error),
            status="error",
            message=error,
        )

    data = canonical_mapper.badges_from(badges_response)
    return make_envelope(username, data, legacy=badges_response)
