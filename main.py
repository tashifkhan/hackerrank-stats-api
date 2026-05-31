from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.badges import router as badges_router
from routes.contests import router as contests_router
from routes.docs import router as docs_router
from routes.heatmap import router as heatmap_router
from routes.profiles import router as profiles_router
from routes.stats import router as stats_router
from routes.unified import router as unified_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="HackerRank Stats API",
        description="A FastAPI service for exploring public HackerRank profiles, stats, and activity.",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(docs_router)
    app.include_router(contests_router)
    app.include_router(profiles_router)
    app.include_router(badges_router)
    app.include_router(heatmap_router)
    app.include_router(unified_router)
    app.include_router(stats_router)
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=58352, reload=True)
