from datetime import datetime, timezone
from enum import StrEnum

import sqlalchemy as sa
from sqlmodel import Field, JSON, Column, Relationship, SQLModel


class GameStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    WON = "won"
    LOST = "lost"


# ── User ──────────────────────────────────────────────────────────────


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    password_hash: str
    is_guest: bool = False
    current_streak: int = 0
    max_streak: int = 0
    games_played: int = 0
    games_won: int = 0
    created_at: datetime = Field(
        sa_column=Column(sa.DateTime(timezone=True)),
        default_factory=lambda: datetime.now(timezone.utc),
    )
    games: list["Game"] = Relationship(back_populates="user")


class UserCreate(SQLModel):
    username: str
    password: str


class UserRead(UserBase):
    id: int
    current_streak: int
    max_streak: int
    games_played: int
    games_won: int


# ── Game ──────────────────────────────────────────────────────────────


class GameBase(SQLModel):
    status: GameStatus = GameStatus.IN_PROGRESS


class Game(GameBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    target_word: str
    created_at: datetime = Field(
        sa_column=Column(sa.DateTime(timezone=True)),
        default_factory=lambda: datetime.now(timezone.utc),
    )
    completed_at: datetime | None = Field(
        sa_column=Column(sa.DateTime(timezone=True), nullable=True),
        default=None,
    )
    user: User = Relationship(back_populates="games")
    guesses: list["Guess"] = Relationship(back_populates="game")


class GameRead(GameBase):
    id: int
    created_at: datetime
    target_word: str | None = None


# ── Guess ─────────────────────────────────────────────────────────────


class Guess(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    game_id: int = Field(foreign_key="game.id")
    word: str
    attempt_number: int
    result: list[str] = Field(sa_column=Column(JSON))
    created_at: datetime = Field(
        sa_column=Column(sa.DateTime(timezone=True)),
        default_factory=lambda: datetime.now(timezone.utc),
    )
    game: Game = Relationship(back_populates="guesses")


class GuessCreate(SQLModel):
    word: str


class GuessRead(SQLModel):
    word: str
    attempt_number: int
    result: list[str]
