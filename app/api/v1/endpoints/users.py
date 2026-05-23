from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status
from mako.testing.helpers import result_lines
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.security import get_password_hash, verify_password, create_access_token
from app.database.session import get_db
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserRead, UserCreate, FavoriteUpdate, UserResponse
from typing import List
from sqlalchemy.orm import selectinload # Импортируем загрузчик

from app.services.UserService import UserService

user_router = APIRouter(prefix="/users", tags=["User"])


@user_router.post("/favorites", response_model=UserRead)
async def add_favorite(
    favorite_data: FavoriteUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)
    return await service.add_to_favorites(
        user_id=current_user.id,
        excursion_id=favorite_data.excursion_id
    )

@user_router.get(
    "/me",
    response_model=UserResponse,
    summary="Получить профиль текущего пользователя",
    description="Возвращает данные авторизованного пользователя на основе JWT-токена."
)
async def read_user_me(
    current_user: User = Depends(get_current_user)
):
    return current_user