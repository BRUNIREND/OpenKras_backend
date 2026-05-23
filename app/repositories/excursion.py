import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Excursion, Point, PointContent
from app.repositories.base import CRUDBase
from app.schemas.excursion import ExcursionCreate, ExcursionUpdate
from sqlalchemy.orm import selectinload


class ExcursionRepository(CRUDBase[Excursion, ExcursionCreate, ExcursionUpdate]):

    async def get_by_title(self, db: AsyncSession, title: str):
        """Поиск экскурсии по точному названию"""
        result = await db.execute(select(Excursion).where(Excursion.title == title))
        return result.scalar_one_or_none()

    async def get_with_points(self, db: AsyncSession, id: int):
        """Получить экскурсию и сразу загрузить все её точки."""
        query = select(self.model).options(selectinload(self.model.points)).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_all_with_points(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Excursion]:
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
        return result.scalars().all()

excursion_repo = ExcursionRepository(Excursion)