from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import delete
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.router import router as auth_router
from app.config import settings
from app.database import engine, init_db
from app.game.router import router as game_router
from app.game.word_list import load_words
from app.models import User
from app.stats.router import router as stats_router


async def cleanup_guests():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    async with AsyncSession(engine) as session:
        await session.exec(
            delete(User).where(User.is_guest == True, User.created_at < cutoff)
        )
        await session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_words()
    await init_db()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(cleanup_guests, "interval", hours=1)
    scheduler.start()

    yield

    scheduler.shutdown()


app = FastAPI(title="Definitely Not Wordle", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(game_router)
app.include_router(stats_router)
