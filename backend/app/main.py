from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import get_settings
from app.database import engine
from app.routers import haaletus, inimesed, logi, tulemused

settings = get_settings()

app = FastAPI(
    title="Haaletussusteem API",
    description="I osa - haaletussusteemi andmebaas ja API.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inimesed.router)
app.include_router(haaletus.router)
app.include_router(tulemused.router)
app.include_router(logi.router)


@app.get("/api/health", tags=["service"])
def health() -> dict[str, object]:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    return {
        "status": "ok" if db_ok else "degraded",
        "database": db_ok,
        "vote_duration_seconds": settings.vote_duration_seconds,
    }
