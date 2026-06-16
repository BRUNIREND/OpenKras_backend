import os
from typing import List

from fastapi import APIRouter, Depends, status, UploadFile, HTTPException
from fastapi.params import File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models import User, Media, ExcursionMediaLink
from app.models.excursion import Excursion, ExcursionStatus
from app.models.media import MediaType
from app.schemas.excursion import ExcursionResponse, ExcursionCreate, ExcursionRead
from app.core.deps import get_current_admin, get_excursion_service
from app.schemas.media import LinkMediaRequest
from app.schemas.point import PointCreate
from app.services.ExcursionService import ExcursionService
from app.services.FileService import FileService

admin_router = APIRouter(prefix="/admin", tags=["Admin Panel"])

@admin_router.post("/excursions/create", response_model=ExcursionResponse)
async def create_excursion(
    payload: ExcursionCreate,
    excursion_service: ExcursionService = Depends(get_excursion_service),
    current_admin: User = Depends(get_current_admin)
) -> Excursion:

    return await excursion_service.create_excursion(payload)

@admin_router.get("/excursions/{excursion_id}", response_model=ExcursionRead)
async def get_excursion_by_id(
        excursion_id: int,
        service: ExcursionService = Depends(get_excursion_service),
        current_admin: User = Depends(get_current_admin)
):
    data = await service.get_all_detail_excursion_by_id(excursion_id)
    return data

@admin_router.get("/excursions", response_model=List[ExcursionRead])
async def get_admin_excursions(
    skip: int = 0,
    limit: int = 20,
    service: ExcursionService = Depends(get_excursion_service),
    current_admin: User = Depends(get_current_admin)
):
    data = await service.get_all_for_admin(skip=skip, limit=limit)
    return data

@admin_router.post("/media", status_code=status.HTTP_201_CREATED)
async def upload_media(
        media_type: MediaType = Form(...),
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    folder_name = "audio" if media_type == MediaType.AUDIO else "images"

    file_url = await FileService.save_file(file=file, folder=folder_name)

    new_media = Media(
        file_url=file_url,
        media_type=media_type
    )
    db.add(new_media)
    await db.commit()
    await db.refresh(new_media)

    return {
        "id": new_media.id,
        "file_url": new_media.file_url,
        "media_type": new_media.media_type
    }


@admin_router.delete("/media/{media_id}")
async def delete_media(
        media_id: int,
        db: AsyncSession = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    # 1. Ищем медиафайл в БД
    data = await db.execute(select(Media).where(Media.id == media_id))
    media_item = data.scalar_one_or_none()
    if not media_item:
        raise HTTPException(status_code=404, detail="Медиафайл не найден")


    object_name = os.path.basename(media_item.file_url)

    if media_item.media_type == MediaType.AUDIO:
        await FileService.delete_file(
            "museum-media",
                        "audio/" + object_name)
    else:
        await FileService.delete_file(
            "museum-media",
            "images/" + object_name)
    await db.delete(media_item)
    await db.commit()

    return {"status": "success", "message": "Файл успешно удален"}




@admin_router.post("/excursions/points", status_code=status.HTTP_201_CREATED)
async def add_point_to_excursion(
    payload: PointCreate,
    service: ExcursionService = Depends(get_excursion_service),
    current_admin: User = Depends(get_current_admin)
):
    # Передаем Pydantic-схему напрямую в сервис, как он и ожидает
    return await service.add_point_to_excursion(payload)


@admin_router.delete("/excursions/{excursion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_excursion(
    excursion_id: int,
    service: ExcursionService = Depends(get_excursion_service),
    current_admin: User = Depends(get_current_admin)
):
    await service.delete_excursion(excursion_id=excursion_id)
    return None


@admin_router.post("/excursions/{excursion_id}/media")
async def link_media_to_excursion(
    excursion_id: int,
    payload: LinkMediaRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    # Создаем запись в таблице ассоциации
    link = ExcursionMediaLink(
        excursion_id=excursion_id,
        media_id=payload.media_id,
        position=payload.position
    )
    db.add(link)
    await db.commit()
    return {"status": "success", "message": "Медиа успешно привязано к экскурсии"}


@admin_router.put("/excursions/{excursion_id}/publish", response_model=ExcursionResponse)
async def publish_excursion(
    excursion_id: int,
    service: ExcursionService = Depends(get_excursion_service),
    current_admin: User = Depends(get_current_admin)
):
    return await service.publish_excursion(excursion_id=excursion_id)

@admin_router.put("/excursions/{excursion_id}", response_model=ExcursionResponse)
async def update_excursion(
    excursion_id: int,
    payload: ExcursionCreate, # или создай отдельную схему ExcursionUpdate
    service: ExcursionService = Depends(get_excursion_service),
    current_admin: User = Depends(get_current_admin)
):
    # Метод в сервисе должен обновить поля title, description, category_id
    return await service.update_excursion(excursion_id=excursion_id, excursion_in=payload)