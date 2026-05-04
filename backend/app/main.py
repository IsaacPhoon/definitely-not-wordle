from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.config import settings
from app.database import init_db
from app.game.router import router as game_router
from app.game.word_list import load_words
from app.stats.router import router as stats_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_words()
    await init_db()
    yield


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
