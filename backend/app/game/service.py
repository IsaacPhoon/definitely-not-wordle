from datetime import datetime, timezone

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Game, GameStatus, Guess, User


def compute_colors(guess: str, target: str) -> list[str]:
    result = ["gray"] * 5
    target_chars = list(target)

    for i in range(5):
        if guess[i] == target[i]:
            result[i] = "green"
            target_chars[i] = None

    for i in range(5):
        if result[i] == "green":
            continue
        if guess[i] in target_chars:
            result[i] = "yellow"
            target_chars[target_chars.index(guess[i])] = None

    return result


async def process_guess(
    game: Game,
    guess_word: str,
    attempt_number: int,
    session: AsyncSession,
) -> Guess:
    colors = compute_colors(guess_word, game.target_word)

    guess = Guess(
        game_id=game.id,
        word=guess_word,
        attempt_number=attempt_number,
        result=colors,
    )
    session.add(guess)

    if guess_word == game.target_word:
        game.status = GameStatus.WON
        game.completed_at = datetime.now(timezone.utc)
        await _update_stats(game.user, won=True, session=session)
    elif attempt_number >= 6:
        game.status = GameStatus.LOST
        game.completed_at = datetime.now(timezone.utc)
        await _update_stats(game.user, won=False, session=session)

    session.add(game)
    await session.commit()
    await session.refresh(guess)
    await session.refresh(game)
    return guess


async def _update_stats(
    user: User,
    *,
    won: bool,
    session: AsyncSession,
) -> None:
    user.games_played += 1
    if won:
        user.games_won += 1
        user.current_streak += 1
        if user.current_streak > user.max_streak:
            user.max_streak = user.current_streak
    else:
        user.current_streak = 0
    session.add(user)
