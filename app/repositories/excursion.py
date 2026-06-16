import uuid
from typing import List, Optional

from sqlalchemy import select, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Excursion, Point, PointContent, User
from app.models.assocations import user_favorite_excursions
from app.models.excursion import ExcursionStatus
from app.repositories.base import CRUDBase
from app.schemas.excursion import ExcursionCreate2, ExcursionUpdate, ExcursionCreate
from sqlalchemy.orm import selectinload


class ExcursionRepository(CRUDBase[Excursion, ExcursionCreate2, ExcursionUpdate]):

    async def exists(self, db: AsyncSession, id: int) -> bool:
        stmt = select(Excursion.id).where(Excursion.id == id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None
    async def get_by_title(self, db: AsyncSession, title: str):
        """Поиск экскурсии по точному названию"""
        result = await db.execute(select(Excursion).where(Excursion.title == title))
        return result.scalar_one_or_none()

    async def get_with_points(self, db: AsyncSession, id: int):
        """Получить экскурсию и сразу загрузить все её точки."""
        query = select(self.model).options(selectinload(self.model.points)).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_published_short(
            self,
            db: AsyncSession,
            current_user_id: int,  # Передаем id текущего юзера
            skip: int = 0,
            limit: int = 100
    ) -> list[Excursion]:
        """Получить облегченный список опубликованных экскурсий с разметкой избранного"""

        fav_query = select(user_favorite_excursions.c.excursion_id).where(
            user_favorite_excursions.c.user_id == current_user_id
        )
        fav_result = await db.execute(fav_query)
        favorite_ids = set(fav_result.scalars().all())

        # 2. Базовый запрос экскурсий
        query = (
            select(self.model)
            .where(Excursion.status == ExcursionStatus.PUBLISHED)
            .options(selectinload(Excursion.images))  # Только картинка для превью карточки
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(query)
        excursions = result.scalars().all()
        # 3. Проставляем флаги
        for excursion in excursions:
            print(excursion.images)
            excursion.is_favorite = excursion.id in favorite_ids

        return excursions

    async def get_all_with_points(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Excursion]:
        """Получить список всех экскурсий, в каждой из которых уже будут вложены точки"""
        query = (
            select(self.model)
            .where(Excursion.status == ExcursionStatus.PUBLISHED)
            .options(
                # Грузим обложку
                selectinload(Excursion.images),
                # Грузим точки
                selectinload(Excursion.points)
                    .selectinload(Point.contents)
                    .selectinload(PointContent.media)
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_with_points_one(self, db: AsyncSession, excursion_id: int) -> Excursion:
        """Получить список всех экскурсий, в каждой из которых уже будут вложены точки"""
        query = (
            select(self.model)
            .where(Excursion.id == excursion_id)
            .options(
                # Грузим обложку
                selectinload(Excursion.images),
                # Грузим точки
                selectinload(Excursion.points)
                    .selectinload(Point.contents)
                    .selectinload(PointContent.media)
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()


    async def get_all_raw(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Excursion]:
        """Получить список всех экскурсий, в каждой из которых уже будут вложены точки"""
        query = (
            select(self.model)
            .options(
                # Грузим обложку
                selectinload(Excursion.images),
                # Грузим точки
                selectinload(Excursion.points)
                    .selectinload(Point.contents)
                    .selectinload(PointContent.media)
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        data = result.scalars().all()

        return data

    async def update(self,db, excursion_id: int, obj_in: ExcursionCreate) -> Optional[Excursion]:
        # 1. Получаем текущую экскурсию из базы
        query = select(Excursion).where(Excursion.id == excursion_id)
        result = await db.execute(query)
        db_excursion = result.scalar_one_or_none()

        if not db_excursion:
            return None

        # 2. Превращаем Pydantic-схему в словарь (исключая неустановленные поля)
        update_data = obj_in.model_dump(exclude_unset=True)

        # 3. Обновляем атрибуты модели динамически
        for field in update_data:
            if hasattr(db_excursion, field):
                setattr(db_excursion, field, update_data[field])

        # 4. Фиксируем изменения в БД
        db.add(db_excursion)
        await db.commit()
        await db.refresh(db_excursion)

        return db_excursion

    async def add_to_favorites(self, db: AsyncSession, user_id: int, excursion_id: int) -> bool:
        """Добавить экскурсию в избранное. Возвращает True в случае успеха"""
        try:
            # insert в Core-таблицу передается через values()
            stmt = insert(user_favorite_excursions).values(
                user_id=user_id,
                excursion_id=excursion_id
            )
            await db.execute(stmt)
            await db.commit()
            return True
        except Exception:
            await db.rollback()
            return False

    async def remove_from_favorites(self, db: AsyncSession, user_id: int, excursion_id: int) -> bool:
        """Удалить экскурсию из избранного. Возвращает True в случае успеха"""
        try:
            stmt = delete(user_favorite_excursions).where(
                user_favorite_excursions.c.user_id == user_id,
                user_favorite_excursions.c.excursion_id == excursion_id
            )
            await db.execute(stmt)
            await db.commit()
            return True
        except Exception:
            await db.rollback()
            return False

    async def get_user_favorites(self, db:AsyncSession, user_id: int) -> List[Excursion]:
        """
        Запрашивает из БД экскурсии, привязанные к ID пользователя в таблице избранного.
        """

        # ВАРИАНТ А: Если связь сделана через классическую промежуточную таблицу (Table)
        query = (
            select(Excursion)
            .join(user_favorite_excursions, Excursion.id == user_favorite_excursions.c.excursion_id)
            .where(user_favorite_excursions.c.user_id == user_id)
            .options(selectinload(Excursion.images))  # Ленивая загрузка картинок-превью
        )
        # Выполняем запрос через сессию, сохраненную в конструкторе (self.db или self.session)
        result = await db.execute(query)
        excursions = result.scalars().all()

        # БИЗНЕС-ПРАВИЛО: Так как это эндпоинт ИЗБРАННОГО,
        # мы принудительно проставляем флаг в True для каждой сущности.
        # Это гарантирует, что Pydantic-схема ExcursionShortRead отдаст "is_favorite": true на фронтенд.
        for excursion in excursions:
            excursion.is_favorite = True

        return excursions

    async def is_favorite(self, db: AsyncSession, user_id: int, excursion_id: int) -> bool:
        """Проверить, находится ли конкретная экскурсия в избранном у пользователя"""
        stmt = select(1).where(
            user_favorite_excursions.c.user_id == user_id,
            user_favorite_excursions.c.excursion_id == excursion_id
        )
        result = await db.execute(stmt)
        return result.scalar() is not None

excursion_repo = ExcursionRepository(Excursion)