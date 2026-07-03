from services.client import HackerRankAPI
from services.decoders.heatmap import decode_heatmap


async def get_user_heatmap(username: str):
    profile, error = await HackerRankAPI.fetch_user_profile(username)
    if error:
        return None, error

    submission_history, history_error = await HackerRankAPI.fetch_user_submission_history(username)
    if history_error:
        return None, history_error

    return decode_heatmap(str(profile.get("username") or username), submission_history), None

__all__ = ["get_user_heatmap"]
