import httpx

from services.decoders.common import parse_submission_history


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
    async def fetch_all_recent_challenges(username: str, max_pages: int = 25) -> tuple[dict, str | None]:
        models: list[dict] = []
        cursor: str | None = None
        response_version = "v2"
        last_page = False

        for _ in range(max_pages):
            page, error = await HackerRankAPI.fetch_recent_challenges(username, cursor=cursor)
            if error:
                return {"models": models, "cursor": cursor, "last_page": last_page, "response_version": response_version}, error

            if isinstance(page, dict):
                page_models = page.get("models", []) or []
                models.extend(model for model in page_models if isinstance(model, dict))
                response_version = str(page.get("response_version") or response_version)
                last_page = bool(page.get("last_page", True))
                next_cursor = page.get("cursor")
            else:
                next_cursor = None
                last_page = True

            if last_page or not next_cursor or next_cursor == cursor:
                break
            cursor = str(next_cursor)

        return {"models": models, "cursor": cursor, "last_page": last_page, "response_version": response_version}, None

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
    async def _get_json(
        url: str,
        params: dict | None = None,
        default: dict | list | None = None,
        tolerate_statuses: set[int] | None = None,
    ) -> tuple[dict | list | None, str | None]:
        tolerate_statuses = tolerate_statuses or set()
        try:
            async with httpx.AsyncClient(headers=HackerRankAPI.HEADERS, follow_redirects=True, timeout=20.0) as client:
                response = await client.get(url, params=params)
        except httpx.HTTPError as exc:
            return default, str(exc)

        if response.status_code == 404:
            return default, "user does not exist"

        if response.status_code in tolerate_statuses:
            return default, None

        if response.status_code >= 400:
            return default, f"HTTP {response.status_code}"

        try:
            return response.json(), None
        except ValueError:
            return default, "invalid response from HackerRank"
