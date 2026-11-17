from core.jobs import main
from core.enrichment import refresh_topics
from core.cache import get_json, set_json
from services.client import HackerRankAPI

async def discover(username, cursor):
    payload, error = await HackerRankAPI.fetch_recent_challenges(username, cursor)
    if error: raise RuntimeError('HackerRank history unavailable')
    models = [m for m in payload.get('models',[]) if isinstance(m,dict)]
    history = await get_json('hr:history:v2:'+username.lower()) if cursor else None
    prior = {m.get('ch_slug'):m for m in (history or {}).get('models',[])}
    prior.update({m.get('ch_slug'):m for m in models})
    complete = bool(payload.get('last_page', False))
    next_cursor = payload.get('cursor')
    if not complete and not next_cursor: raise RuntimeError('Missing history cursor')
    if not await set_json('hr:history:v2:'+username.lower(), {'models':list(prior.values()), 'complete':complete, 'cursor':next_cursor}, 604800):
        raise RuntimeError('History checkpoint could not be stored')
    return [m['ch_slug'] for m in models if m.get('ch_slug')], next_cursor, complete

async def tags(slug):
    model, error = await HackerRankAPI.fetch_challenge_detail(slug)
    if error or not model: raise RuntimeError('Challenge metadata unavailable')
    track = (model.get('track') or {}).get('name')
    return [track] if track else []

async def handle(job): return await refresh_topics(job, discover, tags)
if __name__ == '__main__': main(handle)
