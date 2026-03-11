from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.point import Point


async def get_points(db: AsyncSession):
    stmt = select(Point).order_by(Point.id.desc())
    result = await db.execute(stmt)
    return result.scalars().all()