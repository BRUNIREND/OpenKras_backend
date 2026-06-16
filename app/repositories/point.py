from typing import List

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Point, PointContent, PointMediaLink
from app.models.assocations import excursion_point_association
from app.repositories.base import CRUDBase
from app.schemas.point import PointCreate, PointUpdate, PointContentRead


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

    async def create_with_contents_and_media(self, db: AsyncSession, point_schema: PointCreate) -> Point:
        # 1. Создаем и сохраняем саму точку (координаты, радиус)
        point_data = point_schema.model_dump(exclude={"contents", "excursion_id"})
        db_point = Point(**point_data)
        db.add(db_point)
        await db.flush() # Получаем db_point.id без фиксации транзакции
        stmt = insert(excursion_point_association).values(
            excursion_id=point_schema.excursion_id,
            point_id=db_point.id,
            order=point_schema.position  # Твое поле называется order
        )
        await db.execute(stmt)
        # 2. Проходим по языковым версиям контента
        for content_schema in point_schema.contents:
            content_data = content_schema.model_dump(exclude={"media_ids"})
            db_content = PointContent(point_id=db_point.id, **content_data)
            db.add(db_content)
            await db.flush() # Получаем db_content.id

            # 3. Привязываем существующие ID медиа к этому контенту
            for index, media_id in enumerate(content_schema.media_ids):
                media_link = PointMediaLink(
                    point_content_id=db_content.id,
                    media_id=media_id,
                    position=index + 1 # Сохраняем порядковый номер
                )
                db.add(media_link)

        # Фиксируем транзакцию — все три таблицы запишутся одновременно
        await db.commit()

        # Возвращаем собранную точку с подгруженными связями для ответа фронтенду
        stmt = (
            select(Point)
            .where(Point.id == db_point.id)
            .options(
                selectinload(Point.contents).selectinload(PointContent.media)
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one()
point_repo = PointRepository(Point)