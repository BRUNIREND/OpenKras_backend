from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from redis import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.redis import get_redis
from app.database.session import get_db
from app.models.user import User, UserRole
from app.services.AuthService import AuthService
from app.services.CategoryService import CategoryService
from app.services.ExcursionService import ExcursionService
from app.services.UserService import UserService


async def get_category_service(db: AsyncSession = Depends(get_db)) -> CategoryService:
    return CategoryService(db)

async def get_auth_service(
        db: AsyncSession = Depends(get_db),
        redis: Redis = Depends(get_redis)
) -> AuthService:
    return AuthService(db, redis)

async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

async def get_excursion_service(db: AsyncSession = Depends(get_db)) -> ExcursionService:
    return ExcursionService(db)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db),
        user_service: UserService = Depends(get_user_service)
) -> User:
    print(f"Пришедший токен: {token}")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось валидировать учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Декодируем JWT-токен
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        id: str = payload.get("sub")  # Обычно email зашивают в "sub" (subject)
        if id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await user_service.get_user_profile(int(id))
    if user is None:
        raise credentials_exception

    return user

async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Зависимость для проверки, является ли текущий пользователь администратором.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен. Требуются права администратора."
        )
    return current_user