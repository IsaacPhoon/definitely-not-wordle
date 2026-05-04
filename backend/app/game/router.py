from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_session
from app.game.service import process_guess
from app.game.word_list import get_random_target, is_valid_guess
from app.models import (
    Game,
    GameRead,
    GameStatus,
    Guess,
    GuessCreate,
    GuessRead,
    User,
)

router = APIRouter(prefix="/games", tags=["games"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=GameRead)
async def create_game(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    game = Game(
        user_id=user.id,
        target_word=get_random_target(),
    )
    session.add(game)
    await session.commit()
    await session.refresh(game)
    return GameRead(
        id=game.id,
        status=game.status,
        created_at=game.created_at,
    )


@router.get("/{game_id}", response_model=GameRead)
async def get_game(
    game_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    game = await session.get(Game, game_id)
    if not game or game.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

    target = game.target_word if game.status != GameStatus.IN_PROGRESS else None
    return GameRead(
        id=game.id,
        status=game.status,
        created_at=game.created_at,
        target_word=target,
    )


@router.get("/{game_id}/guesses", response_model=list[GuessRead])
async def get_guesses(
    game_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    game = await session.get(Game, game_id)
    if not game or game.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

    result = await session.exec(
        select(Guess).where(Guess.game_id == game_id).order_by(Guess.attempt_number)
    )
    return result.all()


@router.post("/{game_id}/guess")
async def submit_guess(
    game_id: int,
    body: GuessCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    game = await session.get(Game, game_id)
    if not game or game.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

    if game.status != GameStatus.IN_PROGRESS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Game is already over")

    word = body.word.lower().strip()

    if len(word) != 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Word must be exactly 5 letters")

    if not is_valid_guess(word):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not a valid word")

    attempts_result = await session.exec(
        select(func.count()).select_from(Guess).where(Guess.game_id == game_id)
    )
    attempt_number = int(attempts_result.one()) + 1

    if attempt_number > 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No attempts remaining",
        )

    guess = await process_guess(game, word, attempt_number, session)

    await session.refresh(game)
    target = game.target_word if game.status != GameStatus.IN_PROGRESS else None

    return {
        "guess": GuessRead(
            word=guess.word,
            attempt_number=guess.attempt_number,
            result=guess.result,
        ),
        "game": GameRead(
            id=game.id,
            status=game.status,
            created_at=game.created_at,
            target_word=target,
        ),
    }
