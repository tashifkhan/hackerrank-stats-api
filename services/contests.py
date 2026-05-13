import asyncio

from services.client import HackerRankAPI
from services.decoders.contests import decode_contest_ranking


async def get_contest_ranking(username: str):
    profile_data, contests_data, ratings_data = await asyncio.gather(
        HackerRankAPI.fetch_user_profile(username),
        HackerRankAPI.fetch_user_contests(username),
        HackerRankAPI.fetch_user_ratings(username),
    )

    profile, error = profile_data
    if error:
        return None, error

    contests, contests_error = contests_data
    if contests_error:
        return None, contests_error

    ratings, ratings_error = ratings_data
    if ratings_error:
        return None, ratings_error

    contest_response = decode_contest_ranking(profile, contests, ratings)
    if contest_response.status == "error":
        return None, contest_response.message
    return contest_response, None

__all__ = ["get_contest_ranking"]
