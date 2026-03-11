from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.excursions import router
from app.database.session import get_db
from app.crud.points import get_points


@router.get("/points")
async def list_points(db: AsyncSession = Depends(get_db)):
    points = await get_points(db)
    return [
        {
            "id": point.id,
            "excursion_id": point.excursion_id,
            "title": point.title,
            "text": point.text,
            "address": point.address,
            "latitude": point.latitude,
            "longitude": point.longitude,
            "audio_url": point.audio_url,
            "image_url": point.image_url,
            "radius_meters": point.radius_meters,
        }
        for point in points
    ]