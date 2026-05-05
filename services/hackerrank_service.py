import asyncio

from services.hackerrank_api import HackerRankAPI, ResponseDecoder


class HackerRankService:
    @staticmethod
    async def get_user_stats(username: str):
        profile_data, scores_data, submission_history = await asyncio.gather(
            HackerRankAPI.fetch_user_profile(username),
            HackerRankAPI.fetch_user_scores(username),
            HackerRankAPI.fetch_user_submission_history(username),
        )

        profile, error = profile_data
        if error:
            return None, error

        scores, scores_error = scores_data
        if scores_error:
            return None, scores_error

        history, history_error = submission_history
        if history_error:
            return None, history_error

        return ResponseDecoder.decode_stats(profile, scores, history), None

    @staticmethod
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

        contest_response = ResponseDecoder.decode_contest_ranking(profile, contests, ratings)
        if contest_response.status == "error":
            return None, contest_response.message
        return contest_response, None

    @staticmethod
    async def get_user_profile(username: str):
        profile_data, scores_data, badges_data, submission_history, recent_challenges_data = await asyncio.gather(
            HackerRankAPI.fetch_user_profile(username),
            HackerRankAPI.fetch_user_scores(username),
            HackerRankAPI.fetch_user_badges(username),
            HackerRankAPI.fetch_user_submission_history(username),
            HackerRankAPI.fetch_recent_challenges(username),
        )

        profile, error = profile_data
        if error:
            return None, error

        scores, scores_error = scores_data
        if scores_error:
            return None, scores_error

        badges, badges_error = badges_data
        if badges_error:
            return None, badges_error

        history, history_error = submission_history
        if history_error:
            return None, history_error

        recent_challenges, recent_error = recent_challenges_data
        if recent_error:
            return None, recent_error

        return ResponseDecoder.decode_profile(profile, scores, badges, history, recent_challenges), None

    @staticmethod
    async def get_user_badges(username: str):
        profile, error = await HackerRankAPI.fetch_user_profile(username)
        if error:
            return None, error

        badges_data, badges_error = await HackerRankAPI.fetch_user_badges(username)
        if badges_error:
            return None, badges_error

        return ResponseDecoder.decode_badges(badges_data), None

    @staticmethod
    async def get_user_heatmap(username: str):
        profile, error = await HackerRankAPI.fetch_user_profile(username)
        if error:
            return None, error

        submission_history, history_error = await HackerRankAPI.fetch_user_submission_history(username)
        if history_error:
            return None, history_error

        return ResponseDecoder.decode_heatmap(str(profile.get("username") or username), submission_history), None
