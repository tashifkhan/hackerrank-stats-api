from pydantic import BaseModel


class Badge(BaseModel):
    id: str
    displayName: str
    icon: str
    creationDate: int


class UpcomingBadge(BaseModel):
    name: str
    icon: str


class BadgesResponse(BaseModel):
    status: str
    message: str
    badges: list[Badge]
    upcomingBadges: list[UpcomingBadge]
    activeBadge: Badge | None

    @classmethod
    def error(cls, status: str, message: str) -> "BadgesResponse":
        return cls(
            status=status,
            message=message,
            badges=[],
            upcomingBadges=[],
            activeBadge=None,
        )
