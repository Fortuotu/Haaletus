from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import get_settings
from app.database import engine
from app.routers import inimesed

settings = get_settings()

app = FastAPI(
    title="Hääletussüsteem API",
    description="I osa – hääletussüsteemi andmebaas ja API (boilerplate).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inimesed.router)


@app.get("/api/health", tags=["service"])
def health() -> dict[str, object]:
    """Teenuse ja andmebaasiühenduse kontroll."""
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
