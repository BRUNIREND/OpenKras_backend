from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.models import Excursion, Point
from app.models.excursion import ExcursionStatus
from app.repositories.category import category_repo
from app.repositories.excursion import  excursion_repo
from fastapi import HTTPException

from app.repositories.point import point_repo
from app.schemas.excursion import ExcursionCreate, ExcursionUpdate
from app.schemas.point import PointCreate


class ExcursionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_excursion(self, excursion_in: ExcursionCreate) -> Excursion:
        """
        Создание экскурсии с проверкой существования категории.
        """
        # 1. Проверяем, существует ли указанная категория
        category = await category_repo.get(self.db, id=excursion_in.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Категория с id {excursion_in.category_id} не найдена"
            )

        # 2. Проверяем уникальность названия (бизнес-логика)
        existing = await excursion_repo.get_by_title(self.db, title=excursion_in.title)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Экскурсия с таким названием уже существует"
            )

        # 3. Сохраняем через репозиторий
        return await excursion_repo.create(self.db, obj_in=excursion_in)

    async def get_all_published(self, user_id: int,skip: int = 0, limit: int = 20) -> List[Excursion]:
        """
        Получение списка только опубликованных экскурсий для мобильного приложения.
        """
        return await excursion_repo.get_published_short(self.db, current_user_id=user_id, skip=skip, limit=limit)

    async def get_full_details(self, excursion_id: int, user_id: int) -> Excursion:
        """
        Получение полной информации: Экскурсия + Точки + Медиа + Статус избранного.
        Это основной метод для экрана подробностей в приложении.
        """
        # 1. Используем метод с полной подгрузкой вложенных связей
        excursion = await excursion_repo.get_with_points_one(self.db, excursion_id)
        if not excursion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Экскурсия не найдена"
            )

        # 2. Проверяем, добавил ли этот пользователь её в избранное
        excursion.is_favorite = await excursion_repo.is_favorite(
            db=self.db,
            user_id=user_id,
            excursion_id=excursion_id
        )

        return excursion


    async def get_all_detail_excursion_by_id(self, excursion_id: int ):
        excursion = await excursion_repo.get_with_points_one(self.db, excursion_id)
        if not excursion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Экскурсия не найдена"
            )
        return excursion

    async def add_point_to_excursion(self, point_data: PointCreate) -> Point:
        """
        Бизнес-логика привязки новой точки с мультиязычным контентом
        и медиа-файлами к экскурсии.
        """
        excursion_exists = await excursion_repo.exists(self.db, id=point_data.excursion_id)
        if not excursion_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Экскурсия с ID {point_data.excursion_id} не найдена."
            )

        try:
            new_point = await point_repo.create_with_contents_and_media(
                db=self.db,
                point_schema=point_data
            )
            return new_point

        except Exception as e:

            await self.db.rollback()


            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось сохранить точку маршрута и связать её с медиа-файлами."
            )

    async def update_point_in_excursion(self, point_id: int, point_data: PointCreate) -> Point:
        """
        Бизнес-логика обновления параметров точки, её мультиязычного контента и медиа.
        """
        # Проверяем, существует ли целевая экскурсия
        excursion_exists = await excursion_repo.exists(self.db, id=point_data.excursion_id)
        if not excursion_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Экскурсия с ID {point_data.excursion_id} не найдена."
            )

        try:
            updated_point = await point_repo.update_with_contents_and_media(
                db=self.db,
                point_id=point_id,
                point_schema=point_data
            )
            if not updated_point:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Точка маршрута с ID {point_id} не найдена."
                )
            return updated_point

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось обновить точку маршрута и перезаписать её медиа-структуру."
            )

    async def delete_point_from_excursion(self, point_id: int):
        """
        Бизнес-логика полного удаления точки.
        """
        try:
            success = await point_repo.delete_point_completely(self.db, point_id=point_id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Точка с ID {point_id} не найдена."
                )
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка сервера при попытке удалить точку маршрута."
            )

    async def delete_excursion(self, excursion_id: int):
        """
        Удаление экскурсии. Благодаря cascade="all, delete-orphan" в моделях,
        все связанные точки и записи в медиа удалятся автоматически.
        """
        excursion = await excursion_repo.get(self.db, id=excursion_id)
        if not excursion:
            raise HTTPException(status_code=404, detail="Экскурсия не найдена")

        return await excursion_repo.remove(self.db, id=excursion_id)

    async def publish_excursion(self, excursion_id: int) -> Excursion:
        """
        Перевод экскурсии из статуса DRAFT в PUBLISHED для публикации в приложении.
        """
        excursion = await excursion_repo.get(self.db, id=excursion_id)
        if not excursion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Экскурсия не найдена"
            )

        # Меняем статус
        excursion.status = ExcursionStatus.PUBLISHED

        await self.db.commit()
        await self.db.refresh(excursion)
        return excursion

    async def get_all_for_admin(self, skip: int = 0, limit: int = 20) -> List[Excursion]:
        """

        Получение ВСЕХ экскурсий (включая DRAFT) для админ-панели.
        """
        # Если в репозитории есть базовый метод get_multi, используем его,
        # либо пишем кастомный метод в репозитории без фильтрации по статусу

        return await excursion_repo.get_all_raw(self.db, skip=skip, limit=limit)

    async def update_excursion(self, excursion_id: int, excursion_in: ExcursionUpdate) -> Excursion:
        # Вызываем метод обновления у репозитория
        updated_excursion = await excursion_repo.update(
            self.db,
            excursion_id=excursion_id,
            obj_in=excursion_in
        )

        # Если репозиторий вернул None, значит такой записи нет в базе
        if not updated_excursion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Экскурсия с ID {excursion_id} не найдена"
            )

        return updated_excursion

    async def add_to_favorites(self, user_id: int, excursion_id: int) -> bool:
        """Бизнес-логика добавления в избранное"""
        # 1. Проверяем, существует ли вообще такая экскурсия, прежде чем плодить связи
        excursion_exists = await excursion_repo.get(self.db, id=excursion_id)
        if not excursion_exists:
            return False

        # 2. Перенаправляем запрос в репозиторий для выполнения записи в БД
        return await excursion_repo.add_to_favorites(
            db=self.db,
            user_id=user_id,
            excursion_id=excursion_id
        )

    async def complete_excursion(self, user_id: int, excursion_id: int) -> bool:

        excursion_exists = await excursion_repo.get(self.db, id=excursion_id)
        if not excursion_exists:
            return False

        # 2. Перенаправляем запрос в репозиторий для выполнения записи в БД
        return await excursion_repo.add_to_completed_excursion(
            db=self.db,
            user_id=user_id,
            excursion_id=excursion_id
        )


    async def remove_from_favorites(self, user_id: int, excursion_id: int) -> bool:
        """Бизнес-логика удаления из избранного"""
        # Репозиторий просто удалит запись из таблицы user_favorite_excursions
        return await excursion_repo.remove_from_favorites(
            db=self.db,
            user_id=user_id,
            excursion_id=excursion_id
        )

    async def get_user_favorites(self, user_id) -> List[Excursion]:
        """
            Получить список облегченных экскурсий,
            добавленных пользователем в избранное.
        """
        return await excursion_repo.get_user_favorites(
            db=self.db,
            user_id=user_id
        )