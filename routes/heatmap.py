from fastapi import APIRouter

from models.heatmap import HeatmapResponse
from models.unified import make_envelope
from services import unified_mapper
from services.hackerrank_service import HackerRankService

router = APIRouter()


@router.get("/{username}/heatmap")
async def get_user_heatmap(username: str):
    heatmap_response, error = await HackerRankService.get_user_heatmap(username)
    if error:
        return make_envelope(
            username,
            None,
            legacy=HeatmapResponse.error("error", error),
            status="error",
            message=error,
        )

    data = unified_mapper.heatmap_from(heatmap_response)
    return make_envelope(username, data, legacy=heatmap_response)
