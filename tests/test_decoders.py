import unittest

from services.decoders.common import ResponseDecoder


class HackerRankDecoderTests(unittest.TestCase):
    def test_decode_stats_splits_solved_count_from_practice_score(self):
        response = ResponseDecoder.decode_stats(
            {"level": 5, "followers_count": 2},
            [
                {"name": "General Programming", "practice": {"score": 0, "rank": 1}},
                {"name": "C++", "practice": {"score": 70, "rank": 527450}},
                {"name": "Python", "practice": {"score": 30, "rank": 4}},
            ],
            {"2024-01-01": 125},
            {"models": [{"badge_name": "C++", "solved": 8}]},
            {"models": [{"ch_slug": "one"}, {"ch_slug": "two"}, {"ch_slug": "one"}]},
        )

        self.assertEqual(response.totalSolved, 8)
        self.assertEqual(response.totalQuestions, 0)
        self.assertEqual(response.practiceScore, 100)
        self.assertEqual(response.acceptanceRate, 0.0)
        self.assertEqual(response.ranking, 4)

    def test_decode_profile_builds_tracks_and_keeps_unknown_recent_dates_at_zero(self):
        response = ResponseDecoder.decode_profile(
            {"username": "alice", "name": "Alice"},
            [{"name": "C++", "practice": {"score": 70, "rank": 1}}],
            {"models": [{"badge_name": "C++", "solved": 8}]},
            {"2024-01-01": 125},
            {"models": [{"name": "Structs", "slug": "structs", "status": "Solved"}]},
        )

        self.assertEqual(response.submitStats["totalSubmissionNum"][0]["submissions"], 125)
        self.assertEqual(response.submitStats["acSubmissionNum"][0]["difficulty"], "C++")
        self.assertEqual(response.submitStats["acSubmissionNum"][0]["rank"], 1)
        self.assertEqual(response.contributions.questionCount, 8)
        self.assertEqual(response.recentSubmissions[0].timestamp, 0)

    def test_decode_profile_parses_recent_challenge_timezone_dates(self):
        response = ResponseDecoder.decode_profile(
            {"username": "alice", "name": "Alice"},
            [],
            {"models": []},
            {},
            {"models": [{"name": "Structs", "ch_slug": "c-tutorial-struct", "created_at": "2023-10-10T05:10:00.000+00:00"}]},
        )

        self.assertEqual(response.recentSubmissions[0].titleSlug, "c-tutorial-struct")
        self.assertGreater(response.recentSubmissions[0].timestamp, 0)

    def test_decode_badges_normalizes_relative_and_nested_icons(self):
        response = ResponseDecoder.decode_badges(
            {
                "models": [
                    {
                        "badge_name": "C++",
                        "badge_type": "language",
                        "level": 5,
                        "icon": {"small": "/assets/badges/cpp.svg"},
                    },
                    {
                        "badge_name": "Python",
                        "badge_type": "language",
                        "level": 3,
                        "badge_icon": "//hrcdn.net/badges/python.svg",
                    },
                ]
            }
        )

        self.assertEqual(response.badges[0].icon, "https://www.hackerrank.com/assets/badges/cpp.svg")
        self.assertEqual(response.badges[1].icon, "https://hrcdn.net/badges/python.svg")


if __name__ == "__main__":
    unittest.main()
