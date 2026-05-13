from pydantic import BaseModel


class StatsResponse(BaseModel):
    status: str
    message: str
    totalSolved: int
    totalQuestions: int
    easySolved: int
    totalEasy: int
    mediumSolved: int
    totalMedium: int
    hardSolved: int
    totalHard: int
    acceptanceRate: float
    ranking: int
    contributionPoints: int
    practiceScore: int
    reputation: int
    submissionCalendar: dict[str, int]

    @classmethod
    def error(cls, status: str, message: str) -> "StatsResponse":
        return cls(
            status=status,
            message=message,
            totalSolved=0,
            totalQuestions=0,
            easySolved=0,
            totalEasy=0,
            mediumSolved=0,
            totalMedium=0,
            hardSolved=0,
            totalHard=0,
            acceptanceRate=0.0,
            ranking=0,
            contributionPoints=0,
            practiceScore=0,
            reputation=0,
            submissionCalendar={},
        )
