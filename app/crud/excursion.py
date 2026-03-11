# app/crud/excursions.py
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.excursion import Excursion

async def get_excursions(db: AsyncSession, excursion_id: int):
    query = select(Excursion).options(
        selectinload(Excursion.points)
    ).where(Excursion.id == excursion_id)

    result = await db.execute(query)
    return result.scalars().first()