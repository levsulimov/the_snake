import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from redis.asyncio import Redis

from app.api.max_webhook import router as max_router
from app.api.routes import router as api_router
from app.config import get_settings
from app.database.database import SessionLocal, engine
from app.database.models import Base
from app.services.documents import seed_documents
from app.services.faq import seed_faq
from app.utils.logger import configure_logging

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]


async def seed_knowledge_base() -> None:
    async with SessionLocal() as session:
        await seed_faq(session, json.loads((ROOT / "knowledge_base/faq.json").read_text(encoding="utf-8")))
        await seed_documents(session, json.loads((ROOT / "knowledge_base/documents.json").read_text(encoding="utf-8")))


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    await seed_knowledge_base()
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    try:
        await redis.ping()
        app.state.redis = redis
    except Exception:
        logger.warning("Redis is unavailable; bot will continue without cache", exc_info=True)
        await redis.aclose()
        app.state.redis = None
    yield
    if app.state.redis:
        await app.state.redis.aclose()
    await engine.dispose()


app = FastAPI(title="UniBot", version="1.0.0", lifespan=lifespan)
app.include_router(api_router, prefix="/api")
app.include_router(max_router, prefix="/api")
