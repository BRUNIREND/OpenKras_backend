from aiosmtplib import status
from fastapi import HTTPException
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.otp_repository import OTPRepository
from app.repositories.point import point_repo
from app.schemas.point import PointUpdate


class PointService:
    def __init__(self, db: AsyncSession, redis_client: Redis):
        self.db = db
        self.point_repo = point_repo
        self.cache_repo = OTPRepository(redis_client)

    async def update_point(self, point_id: int, data: PointUpdate):
        """Обновление точки администратором"""
        point = await self.point_repo.get_by_id(self.db, point_id)
        if not point:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Точка не найдена"
            )

        updated_point = await self.point_repo.update(self.db, db_obj=point, obj_in=data)

        await self.cache_repo.delete_excursion_cache(point.excursion_id)

        return updated_point

    async def delete_point(self, point_id: int):
        """Удаление точки администратором"""
        point = await self.point_repo.get_by_id(self.db, point_id)
        if not point:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Точка не найдена"
            )

        excursion_id = point.excursion_id

        await self.point_repo.delete(self.db, id=point_id)

        await self.cache_repo.delete_excursion_cache(excursion_id)

        return {"message": "Точка успешно удалена, кэш маршрута обновлен"}