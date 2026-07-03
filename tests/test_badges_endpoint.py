import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.badges import Badge, BadgesResponse  # noqa: E402
from routes.badges import get_user_badges  # noqa: E402


async def _successful_badges(username):
    return (
        BadgesResponse(
            status="success",
            message="ok",
            badges=[
                Badge(id="python:gold:5", displayName="Python", icon="https://example.com/python.svg", creationDate=1),
            ],
            upcomingBadges=[],
            activeBadge=None,
        ),
        None,
    )


async def _failed_badges(username):
    return None, "user not found"


class BadgeEndpointTests(unittest.IsolatedAsyncioTestCase):
    async def test_badges_endpoint_returns_canonical_envelope(self):
        with patch("routes.badges.fetch_user_badges", _successful_badges):
            payload = await get_user_badges("alice")

        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["platform"], "hackerrank")
        self.assertEqual(payload["username"], "alice")
        self.assertEqual(payload["data"]["count"], 1)
        self.assertEqual(payload["data"]["list"][0]["name"], "Python")

    async def test_badges_endpoint_preserves_error_envelope(self):
        with patch("routes.badges.fetch_user_badges", _failed_badges):
            payload = await get_user_badges("missing")

        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["message"], "user not found")
        self.assertIsNone(payload["data"])


if __name__ == "__main__":
    unittest.main()
