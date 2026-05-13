import unittest
from datetime import date
from unittest.mock import patch

from services.decoders.common import ResponseDecoder


class HeatmapDecoderTests(unittest.TestCase):
    @patch("services.decoders.common.ResponseDecoder._utc_today")
    def test_decode_heatmap_builds_continuous_daily_series(self, mock_utc_today):
        mock_utc_today.return_value = date(2024, 1, 5)
        submission_history = {
            "1704067200": 2,
            "1704153600": 5,
            "1704326400": 1,
        }

        response = ResponseDecoder.decode_heatmap("heatmap-user", submission_history)

        self.assertEqual(response.status, "success")
        self.assertEqual(response.username, "heatmap-user")
        self.assertEqual(response.startDate, "2024-01-01")
        self.assertEqual(response.endDate, "2024-01-05")
        self.assertEqual(response.firstActiveDate, "2024-01-01")
        self.assertEqual(response.lastActiveDate, "2024-01-04")
        self.assertEqual(response.totalSubmissions, 8)
        self.assertEqual(response.activeDays, 3)
        self.assertEqual(response.currentStreak, 1)
        self.assertEqual(response.longestStreak, 2)
        self.assertEqual(response.maxDailySubmissions, 5)

        self.assertEqual(len(response.dailyContributions), 5)
        self.assertEqual(response.dailyContributions[0].date, "2024-01-01")
        self.assertEqual(response.dailyContributions[0].count, 2)
        self.assertEqual(response.dailyContributions[0].level, 2)
        self.assertEqual(response.dailyContributions[2].date, "2024-01-03")
        self.assertEqual(response.dailyContributions[2].count, 0)
        self.assertEqual(response.dailyContributions[2].level, 0)
        self.assertEqual(response.dailyContributions[3].date, "2024-01-04")
        self.assertEqual(response.dailyContributions[3].count, 1)
        self.assertEqual(response.dailyContributions[3].level, 1)

        self.assertEqual(len(response.yearlyContributions), 1)
        self.assertEqual(response.yearlyContributions[0].year, 2024)
        self.assertEqual(response.yearlyContributions[0].totalSubmissions, 8)
        self.assertEqual(response.yearlyContributions[0].activeDays, 3)

    def test_decode_heatmap_handles_empty_calendar(self):
        response = ResponseDecoder.decode_heatmap("empty-user", {})

        self.assertEqual(response.status, "success")
        self.assertEqual(response.username, "empty-user")
        self.assertEqual(response.totalSubmissions, 0)
        self.assertEqual(response.dailyContributions, [])
        self.assertEqual(response.yearlyContributions, [])


if __name__ == "__main__":
    unittest.main()
