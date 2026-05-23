# app/api/v1/excursions.py
from http.client import HTTPException

from fastapi import APIRouter, Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from watchfiles import awatch

from app.core.deps import get_excursion_service
from app.database.session import get_db
from app.models.excursion import Excursion
from app.repositories.excursion import ExcursionRepository
from app.schemas.excursion import ExcursionRead, ExcursionCreate
from typing import List
from sqlalchemy.orm import selectinload

from app.services.ExcursionService import ExcursionService

router = APIRouter(prefix="/excursions", tags=["Excursions"])

@router.get("/", response_model=List[ExcursionRead])
async def get_list_excursions(
        excursion_service: ExcursionService = Depends(get_excursion_service),
        skip: int = 0,
        limit: int = 100
) -> List[Excursion]:
    return await excursion_service.get_all_published(skip, limit)





@router.get("/{excursion_id}", response_model=ExcursionRead)
async def get_excursion(
        excursion_id: int,
        excursion_service: ExcursionService = Depends(get_excursion_service)
) -> Excursion:
    """
    Возвращает полную информацию о конкретной экскурсии по id
    :param excursion_id:
    :param excursion_service:
    :return: Excursion
    """
    return await excursion_service.get_full_details(excursion_id = excursion_id)

@router.post("/create", response_model=ExcursionCreate)
async def create_excursion(
        data: ExcursionCreate,
        excursion_service: ExcursionService = Depends(get_excursion_service)
):
    return await excursion_service.create_excursion(data)


