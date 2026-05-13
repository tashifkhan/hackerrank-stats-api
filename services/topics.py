"""Per-challenge topic (track) lookup for HackerRank solved challenges.

``recent_challenges`` (despite its name) paginates a user's entire solved-
challenge history via ``cursor``/``last_page``. Each challenge slug is then
resolved to its sub-track name (e.g. "Strings", "Dynamic Programming") via the
public challenge-detail endpoint, and tallied into a genuine per-challenge
topic breakdown -- replacing the previous per-track practice-score proxy. See
../CANONICAL_SCHEMA.md.
"""

import asyncio
from typing import Dict, List

from models.canonical.stats import TopicCount
from services.client import HackerRankAPI

_CONCURRENCY = 10

# Challenge -> track name is static metadata, safe to cache for the process
# lifetime and reused across users.
_TRACK_CACHE: Dict[str, str | None] = {}


async def _all_solved_slugs(username: str) -> List[str]:
    slugs: List[str] = []
    cursor: str | None = None
    while True:
        page, error = await HackerRankAPI.fetch_recent_challenges(username, cursor=cursor)
        if error:
            break
        for model in page.get("models", []) or []:
            slug = model.get("ch_slug")
            if slug:
                slugs.append(slug)
        if page.get("last_page", True) or not page.get("cursor"):
            break
        cursor = page.get("cursor")
    return slugs


async def _track_name(slug: str) -> str | None:
    if slug in _TRACK_CACHE:
        return _TRACK_CACHE[slug]

    track_name = None
    model, error = await HackerRankAPI.fetch_challenge_detail(slug)
    if not error and model:
        track = model.get("track")
        if track:
            track_name = track.get("name")

    _TRACK_CACHE[slug] = track_name
    return track_name


async def build_topic_analysis(username: str) -> List[TopicCount]:
    slugs = await _all_solved_slugs(username)
    if not slugs:
        return []

    unique_slugs = list(dict.fromkeys(slugs))
    semaphore = asyncio.Semaphore(_CONCURRENCY)

    async def _bounded_track(slug: str) -> str | None:
        async with semaphore:
            return await _track_name(slug)

    track_names = await asyncio.gather(*(_bounded_track(slug) for slug in unique_slugs))
    slug_to_track = dict(zip(unique_slugs, track_names))

    counts: Dict[str, int] = {}
    for slug in slugs:
        track_name = slug_to_track.get(slug)
        if not track_name:
            continue
        counts[track_name] = counts.get(track_name, 0) + 1

    return [
        TopicCount(topic=topic, count=count)
        for topic, count in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    ]


__all__ = ["build_topic_analysis"]
