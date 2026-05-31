"""Canonical unified endpoints shared across all stats services.

Adds ``/{username}/stats``, ``/{username}/rating`` and the aggregated
``/{username}/card``. See ../UNIFIED_SCHEMA.md.
"""

from fastapi import APIRouter

from models.unified import make_envelope
from services import unified_mapper

router = APIRouter()


@router.get("/{username}/stats")
async def get_unified_stats(username: str):
    return make_envelope(username, await unified_mapper.build_stats(username))


@router.get("/{username}/rating")
async def get_unified_rating(username: str):
    return make_envelope(username, await unified_mapper.build_rating(username))


@router.get("/{username}/card")
async def get_unified_card(username: str):
    return make_envelope(username, await unified_mapper.build_card(username))
