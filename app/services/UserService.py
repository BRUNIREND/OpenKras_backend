from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user import user_repo
from app.repositories.excursion import excursion_repo  # Нужен для проверки существования экскурсии
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from app.models.user import User


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
    async def create_user(self, user_in: UserCreate) -> User:
        """Регистрация нового пользователя с проверкой email и хешированием пароля"""
        # 1. Проверяем, не занят ли email
        existing_user = await user_repo.get_by_email(self.db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )

        # 2. Хешируем пароль перед сохранением
        user_data = user_in.model_dump()
        password = user_data.pop("password")
        user_data["hashed_password"] = get_password_hash(password)

        # 3. Создаем запись через репозиторий
        new_user = User(**user_data)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def get_user_profile(self, user_id: int) -> Optional[User]:
        """Получение профиля со всеми связями (избранным)"""
        user = await user_repo.get_with_favorites(self.db, user_id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Получение профиля со всеми связями (избранным)"""
        user = await user_repo.get_by_email(self.db, email=email)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return user

    async def add_to_favorites(self, user_id: int, excursion_id: int) -> User:
        """Добавление экскурсии в список избранного"""
        # 1. Загружаем пользователя с его текущим списком избранного
        user = await user_repo.get_with_favorites(self.db, user_id=user_id)

        # 2. Проверяем, существует ли такая экскурсия вообще
        excursion = await excursion_repo.get(self.db, id=excursion_id)
        if not excursion:
            raise HTTPException(status_code=404, detail="Экскурсия не найдена")

        # 3. Проверяем, нет ли её уже в списке (чтобы не дублировать)
        if excursion in user.favorites:
            raise HTTPException(status_code=400, detail="Экскурсия уже в избранном")

        # 4. Добавляем в связь
        user.favorites.append(excursion)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def remove_from_favorites(self, user_id: int, excursion_id: int) -> User:
        """Удаление экскурсии из избранного"""
        user = await user_repo.get_with_favorites(self.db, user_id=user_id)
        excursion = await excursion_repo.get(self.db, id=excursion_id)

        if excursion in user.favorites:
            user.favorites.remove(excursion)
            await self.db.commit()
            await self.db.refresh(user)
        return user