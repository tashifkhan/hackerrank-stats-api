"""Builds the canonical cross-platform card for HackerRank by reusing the existing
``HackerRankService`` fetchers, deriving topic analysis from per-challenge
tracks and a rating time series from contest history.

See ../CANONICAL_SCHEMA.md for the wire format.
"""

import asyncio
from datetime import datetime, timezone
from typing import List, Optional

from models.canonical.badges import BadgeItem, Badges
from models.canonical.card import Card
from models.canonical.contests import ContestHistoryItem, Contests
from models.canonical.heatmap import HeatDay, Heatmap, YearContribution
from models.canonical.profile import Profile, Social
from models.canonical.rating import RatingPoint, Rating
from models.canonical.stats import TopicCount, Stats
from models.canonical.summary import Summary
from services import topics
from services.hackerrank_service import HackerRankService
from services.heatmap_window import window_heatmap


def _ts_to_date(timestamp) -> Optional[str]:
    if not timestamp:
        return None
    try:
        return datetime.fromtimestamp(int(timestamp), tz=timezone.utc).date().isoformat()
    except (ValueError, OSError, OverflowError):
        return None


# --- pure converters --------------------------------------------------------

def profile_from(profile_response, username: str) -> Profile:
    if profile_response is None:
        return Profile(username=username)
    p = profile_response.profile
    return Profile(
        displayName=p.realName or None,
        username=profile_response.username or username,
        avatar=p.userAvatar or None,
        country=p.countryName or None,
        institution=p.school or None,
        company=p.company or None,
        bio=p.aboutMe or None,
        websites=list(p.websites or []),
        social=Social(
            github=profile_response.githubUrl,
            twitter=profile_response.twitterUrl,
            linkedin=profile_response.linkedinUrl,
        ),
        verified=False,
    )


def stats_from(stats_response, topic_analysis: List[TopicCount]) -> Stats:
    if stats_response is None:
        return Stats(topicAnalysis=topic_analysis)
    return Stats(
        totalSolved=stats_response.totalSolved,
        totalQuestions=stats_response.totalQuestions or None,
        acceptanceRate=None,
        byDifficulty={
            "easy": stats_response.easySolved,
            "medium": stats_response.mediumSolved,
            "hard": stats_response.hardSolved,
        },
        topicAnalysis=topic_analysis,
    )


def contests_from(contest_response) -> Contests:
    if contest_response is None:
        return Contests()
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
    return Contests(
        count=contest_response.attendedContestsCount,
        rating=contest_response.rating or None,
        maxRating=max_rating,
        rank=contest_response.badge.name if contest_response.badge else None,
        globalRanking=contest_response.globalRanking or None,
        topPercentage=contest_response.topPercentage,
        history=history,
    )


def rating_from(contests: Contests) -> Rating:
    history = [
        RatingPoint(timestamp=h.timestamp, rating=h.rating, contestName=h.name)
        for h in contests.history
        if h.rating is not None
    ]
    return Rating(current=contests.rating, max=contests.maxRating, history=history)


def heatmap_from(heatmap_response) -> Heatmap:
    if heatmap_response is None:
        return Heatmap()
    return Heatmap(
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


def badges_from(badges_response) -> Badges:
    if badges_response is None:
        return Badges()
    items = [
        BadgeItem(id=str(b.id), name=b.displayName, icon=b.icon, level=None)
        for b in badges_response.badges
    ]
    active = None
    if badges_response.activeBadge:
        ab = badges_response.activeBadge
        active = BadgeItem(id=str(ab.id), name=ab.displayName, icon=ab.icon, level=None)
    return Badges(count=len(items), active=active, list=items)


def summary_from(card: Card) -> Summary:
    return Summary(
        totalSolved=card.stats.totalSolved,
        totalActiveDays=card.heatmap.totalActiveDays,
        totalContests=card.contests.count,
        currentRating=card.contests.rating,
        maxRating=card.contests.maxRating,
        rank=card.contests.rank,
        badgesCount=card.badges.count,
    )


# --- fetchers ---------------------------------------------------------------

async def build_stats(username: str) -> Stats:
    stats_response, _ = await HackerRankService.get_user_stats(username)
    return stats_from(stats_response, await topics.build_topic_analysis(username))


async def build_contests(username: str) -> Contests:
    contest_response, _ = await HackerRankService.get_contest_ranking(username)
    return contests_from(contest_response)


async def build_rating(username: str) -> Rating:
    return rating_from(await build_contests(username))


async def build_card(username: str) -> Card:
    profile_response, stats_response, contest_response, badges_response, heatmap_response, topic_analysis = (
        await asyncio.gather(
            HackerRankService.get_user_profile(username),
            HackerRankService.get_user_stats(username),
            HackerRankService.get_contest_ranking(username),
            HackerRankService.get_user_badges(username),
            HackerRankService.get_user_heatmap(username),
            topics.build_topic_analysis(username),
        )
    )
    contests = contests_from(contest_response[0])
    return Card(
        username=username,
        profile=profile_from(profile_response[0], username),
        stats=stats_from(stats_response[0], topic_analysis),
        contests=contests,
        rating=rating_from(contests),
        heatmap=window_heatmap(heatmap_from(heatmap_response[0]), "all", None),
        badges=badges_from(badges_response[0]),
    )
