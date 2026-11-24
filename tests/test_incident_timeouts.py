"""Offline regressions for the Vercel 10s timeout incident."""

import asyncio
import os
import sys
import time
import unittest
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch

import httpx
from fastapi import HTTPException

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import cache, middleware, runtime, source  # noqa: E402
from main import app  # noqa: E402
from services import client  # noqa: E402


async def request(path):
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as http:
        return await http.get(path, headers={"Origin": "https://example.org"})


class RequestBudgetTests(unittest.IsolatedAsyncioTestCase):
    async def test_deadline_returns_504_with_cors_and_cancels_route(self):
        cancelled = asyncio.Event()

        async def stalled(username):
            try:
                await asyncio.sleep(60)
            finally:
                cancelled.set()

        with patch.object(runtime, "REQUEST_BUDGET_SECONDS", 0.05), patch.object(
            middleware, "redis_enabled", return_value=False
        ), patch("routes.topics.build_topic_analysis", side_effect=stalled):
            response = await request("/alice/topics")

        self.assertEqual(response.status_code, 504)
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertEqual(response.headers["access-control-allow-origin"], "https://example.org")
        self.assertTrue(cancelled.is_set())

    async def test_deadline_includes_cache_access(self):
        async def stalled(key):
            await asyncio.sleep(60)

        with patch.object(runtime, "REQUEST_BUDGET_SECONDS", 0.05), patch.object(
            middleware, "redis_enabled", return_value=True
        ), patch.object(middleware, "get_json", side_effect=stalled):
            response = await request("/alice/topics")
        self.assertEqual(response.status_code, 504)

    async def test_unavailable_topics_keep_body_shape_and_are_not_cached(self):
        stored = AsyncMock(return_value=True)
        with patch.object(middleware, "redis_enabled", return_value=True), patch.object(
            middleware, "get_json", AsyncMock(return_value=None)
        ), patch.object(middleware, "set_json", stored), patch(
            "core.enrichment.get_json", AsyncMock(return_value=None)
        ):
            response = await request("/alice/topics")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("meta", response.json())
        self.assertEqual(response.json()["data"], [])
        self.assertEqual(middleware.PARTIAL_TTL_SECONDS, 15)
        self.assertEqual(response.headers.get_list("cache-control"), ["no-store"])
        self.assertEqual(response.headers.get_list("cdn-cache-control"), ["no-store"])
        self.assertIn('"status":"unavailable"', response.headers["x-data-state"])
        stored.assert_not_awaited()


class StoreTests(unittest.IsolatedAsyncioTestCase):
    async def test_stalled_store_call_is_a_miss(self):
        class Stalled:
            async def get(self, key):
                await asyncio.sleep(60)

        with patch.object(cache, "get_redis", return_value=Stalled()), patch.object(cache, "OPERATION_TIMEOUT", 0.02):
            started = time.monotonic()
            self.assertIsNone(await cache.get_json("k"))
        self.assertLess(time.monotonic() - started, 1)

    async def test_lease_uses_nx_and_ex_keywords(self):
        commands = AsyncMock(return_value=True)
        with patch.object(source, "redis_enabled", return_value=True), patch.object(
            source, "get_json", AsyncMock(return_value=None)
        ), patch.object(source, "set_json", AsyncMock()), patch.object(source, "command", commands):
            self.assertEqual(await source.source("k", AsyncMock(return_value={"ok": 1})), {"ok": 1})
        lease = commands.await_args_list[0]
        self.assertEqual(lease.args[0], "set")
        self.assertEqual(lease.kwargs, {"ex": 10, "nx": True})

    async def test_failed_upstream_falls_back_to_stale_cache(self):
        stale = {"at": time.time() - 1000, "data": {"model": {"username": "alice"}}}
        failing = AsyncMock(side_effect=HTTPException(502, "HTTP 503"))
        with patch.object(source, "redis_enabled", return_value=False), patch.object(
            source, "get_json", AsyncMock(return_value=stale)
        ):
            async with httpx.AsyncClient() as http:
                token = runtime.state.set(runtime.RequestState(time.monotonic() + 5, http))
                try:
                    data = await source.source("k", failing)
                    meta = runtime.state.get().meta
                finally:
                    runtime.state.reset(token)
        self.assertEqual(data, stale["data"])
        self.assertEqual(meta["source"]["status"], "stale")

    async def test_failure_without_cache_still_raises(self):
        with patch.object(source, "redis_enabled", return_value=False), patch.object(
            source, "get_json", AsyncMock(return_value=None)
        ):
            with self.assertRaises(HTTPException):
                await source.source("k", AsyncMock(side_effect=HTTPException(502, "down")))


class UpstreamTests(unittest.IsolatedAsyncioTestCase):
    async def test_stalled_upstream_is_cut_off(self):
        class Stalled:
            async def get(self, *args, **kwargs):
                await asyncio.sleep(60)

        @asynccontextmanager
        async def fake_client():
            yield Stalled()

        with patch.object(client, "http_client", fake_client), patch.object(client, "UPSTREAM_TIMEOUT", 0.02):
            started = time.monotonic()
            data, error = await client.HackerRankAPI._fetch_json("https://example.invalid", default={})
        self.assertEqual((data, error), ({}, "HackerRank upstream unavailable"))
        self.assertLess(time.monotonic() - started, 1)

    async def test_history_uses_one_live_page_and_cached_older_pages(self):
        page = {"models": [{"ch_slug": "new"}, {"ch_slug": "both"}], "cursor": "c", "last_page": False}
        history = {"models": [{"ch_slug": "both"}, {"ch_slug": "old"}], "complete": True}
        live = AsyncMock(return_value=(page, None))
        with patch.object(client.HackerRankAPI, "fetch_recent_challenges", live), patch.object(
            client, "get_json", AsyncMock(return_value=history)
        ):
            data, error = await client.HackerRankAPI.fetch_all_recent_challenges("alice")
        self.assertIsNone(error)
        self.assertEqual([m["ch_slug"] for m in data["models"]], ["new", "both", "old"])
        self.assertTrue(data["last_page"])
        live.assert_awaited_once()

    async def test_history_failure_is_not_fatal(self):
        failed = ({"models": [], "cursor": None, "last_page": True}, "HTTP 500")
        with patch.object(client.HackerRankAPI, "fetch_recent_challenges", AsyncMock(return_value=failed)), patch.object(
            client, "get_json", AsyncMock(return_value=None)
        ), patch.object(client, "enqueue", AsyncMock(return_value=False)):
            data, error = await client.HackerRankAPI.fetch_all_recent_challenges("alice")
        self.assertIsNone(error)
        self.assertEqual(data["models"], [])
        self.assertFalse(data["last_page"])


if __name__ == "__main__":
    unittest.main()
