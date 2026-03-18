# app/api/v1/excursions.py
from http.client import HTTPException

from alembic.util import status
from fastapi import APIRouter, Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.models.excursion import Excursion  # SQLAlchemy модель
from app.schemas.excursion import ExcursionRead
from typing import List
from sqlalchemy.orm import selectinload # Импортируем загрузчик

router = APIRouter(prefix="/excursions", tags=["Excursions"])

@router.get("/", response_model=List[ExcursionRead])
async def get_excursions(
        db: AsyncSession = Depends(get_db),
        skip: int = 0,
        limit: int = 100
):
    # 1. Формируем запрос
    query = select(Excursion).options(selectinload(Excursion.points)).offset(skip).limit(limit)
    # 2. Выполняем асинхронно
    result = await db.execute(query)

    # 3. Извлекаем объекты
    excursions = result.scalars().all()

    return excursions


@router.get("/{excursion_id}", response_model=ExcursionRead)
async def get_excursion(excursion_id: int, db: AsyncSession = Depends(get_db)):
    query = (
        select(Excursion)
        .options(selectinload(Excursion.points))
        .where(Excursion.id == excursion_id)
    )
    result = await db.execute(query)
    excursion = result.scalar_one_or_none()

    if not excursion:
        raise HTTPException("404 not found blat")
    return excursion