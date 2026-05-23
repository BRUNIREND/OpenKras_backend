from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Point
from app.repositories.base import CRUDBase
from app.schemas.point import PointCreate, PointUpdate


class PointRepository(CRUDBase[Point, PointCreate, PointUpdate]):
    async def get_by_excursion(self, db: AsyncSession, excursion_id: int) -> List[Point]:
        """Поиск экскурсии по точному названию"""
        query = select(self.model).where(self.model.excursion_id == excursion_id)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_points_with_audio(self, db: AsyncSession) -> List[Point]:
        """
        Возвращает только те точки, у которых загружен аудиогид.
        """
        query = select(self.model).where(self.model.audio_url.isnot(None))
        result = await db.execute(query)
        return result.scalars().all()

point_repo = PointRepository(Point)