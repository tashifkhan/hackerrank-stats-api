"""Offline tests for HackerRank topic-track aggregation (see ../CANONICAL_SCHEMA.md).

Topics no longer resolve inline. A refresh job discovers solved slugs page by
page, resolves each slug's track in small batches, and publishes a snapshot that
requests read from the cache.
"""

import os
import sys
import unittest
from unittest.mock import AsyncMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import enrichment  # noqa: E402
from services import refresh, topics  # noqa: E402


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


class FakeJob:
    def __init__(self, subject):
        self.payload = {"subject": subject}
        self.data = {}

    async def save(self):
        return None


class FakeStore:
    def __init__(self):
        self.values = {}

    async def get_json(self, key):
        return self.values.get(key)

    async def get_many(self, keys):
        return [self.values.get(key) for key in keys]

    async def set_json(self, key, value, ttl):
        self.values[key] = value
        return True


class TopicAnalysisTests(unittest.IsolatedAsyncioTestCase):
    def store(self):
        store = FakeStore()
        patches = [
            patch.object(enrichment, "get_json", store.get_json),
            patch.object(enrichment, "get_many", store.get_many),
            patch.object(enrichment, "set_json", store.set_json),
            patch.object(refresh, "get_json", store.get_json),
            patch.object(refresh, "set_json", store.set_json),
            patch.object(enrichment, "enqueue", AsyncMock(return_value=False)),
        ]
        for item in patches:
            item.start()
            self.addCleanup(item.stop)
        return store

    async def test_refresh_paginates_then_tallies_and_sorts(self):
        self.store()
        calls = []

        async def fake_recent(username, cursor=None):
            calls.append(cursor)
            return PAGES[len(calls) - 1], None

        async def fake_detail(slug):
            return TRACKS.get(slug), None

        job = FakeJob("demo")
        with patch.object(refresh.HackerRankAPI, "fetch_recent_challenges", fake_recent), patch.object(
            refresh.HackerRankAPI, "fetch_challenge_detail", fake_detail
        ):
            done = [await refresh.handle(job) for _ in range(2)]

        self.assertEqual(calls, [None, "next-page"])
        self.assertEqual(done, [False, True])
        result = await topics.build_topic_analysis("demo")
        self.assertEqual([(t.topic, t.count) for t in result], [("Strings", 2), ("Implementation", 1)])

    async def test_failed_track_lookup_is_not_cached(self):
        store = self.store()

        async def fake_recent(username, cursor=None):
            return PAGES[1], None

        async def failed_detail(slug):
            return None, "HackerRank upstream unavailable"

        job = FakeJob("demo")
        with patch.object(refresh.HackerRankAPI, "fetch_recent_challenges", fake_recent), patch.object(
            refresh.HackerRankAPI, "fetch_challenge_detail", failed_detail
        ):
            with self.assertRaises(RuntimeError):
                await refresh.handle(job)

        self.assertNotIn(enrichment.tag_key("climbing-the-leaderboard"), store.values)
        self.assertNotIn(enrichment.key("demo"), store.values)

    async def test_build_topic_analysis_empty_without_snapshot(self):
        self.store()
        self.assertEqual(await topics.build_topic_analysis("demo"), [])


if __name__ == "__main__":
    unittest.main()
