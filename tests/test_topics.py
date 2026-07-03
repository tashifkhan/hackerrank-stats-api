"""Offline tests for HackerRank topic-track aggregation (see ../CANONICAL_SCHEMA.md)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services import topics  # noqa: E402


PAGES = [
    {
        "models": [
            {"ch_slug": "sherlock-and-anagrams"},
            {"ch_slug": "two-strings"},
        ],
        "cursor": "next-page",
        "last_page": False,
    },
    {
        "models": [{"ch_slug": "climbing-the-leaderboard"}],
        "cursor": "",
        "last_page": True,
    },
]

TRACKS = {
    "sherlock-and-anagrams": {"track": {"name": "Strings"}},
    "two-strings": {"track": {"name": "Strings"}},
    "climbing-the-leaderboard": {"track": {"name": "Implementation"}},
}


class TopicAnalysisTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        topics._TRACK_CACHE.clear()

    async def test_all_solved_slugs_paginates_via_cursor(self):
        calls = []

        async def fake_fetch_recent_challenges(username, cursor=None):
            calls.append(cursor)
            return PAGES[len(calls) - 1], None

        from services.client import HackerRankAPI

        original = HackerRankAPI.fetch_recent_challenges
        HackerRankAPI.fetch_recent_challenges = staticmethod(fake_fetch_recent_challenges)
        try:
            slugs = await topics._all_solved_slugs("demo")
        finally:
            HackerRankAPI.fetch_recent_challenges = original

        self.assertEqual(
            slugs, ["sherlock-and-anagrams", "two-strings", "climbing-the-leaderboard"]
        )
        self.assertEqual(calls, [None, "next-page"])

    async def test_build_topic_analysis_tallies_and_sorts(self):
        async def fake_all_solved_slugs(username):
            return [
                "sherlock-and-anagrams",
                "two-strings",
                "climbing-the-leaderboard",
            ]

        async def fake_fetch_challenge_detail(slug):
            return TRACKS.get(slug), None

        from services.client import HackerRankAPI

        original_slugs = topics._all_solved_slugs
        original_detail = HackerRankAPI.fetch_challenge_detail
        topics._all_solved_slugs = fake_all_solved_slugs
        HackerRankAPI.fetch_challenge_detail = staticmethod(fake_fetch_challenge_detail)
        try:
            result = await topics.build_topic_analysis("demo")
        finally:
            topics._all_solved_slugs = original_slugs
            HackerRankAPI.fetch_challenge_detail = original_detail

        as_dict = {t.topic: t.count for t in result}
        self.assertEqual(as_dict, {"Strings": 2, "Implementation": 1})
        self.assertEqual(result[0].topic, "Strings")

    async def test_build_topic_analysis_empty_when_no_slugs(self):
        async def fake_all_solved_slugs(username):
            return []

        original = topics._all_solved_slugs
        topics._all_solved_slugs = fake_all_solved_slugs
        try:
            result = await topics.build_topic_analysis("demo")
        finally:
            topics._all_solved_slugs = original

        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
