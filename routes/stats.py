from fastapi import APIRouter

from models.stats import StatsResponse
from models.unified import make_envelope
from services import unified_mapper
from services.hackerrank_service import HackerRankService

router = APIRouter()


@router.get("/{username}")
async def get_stats(username: str):
    stats_response, error = await HackerRankService.get_user_stats(username)
    if error:
        return make_envelope(
            username,
            None,
            legacy=StatsResponse.error("error", error),
            status="error",
            message=error,
        )

    data = unified_mapper.stats_from(
        stats_response, await unified_mapper._topics(username)
    )
    return make_envelope(username, data, legacy=stats_response)
