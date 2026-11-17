from core.enrichment import read_topics
from models.canonical.stats import TopicCount

async def build_topic_analysis(username):
    from services.refresh import handle as refresh_handler

    return [TopicCount(**row) for row in await read_topics(username, refresh_handler)]
