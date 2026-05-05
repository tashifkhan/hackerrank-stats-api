from fastapi import APIRouter

from models.stats import StatsResponse
from services.hackerrank_service import HackerRankService

router = APIRouter()


@router.get("/{username}", response_model=StatsResponse)
async def get_stats(username: str) -> StatsResponse:
    stats_response, error = await HackerRankService.get_user_stats(username)
    if error:
        return StatsResponse.error("error", error)
    return stats_response
