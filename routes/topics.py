from fastapi import APIRouter

from models.canonical import make_envelope
from services.topics import build_topic_analysis


router = APIRouter(tags=["Canonical"])


@router.get("/{username}/topics")
async def get_topics(username: str):
    return make_envelope(username, await build_topic_analysis(username))
