from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Query

from models.heatmap import HeatmapResponse
from models.canonical import make_envelope
from services import canonical_mapper
from services.heatmap import get_user_heatmap as fetch_user_heatmap
from services.heatmap_window import normalize_view, window_heatmap

router = APIRouter(tags=["Canonical"])


def _window_heatmap(legacy: dict, view: str, year: Optional[int]) -> dict:
    """Slice the daily contributions to the requested window and recompute
    the rollup stats so the totals stay in sync with the visible grid.

    ``view`` is one of ``all`` | ``last_365`` | ``year``. ``availableYears`` is
    always derived from the full data set before slicing.
    """
    daily = legacy.get("dailyContributions") or []
    years = sorted({int(d["date"][:4]) for d in daily if d.get("date")}, reverse=True)
    legacy["availableYears"] = years
    legacy["view"] = view
    legacy["year"] = year if view == "year" else None

    today = datetime.utcnow().date()
    if view == "year" and year is not None:
        sliced = [d for d in daily if d.get("date", "").startswith(f"{year}-")]
        win_start, win_end = f"{year}-01-01", f"{year}-12-31"

    elif view == "all":
        sliced = daily
        win_start = daily[0]["date"] if daily else ""
        win_end = daily[-1]["date"] if daily else ""

    else:  # last_365
        cutoff = (today - timedelta(days=364)).isoformat()
        sliced = [d for d in daily if d.get("date", "") >= cutoff]
        win_start, win_end = cutoff, today.isoformat()

    legacy["dailyContributions"] = sliced
    legacy["startDate"] = win_start
    legacy["endDate"] = win_end
    legacy["totalSubmissions"] = sum(d["count"] for d in sliced)
    legacy["activeDays"] = sum(1 for d in sliced if d["count"] > 0)
    legacy["maxDailySubmissions"] = max((d["count"] for d in sliced), default=0)

    actives = [d["date"] for d in sliced if d["count"] > 0]
    legacy["firstActiveDate"] = actives[0] if actives else ""
    legacy["lastActiveDate"] = actives[-1] if actives else ""

    longest = current = 0
    prev: Optional[date] = None
    for d in sliced:
        if d["count"] <= 0:
            continue
        cur_date = date.fromisoformat(d["date"])
        current = current + 1 if (prev is not None and (cur_date - prev).days == 1) else 1
        longest = max(longest, current)
        prev = cur_date
    legacy["longestStreak"] = longest

    return legacy


@router.get("/{username}/heatmap")
async def get_user_heatmap(
    username: str,
    view: str = Query("all", description="all | last_365 | year"),
    year: Optional[int] = Query(None, description="Required when view=year"),
):
    view, year = normalize_view(view, year)

    heatmap_response, error = await fetch_user_heatmap(username)
    if error:
        return make_envelope(
            username,
            None,
            legacy=HeatmapResponse.error("error", error),
            status="error",
            message=error,
        )

    data = window_heatmap(canonical_mapper.heatmap_from(heatmap_response), view, year)
    legacy = _window_heatmap(heatmap_response.model_dump(), view, year)
    return make_envelope(username, data, legacy=legacy)
