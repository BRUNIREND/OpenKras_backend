from typing import Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user_otp import UserOTP
from app.repositories.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
import random
from datetime import datetime, timedelta


class UserRepository(CRUDBase[User, UserCreate, UserUpdate]):

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(select(self.model).where(self.model.email == email))
        return result.scalar_one_or_none()

    async def get_with_favorites(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """Получить пользователя вместе со списком избранных экскурсий"""
        result = await db.execute(
            select(self.model)
            .options(selectinload(self.model.favorites))  # Загружаем связанные данные
            .where(self.model.id == user_id)
        )
        return result.scalar_one_or_none()




# Создаем объект репозитория
user_repo = UserRepository(User)