from services.client import HackerRankAPI
from services.decoders.badges import decode_badges


async def get_user_badges(username: str):
    _, error = await HackerRankAPI.fetch_user_profile(username)
    if error:
        return None, error

    badges_data, badges_error = await HackerRankAPI.fetch_user_badges(username)
    if badges_error:
        return None, badges_error

    return decode_badges(badges_data), None

__all__ = ["get_user_badges"]
