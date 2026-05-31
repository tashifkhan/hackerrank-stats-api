from fastapi import APIRouter

from models.badges import BadgesResponse
from models.unified import make_envelope
from services import unified_mapper
from services.hackerrank_service import HackerRankService

router = APIRouter()


@router.get("/{username}/badges")
async def get_user_badges(username: str):
    badges_response, error = await HackerRankService.get_user_badges(username)
    if error:
        return make_envelope(
            username,
            None,
            legacy=BadgesResponse.error("error", error),
            status="error",
            message=error,
        )

    data = unified_mapper.badges_from(badges_response)
    return make_envelope(username, data, legacy=badges_response)
