from pydantic import BaseModel

from models.badges import Badge, UpcomingBadge


class Contribution(BaseModel):
    points: int
    questionCount: int
    testcaseCount: int


class UserProfile(BaseModel):
    realName: str
    userAvatar: str
    birthday: str
    ranking: int
    reputation: int
    websites: list[str]
    countryName: str
    company: str
    school: str
    skillTags: list[str]
    aboutMe: str
    starRating: float


class RecentSubmission(BaseModel):
    title: str
    titleSlug: str
    timestamp: int
    statusDisplay: str
    lang: str


class ProfileResponse(BaseModel):
    status: str
    message: str
    username: str
    githubUrl: str | None
    twitterUrl: str | None
    linkedinUrl: str | None
    contributions: Contribution
    profile: UserProfile
    badges: list[Badge]
    upcomingBadges: list[UpcomingBadge]
    activeBadge: Badge | None
    submitStats: dict[str, list[dict[str, int | str]]]
    submissionCalendar: dict[str, int]
    recentSubmissions: list[RecentSubmission]

    @classmethod
    def error(cls, status: str, message: str) -> "ProfileResponse":
        return cls(
            status=status,
            message=message,
            username="",
            githubUrl=None,
            twitterUrl=None,
            linkedinUrl=None,
            contributions=Contribution(points=0, questionCount=0, testcaseCount=0),
            profile=UserProfile(
                realName="",
                userAvatar="",
                birthday="",
                ranking=0,
                reputation=0,
                websites=[],
                countryName="",
                company="",
                school="",
                skillTags=[],
                aboutMe="",
                starRating=0.0,
            ),
            badges=[],
            upcomingBadges=[],
            activeBadge=None,
            submitStats={"acSubmissionNum": [], "totalSubmissionNum": []},
            submissionCalendar={},
            recentSubmissions=[],
        )
