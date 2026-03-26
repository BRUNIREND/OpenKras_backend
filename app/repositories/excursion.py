import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Excursion


class ExcursionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_title(self, title: str):
        result = await self.db.execute(select(Excursion).where(Excursion.title == title))
        return result.scalar_one_or_none()

    async def create(self, obj_in_data):
        db_obj = Excursion(**obj_in_data)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

