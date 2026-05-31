from fastapi import APIRouter

from models.contests import ContestRankingResponse
from models.unified import make_envelope
from services import unified_mapper
from services.hackerrank_service import HackerRankService

router = APIRouter()


@router.get("/{username}/contests")
async def get_contest_ranking(username: str):
    contest_response, error = await HackerRankService.get_contest_ranking(username)
    if error:
        return make_envelope(
            username,
            None,
            legacy=ContestRankingResponse.error("error", error),
            status="error",
            message=error,
        )

    data = unified_mapper.contests_from(contest_response)
    return make_envelope(username, data, legacy=contest_response)
