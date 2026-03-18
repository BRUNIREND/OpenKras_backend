from fastapi import APIRouter, Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.models.point import Point  # SQLAlchemy модель
from app.schemas.point import PointRead
from typing import List
from sqlalchemy.orm import selectinload # Импортируем загрузчик

router = APIRouter(prefix="/points", tags=["Points"])

@router.get("/", response_model=List[PointRead])
async def get_points(
        db: AsyncSession = Depends(get_db),
        skip: int = 0,
        limit: int = 100
):
    # 1. Формируем запрос
    query = select(Point).offset(skip).limit(limit)
    # 2. Выполняем асинхронно
    result = await db.execute(query)

    # 3. Извлекаем объекты
    points = result.scalars().all()

    return points