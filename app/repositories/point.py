from typing import List

from sqlalchemy import select, insert, delete
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

    async def update_with_contents_and_media(self, db: AsyncSession, point_id: int, point_schema: PointCreate) -> Point:
        """
        Полное обновление точки, включая перезапись локализованного контента и медиа-ссылок.
        """
        # 1. Получаем существующую точку из базы
        stmt = select(Point).where(Point.id == point_id)
        result = await db.execute(stmt)
        db_point = result.scalar_one_or_none()
        if not db_point:
            return None

        # 2. Обновляем основные поля самой точки (координаты, радиус и т.д.)
        point_data = point_schema.model_dump(exclude={"contents", "excursion_id"})
        for key, value in point_data.items():
            setattr(db_point, key, value)
        db.add(db_point)

        # 3. Обновляем позицию (order) в таблице ассоциации экскурсии
        # Самый надежный способ — удалить старую связь и вставить актуальную
        await db.execute(
            delete(excursion_point_association).where(excursion_point_association.c.point_id == point_id)
        )
        stmt_assoc = insert(excursion_point_association).values(
            excursion_id=point_schema.excursion_id,
            point_id=point_id,
            order=point_schema.position
        )
        await db.execute(stmt_assoc)

        # 4. Перезаписываем языковой контент и медиа (Паттерн: Очистить старое -> Записать новое)
        # Получаем ID всех старых записей контента для этой точки
        old_contents_stmt = select(PointContent.id).where(PointContent.point_id == point_id)
        old_contents_res = await db.execute(old_contents_stmt)
        old_content_ids = old_contents_res.scalars().all()

        if old_content_ids:
            # Сначала удаляем старые связи с медиафайлами
            await db.execute(delete(PointMediaLink).where(PointMediaLink.point_content_id.in_(old_content_ids)))
            # Затем удаляем сами блоки текстового контента
            await db.execute(delete(PointContent).where(PointContent.point_id == point_id))

        # Накатываем новые данные из пришедшего payload
        for content_schema in point_schema.contents:
            content_data = content_schema.model_dump(exclude={"media_ids"})
            db_content = PointContent(point_id=point_id, **content_data)
            db.add(db_content)
            await db.flush()  # Получаем новый db_content.id

            for index, media_id in enumerate(content_schema.media_ids):
                media_link = PointMediaLink(
                    point_content_id=db_content.id,
                    media_id=media_id,
                    position=index + 1
                )
                db.add(media_link)

        # Фиксируем все изменения одной транзакцией
        await db.commit()

        # Возвращаем обновленный объект в полной сборке со связями для фронтенда
        final_stmt = (
            select(Point)
            .where(Point.id == point_id)
            .options(
                selectinload(Point.contents).selectinload(PointContent.media)
            )
        )
        final_result = await db.execute(final_stmt)
        return final_result.scalar_one()

    async def delete_point_completely(self, db: AsyncSession, point_id: int) -> bool:
        """
        Полное удаление точки и всех связанных с ней сущностей из промежуточных таблиц.
        """
        stmt = select(Point).where(Point.id == point_id)
        result = await db.execute(stmt)
        db_point = result.scalar_one_or_none()
        if not db_point:
            return False

        # Удаляем привязку к экскурсии
        await db.execute(delete(excursion_point_association).where(excursion_point_association.c.point_id == point_id))

        # Находим и зачищаем контент/медиа (на случай, если в СУБД не проставлен CASCADE ON DELETE)
        old_contents_stmt = select(PointContent.id).where(PointContent.point_id == point_id)
        old_contents_res = await db.execute(old_contents_stmt)
        old_content_ids = old_contents_res.scalars().all()

        if old_content_ids:
            await db.execute(delete(PointMediaLink).where(PointMediaLink.point_content_id.in_(old_content_ids)))
            await db.execute(delete(PointContent).where(PointContent.point_id == point_id))

        # Удаляем саму физическую точку
        await db.delete(db_point)
        await db.commit()
        return True
point_repo = PointRepository(Point)