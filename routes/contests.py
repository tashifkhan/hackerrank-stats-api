from fastapi import APIRouter

from models.contests import ContestRankingResponse
from services.hackerrank_service import HackerRankService

router = APIRouter()


@router.get("/{username}/contests", response_model=ContestRankingResponse)
async def get_contest_ranking(username: str) -> ContestRankingResponse:
    contest_response, error = await HackerRankService.get_contest_ranking(username)
    if error:
        return ContestRankingResponse.error("error", error)
    return contest_response
