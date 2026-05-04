from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.utils import create_access_token, hash_password, verify_password
from app.config import settings
from app.database import get_session
from app.models import User, UserCreate
from app.ratelimit import limiter

router = APIRouter(prefix="/auth", tags=["auth"])


def _client_ip(request: Request) -> str:
    # Demo-friendly: prefer direct client host. If behind a proxy, you can
    # swap to X-Forwarded-For parsing.
    return request.client.host if request.client else "unknown"


def _enforce_rate_limit(
    response: Response,
    *,
    key: str,
    limit: int,
    window_seconds: int,
) -> None:
    result = limiter.check(key=key, limit=limit, window_seconds=window_seconds)
    if result.allowed:
        return
    response.headers["Retry-After"] = str(result.retry_after_seconds)
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Too many requests",
        headers={"Retry-After": str(result.retry_after_seconds)},
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    body: UserCreate,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    ip = _client_ip(request)
    _enforce_rate_limit(response, key=f"register:ip:{ip}", limit=10, window_seconds=60)

    existing = await session.exec(select(User).where(User.username == body.username))
    if existing.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )
    user = User(username=body.username, password_hash=hash_password(body.password))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    token = create_access_token(user.id, settings.secret_key)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login")
async def login(
    body: UserCreate,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    ip = _client_ip(request)
    username = body.username.strip().lower()
    _enforce_rate_limit(response, key=f"login:ip:{ip}", limit=20, window_seconds=60)
    _enforce_rate_limit(
        response, key=f"login:user:{username}", limit=10, window_seconds=10 * 60
    )

    user = (
        await session.exec(select(User).where(User.username == body.username))
    ).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_access_token(user.id, settings.secret_key)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/guest", status_code=status.HTTP_201_CREATED)
async def guest_login(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    ip = _client_ip(request)
    _enforce_rate_limit(response, key=f"guest:ip:{ip}", limit=10, window_seconds=60)

    username = f"guest_{uuid4().hex[:8]}"
    user = User(username=username, password_hash="", is_guest=True)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    token = create_access_token(user.id, settings.secret_key)
    return {"access_token": token, "token_type": "bearer"}
