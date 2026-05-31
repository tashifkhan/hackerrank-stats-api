"""Builds the unified cross-platform card for HackerRank by reusing the existing
``HackerRankService`` fetchers, deriving topic analysis from per-track practice
scores and a rating time series from contest history.

See ../UNIFIED_SCHEMA.md for the wire format.
"""

import asyncio
from datetime import datetime, timezone
from typing import List, Optional

from models.unified import (
    BadgeItem,
    ContestHistoryItem,
    HeatDay,
    RatingPoint,
    TopicCount,
    UnifiedBadges,
    UnifiedCard,
    UnifiedContests,
    UnifiedHeatmap,
    UnifiedProfile,
    UnifiedRating,
    UnifiedSocial,
    UnifiedStats,
    UnifiedSummary,
    YearContribution,
)
from services.hackerrank_api import HackerRankAPI, ResponseDecoder
from services.hackerrank_service import HackerRankService


def _ts_to_date(timestamp) -> Optional[str]:
    if not timestamp:
        return None
    try:
        return datetime.fromtimestamp(int(timestamp), tz=timezone.utc).date().isoformat()
    except (ValueError, OSError, OverflowError):
        return None


# --- pure converters --------------------------------------------------------

def profile_from(profile_response, username: str) -> UnifiedProfile:
    if profile_response is None:
        return UnifiedProfile(username=username)
    p = profile_response.profile
    return UnifiedProfile(
        displayName=p.realName or None,
        username=profile_response.username or username,
        avatar=p.userAvatar or None,
        country=p.countryName or None,
        institution=p.school or None,
        company=p.company or None,
        bio=p.aboutMe or None,
        websites=list(p.websites or []),
        social=UnifiedSocial(
            github=profile_response.githubUrl,
            twitter=profile_response.twitterUrl,
            linkedin=profile_response.linkedinUrl,
        ),
        verified=False,
    )


def topics_from_scores(scores_data) -> List[TopicCount]:
    """Per-track practice score -> topic analysis bars."""
    if not scores_data:
        return []
    tracks = ResponseDecoder._active_tracks(scores_data)
    topics = [
        TopicCount(
            topic=str(track.get("name")),
            count=int(round(ResponseDecoder._practice_score(track))),
        )
        for track in tracks
        if track.get("name")
    ]
    return sorted(topics, key=lambda t: t.count, reverse=True)


def stats_from(stats_response, topics: List[TopicCount]) -> UnifiedStats:
    if stats_response is None:
        return UnifiedStats(topicAnalysis=topics)
    return UnifiedStats(
        totalSolved=stats_response.totalSolved,
        totalQuestions=stats_response.totalQuestions or None,
        acceptanceRate=stats_response.acceptanceRate,
        byDifficulty={
            "easy": stats_response.easySolved,
            "medium": stats_response.mediumSolved,
            "hard": stats_response.hardSolved,
        },
        topicAnalysis=topics,
    )


def contests_from(contest_response) -> UnifiedContests:
    if contest_response is None:
        return UnifiedContests()
    history = [
        ContestHistoryItem(
            name=entry.contest.title,
            date=_ts_to_date(entry.contest.startTime),
            timestamp=entry.contest.startTime,
            rating=entry.rating,
            ranking=entry.ranking,
            problemsSolved=entry.problemsSolved,
            totalProblems=entry.totalProblems,
        )
        for entry in contest_response.contestHistory
    ]
    max_rating = max((h.rating for h in history if h.rating is not None), default=None)
    return UnifiedContests(
        count=contest_response.attendedContestsCount,
        rating=contest_response.rating or None,
        maxRating=max_rating,
        rank=contest_response.badge.name if contest_response.badge else None,
        globalRanking=contest_response.globalRanking or None,
        topPercentage=contest_response.topPercentage,
        history=history,
    )


def rating_from(contests: UnifiedContests) -> UnifiedRating:
    history = [
        RatingPoint(timestamp=h.timestamp, rating=h.rating, contestName=h.name)
        for h in contests.history
        if h.rating is not None
    ]
    return UnifiedRating(current=contests.rating, max=contests.maxRating, history=history)


def heatmap_from(heatmap_response) -> UnifiedHeatmap:
    if heatmap_response is None:
        return UnifiedHeatmap()
    return UnifiedHeatmap(
        totalSubmissions=heatmap_response.totalSubmissions,
        totalActiveDays=heatmap_response.activeDays,
        currentStreak=heatmap_response.currentStreak,
        longestStreak=heatmap_response.longestStreak,
        maxDailySubmissions=heatmap_response.maxDailySubmissions,
        firstActiveDate=heatmap_response.firstActiveDate or None,
        lastActiveDate=heatmap_response.lastActiveDate or None,
        dailyContributions=[
            HeatDay(date=d.date, count=d.count, level=d.level)
            for d in heatmap_response.dailyContributions
        ],
        yearlyContributions=[
            YearContribution(
                year=y.year,
                totalSubmissions=y.totalSubmissions,
                activeDays=y.activeDays,
            )
            for y in heatmap_response.yearlyContributions
        ],
    )


def badges_from(badges_response) -> UnifiedBadges:
    if badges_response is None:
        return UnifiedBadges()
    items = [
        BadgeItem(id=str(b.id), name=b.displayName, icon=b.icon, level=None)
        for b in badges_response.badges
    ]
    active = None
    if badges_response.activeBadge:
        ab = badges_response.activeBadge
        active = BadgeItem(id=str(ab.id), name=ab.displayName, icon=ab.icon, level=None)
    return UnifiedBadges(count=len(items), active=active, list=items)


def summary_from(card: UnifiedCard) -> UnifiedSummary:
    return UnifiedSummary(
        totalSolved=card.stats.totalSolved,
        totalActiveDays=card.heatmap.totalActiveDays,
        totalContests=card.contests.count,
        currentRating=card.contests.rating,
        maxRating=card.contests.maxRating,
        rank=card.contests.rank,
        badgesCount=card.badges.count,
    )


# --- fetchers ---------------------------------------------------------------

async def _topics(username: str) -> List[TopicCount]:
    scores, error = await HackerRankAPI.fetch_user_scores(username)
    if error:
        return []
    return topics_from_scores(scores)


async def build_stats(username: str) -> UnifiedStats:
    stats_response, _ = await HackerRankService.get_user_stats(username)
    return stats_from(stats_response, await _topics(username))


async def build_contests(username: str) -> UnifiedContests:
    contest_response, _ = await HackerRankService.get_contest_ranking(username)
    return contests_from(contest_response)


async def build_rating(username: str) -> UnifiedRating:
    return rating_from(await build_contests(username))


async def build_card(username: str) -> UnifiedCard:
    profile_response, stats_response, contest_response, badges_response, heatmap_response, scores = (
        await asyncio.gather(
            HackerRankService.get_user_profile(username),
            HackerRankService.get_user_stats(username),
            HackerRankService.get_contest_ranking(username),
            HackerRankService.get_user_badges(username),
            HackerRankService.get_user_heatmap(username),
            HackerRankAPI.fetch_user_scores(username),
        )
    )
    topics = topics_from_scores(scores[0]) if not scores[1] else []
    contests = contests_from(contest_response[0])
    return UnifiedCard(
        username=username,
        profile=profile_from(profile_response[0], username),
        stats=stats_from(stats_response[0], topics),
        contests=contests,
        rating=rating_from(contests),
        heatmap=heatmap_from(heatmap_response[0]),
        badges=badges_from(badges_response[0]),
    )
