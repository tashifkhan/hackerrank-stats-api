from pydantic import BaseModel


class ContestBadge(BaseModel):
    name: str


class ContestInfo(BaseModel):
    title: str
    startTime: int


class ContestHistoryEntry(BaseModel):
    attended: bool
    rating: int
    ranking: int
    trendDirection: str
    problemsSolved: int
    totalProblems: int
    finishTimeInSeconds: int
    contest: ContestInfo


class ContestRankingResponse(BaseModel):
    status: str
    message: str
    attendedContestsCount: int
    rating: int
    globalRanking: int
    totalParticipants: int
    topPercentage: float
    badge: ContestBadge | None
    contestHistory: list[ContestHistoryEntry]

    @classmethod
    def error(cls, status: str, message: str) -> "ContestRankingResponse":
        return cls(
            status=status,
            message=message,
            attendedContestsCount=0,
            rating=0,
            globalRanking=0,
            totalParticipants=0,
            topPercentage=0.0,
            badge=None,
            contestHistory=[],
        )
