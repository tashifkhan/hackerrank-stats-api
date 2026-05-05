from fastapi import APIRouter

from models.heatmap import HeatmapResponse
from services.hackerrank_service import HackerRankService

router = APIRouter()


@router.get("/{username}/heatmap", response_model=HeatmapResponse)
async def get_user_heatmap(username: str) -> HeatmapResponse:
    heatmap_response, error = await HackerRankService.get_user_heatmap(username)
    if error:
        return HeatmapResponse.error("error", error)
    return heatmap_response
