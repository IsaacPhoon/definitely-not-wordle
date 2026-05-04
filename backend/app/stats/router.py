from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_session
from app.models import Game, GameHistoryItem, GameStatus, Guess, User, UserRead

router = APIRouter(prefix="/users", tags=["stats"])


@router.get("/me/stats", response_model=UserRead)
async def get_stats(user: User = Depends(get_current_user)):
    return user


@router.get("/me/history", response_model=list[GameHistoryItem])
async def get_history(
    limit: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(
        select(
            Game,
            func.count(Guess.id).label("attempts_used"),
        )
        .outerjoin(Guess, Guess.game_id == Game.id)
        .where(
            Game.user_id == user.id,
            Game.status.in_([GameStatus.WON, GameStatus.LOST]),
        )
        .group_by(Game.id)
        .order_by(Game.completed_at.desc().nullslast(), Game.created_at.desc())
        .limit(limit)
    )

    items: list[GameHistoryItem] = []
    for game, attempts_used in result.all():
        items.append(
            GameHistoryItem(
                game_id=game.id,
                status=game.status,
                created_at=game.created_at,
                completed_at=game.completed_at,
                target_word=game.target_word,
                attempts_used=int(attempts_used or 0),
            )
        )

    return items
