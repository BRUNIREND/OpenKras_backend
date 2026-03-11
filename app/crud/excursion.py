# app/crud/excursions.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.excursion import Excursion

async def get_excursions(db: AsyncSession):
    stmt = select(Excursion).order_by(Excursion.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()