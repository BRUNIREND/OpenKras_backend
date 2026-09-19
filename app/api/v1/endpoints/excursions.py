# app/api/v1/excursions.py
from http.client import HTTPException

from fastapi import APIRouter, Depends
from fastapi.params import Path
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from watchfiles import awatch

from app.api.v1.endpoints.admin import admin_router
from app.core.deps import get_excursion_service, get_current_admin, get_current_user
from app.database.session import get_db
from app.models import User, ExcursionMediaLink
from app.models.excursion import Excursion
from app.repositories.excursion import ExcursionRepository
from app.schemas.excursion import ExcursionRead, ExcursionCreate2, ExcursionShortRead, ExcursionDetailRead
from typing import List
from sqlalchemy.orm import selectinload

from app.schemas.media import LinkMediaRequest
from app.services.ExcursionService import ExcursionService

router = APIRouter(prefix="/excursions", tags=["Excursions"])

@router.get("/",
            response_model=List[ExcursionShortRead],
            summary="Запрос на получение всех экскурсий",
            description="Отправляет список всех доступных экскурсий"
        )
async def get_list_excursions(
        current_user: User = Depends(get_current_user),
        excursion_service: ExcursionService = Depends(get_excursion_service),
        skip: int = 0,
        limit: int = 100
) -> List[Excursion]:
    return await excursion_service.get_all_published(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{excursion_id}",
        summary="Запрос на получение конкретной экскурсии",
        description="Принимает ID экскурсии и отправляет полный список с данными",
    response_model=ExcursionDetailRead
)
async def get_excursion(
        excursion_id: int,
        current_user: User = Depends(get_current_user),
        excursion_service: ExcursionService = Depends(get_excursion_service)
) -> Excursion:
    """
    Возвращает полную информацию о конкретной экскурсии по id с проверкой на избранное
    """
    return await excursion_service.get_full_details(
        excursion_id=excursion_id,
        user_id=current_user.id
    )



@router.post(
        "/complete/{excursion_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Завершение прохождения экскурсии",
    description="Создает связь между текущим пользователем и экскурсией. Возвращает статус операции."
)
async def complete_excursion(
        excursion_id: int = Path(..., description="ID экскурсии, которую нужно добавить"),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        excursion_service: ExcursionService = Depends(get_excursion_service)
):
    success = await excursion_service.complete_excursion(
        user_id=current_user.id,
        excursion_id = excursion_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось добавить экскурсию в пройденное (возможно, она уже добавлена или не существует)"
        )
    return {"status": "success", "message": "Экскурсия добавлена в пройденные"}








