from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import delete
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.router import router as auth_router
from app.config import settings
from app.database import engine, init_db
from app.game.router import router as game_router
from app.game.word_list import load_words
from app.models import Game, Guess, User
from app.stats.router import router as stats_router


async def cleanup_guests():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    async with AsyncSession(engine) as session:
        users_result = await session.exec(
            select(User.id).where(User.is_guest == True, User.created_at < cutoff)
        )
        user_ids = users_result.all()
        if not user_ids:
            return

        game_ids_result = await session.exec(
            select(Game.id).where(Game.user_id.in_(user_ids))
        )
        game_ids = game_ids_result.all()

        if game_ids:
            await session.exec(delete(Guess).where(Guess.game_id.in_(game_ids)))
            await session.exec(delete(Game).where(Game.id.in_(game_ids)))

        await session.exec(delete(User).where(User.id.in_(user_ids)))
        await session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_words()
    if settings.environment.lower() == "development":
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
