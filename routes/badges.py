from fastapi import APIRouter

from models.badges import BadgesResponse
from services.hackerrank_service import HackerRankService

router = APIRouter()


@router.get("/{username}/badges", response_model=BadgesResponse)
async def get_user_badges(username: str) -> BadgesResponse:
    badges_response, error = await HackerRankService.get_user_badges(username)
    if error:
        return BadgesResponse.error("error", error)
    return badges_response
