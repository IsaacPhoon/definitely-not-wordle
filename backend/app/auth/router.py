from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.utils import create_access_token, hash_password, verify_password
from app.config import settings
from app.database import get_session
from app.models import User, UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    body: UserCreate,
    session: AsyncSession = Depends(get_session),
):
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
    session: AsyncSession = Depends(get_session),
):
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
async def guest_login(session: AsyncSession = Depends(get_session)):
    username = f"guest_{uuid4().hex[:8]}"
    user = User(username=username, password_hash="", is_guest=True)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    token = create_access_token(user.id, settings.secret_key)
    return {"access_token": token, "token_type": "bearer"}
