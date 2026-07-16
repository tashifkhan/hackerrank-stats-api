from fastapi import APIRouter, Query

from models.canonical import make_envelope
from models.stats import StatsResponse
from services import canonical_mapper, topics
from services.stats import get_user_stats as fetch_user_stats
from services.stats_svg import error_svg_response, stats_svg_response

router = APIRouter(tags=["Canonical"])


@router.get("/{username}/stats/svg", summary="Stats SVG card")
async def get_stats_svg(
    username: str,
    theme: str = Query("dark", description="Card theme: dark or light"),
):
    stats_response, error = await fetch_user_stats(username)
    if error:
        return error_svg_response(
            error,
            platform="hackerrank",
            username=username,
            theme=theme,
        )
    data = canonical_mapper.stats_from(
        stats_response, await topics.build_topic_analysis(username)
    )
    return stats_svg_response("hackerrank", username, data, theme=theme)


@router.get("/{username}/stats")
async def get_stats(username: str):
    stats_response, error = await fetch_user_stats(username)
    if error:
        return make_envelope(
            username,
            None,
            legacy=StatsResponse.error("error", error),
            status="error",
            message=error,
        )

    data = canonical_mapper.stats_from(
        stats_response, await topics.build_topic_analysis(username)
    )
    return make_envelope(username, data, legacy=stats_response)


@router.get("/{username}")
async def get_summary(username: str):
    card = await canonical_mapper.build_card(username)
    stats_response, error = await fetch_user_stats(username)
    legacy = None if error else stats_response
    return make_envelope(username, canonical_mapper.summary_from(card), legacy=legacy)
