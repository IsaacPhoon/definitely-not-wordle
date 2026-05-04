from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.models import User, UserRead

router = APIRouter(prefix="/users", tags=["stats"])


@router.get("/me/stats", response_model=UserRead)
async def get_stats(user: User = Depends(get_current_user)):
    return user
