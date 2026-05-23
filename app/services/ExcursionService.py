from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.models import Excursion
from app.repositories.category import category_repo
from app.repositories.excursion import ExcursionRepository, excursion_repo
from fastapi import HTTPException

from app.repositories.point import point_repo
from app.schemas.excursion import ExcursionCreate
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

    async def get_all_published(self, skip: int = 0, limit: int = 20) -> List[Excursion]:
        """
        Получение списка только опубликованных экскурсий для мобильного приложения.
        """
        return await excursion_repo.get_all_with_points(self.db, skip=skip, limit=limit)

    async def get_full_details(self, excursion_id: int) -> Excursion:
        """
        Получение полной информации: Экскурсия + Точки + Медиа.
        Это основной метод для экрана подробностей в приложении.
        """
        excursion = await excursion_repo.get_with_points(self.db, id=excursion_id)
        if not excursion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Экскурсия не найдена"
            )
        return excursion

    async def add_new(self, data: ExcursionCreate) -> Excursion:
        """
        Добавление новой экскурсии
        """
        existing_excursion = await excursion_repo.get_by_title(self.db ,data.title)
        if existing_excursion:
            raise HTTPException(400, "Такая экскурсия уже есть")

        return await excursion_repo.create(self.db, obj_in=data)

    async def add_point_to_excursion(self, point_in: PointCreate):
        # Здесь мы просто сохраняем пути, которые прислал фронтенд
        # (Фронтенд сначала загружает файл на другой эндпоинт, получает ссылку и шлет её сюда)

        excursion = await excursion_repo.get(self.db, id=point_in.excursion_id)
        if not excursion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Нельзя добавить точку к несуществующей экскурсии"
            )
        return await point_repo.create(self.db, obj_in=point_in)

    async def delete_excursion(self, excursion_id: int):
        """
        Удаление экскурсии. Благодаря cascade="all, delete-orphan" в моделях,
        все связанные точки и записи в медиа удалятся автоматически.
        """
        excursion = await excursion_repo.get(self.db, id=excursion_id)
        if not excursion:
            raise HTTPException(status_code=404, detail="Экскурсия не найдена")

        return await excursion_repo.remove(self.db, id=excursion_id)