import html
import math
import re
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from models.badges import Badge, BadgesResponse, UpcomingBadge
from models.contests import ContestBadge, ContestHistoryEntry, ContestInfo, ContestRankingResponse
from models.heatmap import HeatmapDay, HeatmapResponse, YearlyContribution
from models.profiles import Contribution, ProfileResponse, RecentSubmission, UserProfile
from models.stats import StatsResponse


class ResponseDecoder:
    HACKERRANK_BASE_URL = "https://www.hackerrank.com"

    @staticmethod
    def parse_submission_history(raw_history: object) -> dict[str, int]:
        if not isinstance(raw_history, dict):
            return {}

        # HackerRank's submission_histories endpoint keys entries either by
        # epoch-second timestamps (legacy) or ISO date strings (current, e.g.
        # ``"2019-09-01"``). Keep any key that resolves to a real date.
        history: dict[str, int] = {}
        for key, count in raw_history.items():
            if ResponseDecoder._history_key_to_date(key) is None:
                continue
            history[str(key)] = ResponseDecoder._safe_int(count)
        return history

    @staticmethod
    def _history_key_to_date(key: object) -> "date | None":
        """Resolve a submission-history key (epoch seconds or ISO date) to a date."""
        text = str(key).strip()
        if not text:
            return None
        if text.isdigit():
            try:
                return datetime.fromtimestamp(int(text), tz=timezone.utc).date()
            except (ValueError, OverflowError, OSError):
                return None
        try:
            return date.fromisoformat(text)
        except ValueError:
            parts = text.split("-")
            if len(parts) == 3:
                try:
                    return date(int(parts[0]), int(parts[1]), int(parts[2]))
                except (ValueError, TypeError):
                    return None
            return None

    @staticmethod
    def _utc_today() -> date:
        return datetime.now(timezone.utc).date()

    @staticmethod
    def _safe_int(value: object, default: int = 0) -> int:
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(round(value))
        if value in (None, "", "N/A"):
            return default
        try:
            return int(float(str(value)))
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _safe_float(value: object, default: float = 0.0) -> float:
        if value in (None, "", "N/A"):
            return default
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _slugify(value: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
        return slug or "challenge"

    @staticmethod
    def _strip_html(value: str | None) -> str:
        if not value:
            return ""
        text = re.sub(r"<[^>]+>", "", value)
        return html.unescape(text).strip()

    @staticmethod
    def _to_timestamp(value: object) -> int:
        if isinstance(value, (int, float)):
            return int(value)
        if not value:
            return 0
        text = str(value).strip()
        if text.isdigit():
            return int(text)
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return int(parsed.timestamp())
        except ValueError:
            pass
        for pattern in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(text, pattern)
                if pattern == "%Y-%m-%d":
                    dt = datetime(dt.year, dt.month, dt.day, tzinfo=timezone.utc)
                else:
                    dt = dt.replace(tzinfo=timezone.utc)
                return int(dt.timestamp())
            except ValueError:
                continue
        return 0

    @staticmethod
    def _calculate_heatmap_level(count: int, max_daily_submissions: int) -> int:
        if count <= 0 or max_daily_submissions <= 0:
            return 0
        return min(4, max(1, math.ceil((count / max_daily_submissions) * 4)))

    @staticmethod
    def _calculate_longest_streak(active_dates: list[date]) -> int:
        if not active_dates:
            return 0

        longest_streak = 1
        current_streak = 1
        for index in range(1, len(active_dates)):
            if active_dates[index] - active_dates[index - 1] == timedelta(days=1):
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 1
        return longest_streak

    @staticmethod
    def _calculate_current_streak(date_counts: dict[date, int], today: date) -> int:
        streak_end = None
        if date_counts.get(today, 0) > 0:
            streak_end = today
        elif date_counts.get(today - timedelta(days=1), 0) > 0:
            streak_end = today - timedelta(days=1)

        if streak_end is None:
            return 0

        current_streak = 0
        cursor = streak_end
        while date_counts.get(cursor, 0) > 0:
            current_streak += 1
            cursor -= timedelta(days=1)
        return current_streak

    @staticmethod
    def _practice_score(track: dict) -> float:
        return max(0.0, ResponseDecoder._safe_float(track.get("practice", {}).get("score")))

    @staticmethod
    def _active_tracks(scores: list[dict]) -> list[dict]:
        return [track for track in scores if ResponseDecoder._practice_score(track) > 0]

    @staticmethod
    def _best_rank(scores: list[dict]) -> int:
        ranks = [
            ResponseDecoder._safe_int(track.get("practice", {}).get("rank"))
            for track in scores
            if ResponseDecoder._practice_score(track) > 0
            and ResponseDecoder._safe_int(track.get("practice", {}).get("rank")) > 0
        ]
        return min(ranks) if ranks else 0

    @staticmethod
    def _total_practice_score(scores: list[dict]) -> int:
        return int(round(sum(ResponseDecoder._practice_score(track) for track in scores)))

    @staticmethod
    def _challenge_identity(challenge: dict) -> str:
        return str(
            challenge.get("ch_slug")
            or challenge.get("slug")
            or challenge.get("url")
            or challenge.get("name")
            or ""
        ).strip()

    @staticmethod
    def _solved_challenge_count(recent_challenges_data: dict | None) -> int:
        if not isinstance(recent_challenges_data, dict):
            return 0
        models = recent_challenges_data.get("models", []) or []
        identities = {
            ResponseDecoder._challenge_identity(challenge)
            for challenge in models
            if isinstance(challenge, dict)
        }
        identities.discard("")
        return len(identities)

    @staticmethod
    def _badge_solved_count(badges_data: dict | None) -> int:
        if not isinstance(badges_data, dict):
            return 0
        models = badges_data.get("models", []) or []
        return sum(
            ResponseDecoder._safe_int(badge.get("solved"))
            for badge in models
            if isinstance(badge, dict)
        )

    @staticmethod
    def _badge_icon(badge_data: dict) -> str:
        icon = (
            badge_data.get("icon")
            or badge_data.get("badge_icon")
            or badge_data.get("badge_image")
            or badge_data.get("image")
            or badge_data.get("url")
        )
        if isinstance(icon, dict):
            icon = icon.get("small") or icon.get("medium") or icon.get("large") or icon.get("url")
        if isinstance(icon, str) and icon.strip():
            icon = icon.strip()
            if icon.startswith("//"):
                return f"https:{icon}"
            if icon.startswith("/"):
                return f"{ResponseDecoder.HACKERRANK_BASE_URL}{icon}"
            return icon
        return ""

    @staticmethod
    def _decode_badge_item(badge_data: dict) -> Badge:
        name = str(badge_data.get("badge_name") or badge_data.get("display_name") or badge_data.get("name") or "Badge")
        badge_type = str(badge_data.get("badge_type") or badge_data.get("type") or "badge")
        level = ResponseDecoder._safe_int(badge_data.get("level"), 1)
        badge_id = str(badge_data.get("id") or f"{badge_type}:{ResponseDecoder._slugify(name)}:{level}")
        return Badge(
            id=badge_id,
            displayName=name,
            icon=ResponseDecoder._badge_icon(badge_data),
            creationDate=ResponseDecoder._to_timestamp(badge_data.get("created_at") or badge_data.get("awarded_at")),
        )

    @staticmethod
    def _pick_active_badge(badges: list[dict]) -> Badge | None:
        if not badges:
            return None
        best = max(
            badges,
            key=lambda badge: (
                ResponseDecoder._safe_int(badge.get("stars")),
                ResponseDecoder._safe_int(badge.get("level")),
            ),
        )
        return ResponseDecoder._decode_badge_item(best)

    @staticmethod
    def decode_stats(
        profile_data: dict,
        scores_data: list[dict],
        submission_history: dict[str, int],
        badges_data: dict | None = None,
        recent_challenges_data: dict | None = None,
    ) -> StatsResponse:
        total_practice_score = ResponseDecoder._total_practice_score(scores_data)
        solved_challenges = ResponseDecoder._badge_solved_count(badges_data)
        if solved_challenges <= 0:
            solved_challenges = ResponseDecoder._solved_challenge_count(recent_challenges_data)
        return StatsResponse(
            status="success",
            message="retrieved",
            totalSolved=solved_challenges,
            totalQuestions=0,
            easySolved=0,
            totalEasy=0,
            mediumSolved=0,
            totalMedium=0,
            hardSolved=0,
            totalHard=0,
            acceptanceRate=0.0,
            ranking=ResponseDecoder._best_rank(scores_data),
            contributionPoints=ResponseDecoder._safe_int(profile_data.get("level")),
            practiceScore=total_practice_score,
            reputation=ResponseDecoder._safe_int(profile_data.get("followers_count")),
            submissionCalendar=submission_history,
        )

    @staticmethod
    def decode_profile(
        profile_data: dict,
        scores_data: list[dict],
        badges_data: dict,
        submission_history: dict[str, int],
        recent_challenges_data: dict,
    ) -> ProfileResponse:
        badges_raw = badges_data.get("models", []) if isinstance(badges_data, dict) else []
        badges = [ResponseDecoder._decode_badge_item(badge) for badge in badges_raw if isinstance(badge, dict)]
        active_tracks = ResponseDecoder._active_tracks(scores_data)
        total_practice_score = ResponseDecoder._total_practice_score(scores_data)
        total_submissions = sum(submission_history.values())
        solved_challenges = ResponseDecoder._badge_solved_count(badges_data)
        if solved_challenges <= 0:
            solved_challenges = ResponseDecoder._solved_challenge_count(recent_challenges_data)

        skill_tags = [str(track.get("name")) for track in active_tracks if track.get("name")]
        website = str(profile_data.get("website") or "").strip()

        practice_rows = []
        for track in sorted(active_tracks, key=ResponseDecoder._practice_score, reverse=True)[:5]:
            score = ResponseDecoder._safe_int(track.get("practice", {}).get("score"))
            rank = ResponseDecoder._safe_int(track.get("practice", {}).get("rank"))
            practice_rows.append(
                {
                    "difficulty": str(track.get("name") or "Track"),
                    "count": score,
                    "submissions": 0,
                    "rank": rank,
                }
            )

        attempt_rows = [
            {
                "difficulty": "All",
                "count": total_submissions,
                "submissions": total_submissions,
            }
        ]

        recent_submissions = []
        for challenge in recent_challenges_data.get("models", []):
            if not isinstance(challenge, dict):
                continue
            title = str(
                challenge.get("name")
                or challenge.get("challenge_name")
                or challenge.get("slug")
                or "Unknown Challenge"
            )
            recent_submissions.append(
                RecentSubmission(
                    title=title,
                    titleSlug=str(challenge.get("ch_slug") or challenge.get("slug") or ResponseDecoder._slugify(title)),
                    timestamp=ResponseDecoder._to_timestamp(
                        challenge.get("solved_at")
                        or challenge.get("created_at")
                        or challenge.get("timestamp")
                        or challenge.get("updated_at")
                        or challenge.get("last_solved_at")
                    ),
                    statusDisplay=str(challenge.get("status") or "Listed"),
                    lang=str(challenge.get("language") or challenge.get("lang") or ""),
                )
            )

        return ProfileResponse(
            status="success",
            message="retrieved",
            username=str(profile_data.get("username") or ""),
            githubUrl=profile_data.get("github_url") or None,
            twitterUrl=None,
            linkedinUrl=profile_data.get("linkedin_url") or None,
            contributions=Contribution(
                points=total_practice_score,
                questionCount=solved_challenges,
                testcaseCount=total_submissions,
            ),
            profile=UserProfile(
                realName=str(profile_data.get("name") or ""),
                userAvatar=str(profile_data.get("avatar") or ""),
                birthday="",
                ranking=ResponseDecoder._best_rank(scores_data),
                reputation=ResponseDecoder._safe_int(profile_data.get("followers_count")),
                websites=[website] if website else [],
                countryName=str(profile_data.get("country") or profile_data.get("location") or ""),
                company=str(profile_data.get("company") or ""),
                school=str(profile_data.get("school") or ""),
                skillTags=skill_tags,
                aboutMe=str(profile_data.get("short_bio") or ""),
                starRating=ResponseDecoder._safe_float(profile_data.get("level")),
            ),
            badges=badges,
            upcomingBadges=[],
            activeBadge=ResponseDecoder._pick_active_badge(badges_raw),
            submitStats={
                "acSubmissionNum": practice_rows,
                "totalSubmissionNum": attempt_rows,
            },
            submissionCalendar=submission_history,
            recentSubmissions=recent_submissions,
        )

    @staticmethod
    def decode_badges(badges_data: dict) -> BadgesResponse:
        badges_raw = badges_data.get("models", []) if isinstance(badges_data, dict) else []
        badges = [ResponseDecoder._decode_badge_item(badge) for badge in badges_raw if isinstance(badge, dict)]
        return BadgesResponse(
            status="success",
            message="retrieved",
            badges=badges,
            upcomingBadges=[],
            activeBadge=ResponseDecoder._pick_active_badge(badges_raw),
        )

    @staticmethod
    def decode_contest_ranking(profile_data: dict, contests_data: dict, ratings_data: dict) -> ContestRankingResponse:
        contest_models = contests_data.get("models", []) if isinstance(contests_data, dict) else []
        rating_models = ratings_data.get("models", []) if isinstance(ratings_data, dict) else []
        if not contest_models and not rating_models:
            return ContestRankingResponse.error("error", "user has no contest history")

        history_source = contest_models or rating_models
        contest_history: list[ContestHistoryEntry] = []
        last_rating = 0
        for item in history_source:
            if not isinstance(item, dict):
                continue
            rating = ResponseDecoder._safe_int(
                item.get("rating") or item.get("elo") or item.get("score") or item.get("contest_score")
            )
            trend_direction = str(item.get("trendDirection") or item.get("trend_direction") or "")
            if not trend_direction:
                if rating > last_rating:
                    trend_direction = "UP"
                elif rating < last_rating:
                    trend_direction = "DOWN"
                else:
                    trend_direction = "SAME"
            last_rating = rating

            title = str(
                item.get("contest_name")
                or item.get("name")
                or item.get("event_name")
                or item.get("slug")
                or ""
            )
            contest_history.append(
                ContestHistoryEntry(
                    attended=True,
                    rating=rating,
                    ranking=ResponseDecoder._safe_int(item.get("rank") or item.get("ranking")),
                    trendDirection=trend_direction,
                    problemsSolved=ResponseDecoder._safe_int(
                        item.get("solved_challenges") or item.get("solved") or item.get("problems_solved")
                    ),
                    totalProblems=ResponseDecoder._safe_int(
                        item.get("total_challenges") or item.get("total") or item.get("total_problems")
                    ),
                    finishTimeInSeconds=ResponseDecoder._safe_int(
                        item.get("time_taken") or item.get("finishTimeInSeconds")
                    ),
                    contest=ContestInfo(
                        title=title,
                        startTime=ResponseDecoder._to_timestamp(
                            item.get("start_time") or item.get("created_at") or item.get("timestamp")
                        ),
                    ),
                )
            )

        rating_values = [entry.rating for entry in contest_history if entry.rating > 0]
        latest_rating = rating_values[-1] if rating_values else 0
        latest_ranking = next((entry.ranking for entry in reversed(contest_history) if entry.ranking > 0), 0)
        total_participants = ResponseDecoder._safe_int(
            next(
                (
                    item.get("total_participants")
                    for item in reversed(history_source)
                    if isinstance(item, dict) and item.get("total_participants")
                ),
                0,
            )
        )
        top_percentage = 0.0
        if latest_ranking > 0 and total_participants > 0:
            top_percentage = round((latest_ranking / total_participants) * 100, 2)

        title = ResponseDecoder._strip_html(str(profile_data.get("title") or ""))
        badge = ContestBadge(name=title) if title else None
        return ContestRankingResponse(
            status="success",
            message="retrieved",
            attendedContestsCount=len(contest_history),
            rating=latest_rating,
            globalRanking=latest_ranking,
            totalParticipants=total_participants,
            topPercentage=top_percentage,
            badge=badge,
            contestHistory=contest_history,
        )

    @staticmethod
    def decode_heatmap(username: str, submission_history: dict[str, int]) -> HeatmapResponse:
        date_counts: dict[date, int] = {}
        for key, count in submission_history.items():
            contribution_date = ResponseDecoder._history_key_to_date(key)
            if contribution_date is None:
                continue
            date_counts[contribution_date] = date_counts.get(contribution_date, 0) + ResponseDecoder._safe_int(count)

        if not date_counts:
            return HeatmapResponse(
                status="success",
                message="retrieved",
                username=username,
                startDate="",
                endDate="",
                firstActiveDate="",
                lastActiveDate="",
                totalSubmissions=0,
                activeDays=0,
                currentStreak=0,
                longestStreak=0,
                maxDailySubmissions=0,
                dailyContributions=[],
                yearlyContributions=[],
            )

        today = ResponseDecoder._utc_today()
        active_dates = sorted(date_counts)
        first_active_date = active_dates[0]
        last_active_date = active_dates[-1]
        start_date = date(first_active_date.year, 1, 1)
        end_date = max(today, last_active_date)
        total_submissions = sum(date_counts.values())
        active_days = len(active_dates)
        max_daily_submissions = max(date_counts.values())

        yearly_totals: dict[int, dict[str, int]] = {}
        for contribution_date, count in date_counts.items():
            year_totals = yearly_totals.setdefault(contribution_date.year, {"totalSubmissions": 0, "activeDays": 0})
            year_totals["totalSubmissions"] += count
            year_totals["activeDays"] += 1

        daily_contributions = []
        cursor = start_date
        while cursor <= end_date:
            count = date_counts.get(cursor, 0)
            timestamp = int(datetime(cursor.year, cursor.month, cursor.day, tzinfo=timezone.utc).timestamp())
            daily_contributions.append(
                HeatmapDay(
                    date=cursor.isoformat(),
                    timestamp=timestamp,
                    count=count,
                    level=ResponseDecoder._calculate_heatmap_level(count, max_daily_submissions),
                )
            )
            cursor += timedelta(days=1)

        yearly_contributions = [
            YearlyContribution(
                year=year,
                totalSubmissions=totals["totalSubmissions"],
                activeDays=totals["activeDays"],
            )
            for year, totals in sorted(yearly_totals.items())
        ]

        return HeatmapResponse(
            status="success",
            message="retrieved",
            username=username,
            startDate=start_date.isoformat(),
            endDate=end_date.isoformat(),
            firstActiveDate=first_active_date.isoformat(),
            lastActiveDate=last_active_date.isoformat(),
            totalSubmissions=total_submissions,
            activeDays=active_days,
            currentStreak=ResponseDecoder._calculate_current_streak(date_counts, today),
            longestStreak=ResponseDecoder._calculate_longest_streak(active_dates),
            maxDailySubmissions=max_daily_submissions,
            dailyContributions=daily_contributions,
            yearlyContributions=yearly_contributions,
        )

history_key_to_date = ResponseDecoder._history_key_to_date
parse_submission_history = ResponseDecoder.parse_submission_history
safe_float = ResponseDecoder._safe_float
safe_int = ResponseDecoder._safe_int
slugify = ResponseDecoder._slugify
strip_html = ResponseDecoder._strip_html
to_timestamp = ResponseDecoder._to_timestamp
utc_today = ResponseDecoder._utc_today
