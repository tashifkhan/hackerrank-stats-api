from fastapi import APIRouter

from models.contests import ContestRankingResponse
from models.canonical import make_envelope
from services import canonical_mapper
from services.contests import get_contest_ranking as fetch_contest_ranking

router = APIRouter(tags=["Canonical"])


@router.get("/{username}/contests")
async def get_contest_ranking(username: str):
    contest_response, error = await fetch_contest_ranking(username)
    if error:
        return make_envelope(
            username,
            None,
            legacy=ContestRankingResponse.error("error", error),
            status="error",
            message=error,
        )

    data = canonical_mapper.contests_from(contest_response)
    return make_envelope(username, data, legacy=contest_response)
