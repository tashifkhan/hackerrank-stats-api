from pydantic import BaseModel


class HeatmapDay(BaseModel):
    date: str
    timestamp: int
    count: int
    level: int


class YearlyContribution(BaseModel):
    year: int
    totalSubmissions: int
    activeDays: int


class HeatmapResponse(BaseModel):
    status: str
    message: str
    username: str
    startDate: str
    endDate: str
    firstActiveDate: str
    lastActiveDate: str
    totalSubmissions: int
    activeDays: int
    currentStreak: int
    longestStreak: int
    maxDailySubmissions: int
    dailyContributions: list[HeatmapDay]
    yearlyContributions: list[YearlyContribution]

    @classmethod
    def error(cls, status: str, message: str) -> "HeatmapResponse":
        return cls(
            status=status,
            message=message,
            username="",
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
