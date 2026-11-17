import asyncio
import json

import httpx
from fastapi import HTTPException

from core.cache import get_json
from core.jobs import enqueue
from core.runtime import http_client, remaining, state
from core.source import source

from services.decoders.common import parse_submission_history


UPSTREAM_TIMEOUT = 4.0


class HackerRankAPI:
    PROFILE_URL = "https://www.hackerrank.com/rest/contests/master/hackers/{username}/profile"
    SCORES_URL = "https://www.hackerrank.com/rest/hackers/{username}/scores_elo"
    BADGES_URL = "https://www.hackerrank.com/rest/hackers/{username}/badges"
    CONTESTS_URL = "https://www.hackerrank.com/rest/hackers/{username}/contest_participation"
    RATINGS_URL = "https://www.hackerrank.com/rest/hackers/{username}/rating_histories_elo"
    SUBMISSIONS_URL = "https://www.hackerrank.com/rest/hackers/{username}/submission_histories"
    RECENT_CHALLENGES_URL = "https://www.hackerrank.com/rest/hackers/{username}/recent_challenges"
    CHALLENGE_URL = "https://www.hackerrank.com/rest/contests/master/challenges/{slug}"
    HEADERS = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    }

    @staticmethod
    async def fetch_user_profile(username: str) -> tuple[dict | None, str | None]:
        data, error = await HackerRankAPI._get_json(HackerRankAPI.PROFILE_URL.format(username=username))
        if error:
            return None, error
        model = data.get("model") if isinstance(data, dict) else None
        if not model:
            return None, "user does not exist"
        return model, None

    @staticmethod
    async def fetch_user_scores(username: str) -> tuple[list[dict], str | None]:
        data, error = await HackerRankAPI._get_json(
            HackerRankAPI.SCORES_URL.format(username=username),
            default=[],
            tolerate_statuses={404},
        )
        if error:
            return [], error
        return data if isinstance(data, list) else [], None

    @staticmethod
    async def fetch_user_badges(username: str) -> tuple[dict, str | None]:
        data, error = await HackerRankAPI._get_json(
            HackerRankAPI.BADGES_URL.format(username=username),
            default={"models": [], "version": 0},
            tolerate_statuses={404},
        )
        if error:
            return {"models": [], "version": 0}, error
        return data if isinstance(data, dict) else {"models": [], "version": 0}, None

    @staticmethod
    async def fetch_user_contests(username: str) -> tuple[dict, str | None]:
        data, error = await HackerRankAPI._get_json(
            HackerRankAPI.CONTESTS_URL.format(username=username),
            params={"offset": 0, "limit": 50},
            default={"models": [], "total": 0},
            tolerate_statuses={404},
        )
        if error:
            return {"models": [], "total": 0}, error
        return data if isinstance(data, dict) else {"models": [], "total": 0}, None

    @staticmethod
    async def fetch_user_ratings(username: str) -> tuple[dict, str | None]:
        data, error = await HackerRankAPI._get_json(
            HackerRankAPI.RATINGS_URL.format(username=username),
            default={"models": []},
            tolerate_statuses={404},
        )
        if error:
            return {"models": []}, error
        return data if isinstance(data, dict) else {"models": []}, None

    @staticmethod
    async def fetch_user_submission_history(username: str) -> tuple[dict[str, int], str | None]:
        data, error = await HackerRankAPI._get_json(
            HackerRankAPI.SUBMISSIONS_URL.format(username=username),
            default={},
            tolerate_statuses={404},
        )
        if error:
            return {}, error
        return parse_submission_history(data), None

    @staticmethod
    async def fetch_recent_challenges(
        username: str,
        cursor: str | None = None,
        limit: int = 100,
    ) -> tuple[dict, str | None]:
        params = {"limit": limit, "response_version": "v2"}
        if cursor:
            params["cursor"] = cursor
        data, error = await HackerRankAPI._get_json(
            HackerRankAPI.RECENT_CHALLENGES_URL.format(username=username),
            params=params,
            default={"models": [], "cursor": None, "last_page": True},
            tolerate_statuses={404, 500},
        )
        if error:
            return {"models": [], "cursor": None, "last_page": True}, error
        return data if isinstance(data, dict) else {"models": [], "cursor": None, "last_page": True}, None

    @staticmethod
    async def fetch_all_recent_challenges(username: str) -> tuple[dict, str | None]:
        """Newest page live, older pages from the refresh worker's history cache.

        Paginating the whole history inline took up to 25 upstream round trips
        and was one cause of the 10s timeouts. History is optional here: the
        profile call decides whether the user exists, so this never errors.
        """
        (page, page_error), history = await asyncio.gather(
            HackerRankAPI.fetch_recent_challenges(username),
            get_json("hr:history:v2:" + username.lower()),
        )
        history = history or {}
        models: list[dict] = []
        seen: set[str] = set()
        for model in [*(page.get("models") or []), *(history.get("models") or [])]:
            if not isinstance(model, dict):
                continue
            slug = model.get("ch_slug")
            if slug:
                if slug in seen:
                    continue
                seen.add(slug)
            models.append(model)

        complete = bool(history.get("complete")) or (not page_error and bool(page.get("last_page", True)))
        if not complete:
            queued = await enqueue("topics", username)
            current = state.get()
            if current:
                status = "partial" if models else "pending" if queued else "unavailable"
                current.meta["history"] = {"status": status, "complete": False}
        return {"models": models, "cursor": None, "last_page": complete, "response_version": "v2"}, None

    @staticmethod
    async def fetch_challenge_detail(slug: str) -> tuple[dict | None, str | None]:
        data, error = await HackerRankAPI._get_json(
            HackerRankAPI.CHALLENGE_URL.format(slug=slug),
            default={},
            tolerate_statuses={404},
        )
        if error:
            return None, error
        model = data.get("model") if isinstance(data, dict) else None
        return model, None

    @staticmethod
    async def _fetch_json(
        url: str,
        params: dict | None = None,
        default: dict | list | None = None,
        tolerate_statuses: set[int] | None = None,
    ) -> tuple[dict | list | None, str | None]:
        tolerate_statuses = tolerate_statuses or set()
        async def fetch():
            async with http_client() as client:
                return await client.get(url, params=params, headers=HackerRankAPI.HEADERS, timeout=min(UPSTREAM_TIMEOUT, remaining()))

        # httpx timeouts are per phase, so a slow trickle could outlive them.
        # wait_for caps the whole call.
        try:
            response = await asyncio.wait_for(fetch(), min(UPSTREAM_TIMEOUT, remaining()))
        except (httpx.HTTPError, asyncio.TimeoutError):
            return default, "HackerRank upstream unavailable"

        if response.status_code in tolerate_statuses and response.status_code < 500:
            return default, None

        if response.status_code == 404:
            return default, "user does not exist"

        if response.status_code >= 400:
            return default, f"HTTP {response.status_code}"

        try:
            return response.json(), None
        except ValueError:
            return default, "invalid response from HackerRank"

    @staticmethod
    async def _get_json(url, params=None, default=None, tolerate_statuses=None):
        """Cached upstream read. A failed refresh falls back to the last good payload."""
        async def fetch():
            data, error = await HackerRankAPI._fetch_json(url, params, default, tolerate_statuses)
            if error:
                raise HTTPException(404 if error == "user does not exist" else 502, error)
            return data

        try:
            return await source("hr:" + url + json.dumps(params, sort_keys=True), fetch), None
        except HTTPException as exc:
            return default, str(exc.detail)
