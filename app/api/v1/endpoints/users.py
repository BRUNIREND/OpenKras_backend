from fastapi import APIRouter, Depends, HTTPException, status, Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_excursion_service
from app.database.session import get_db
from app.models.user import User
from app.schemas.excursion import  ExcursionShortRead
from app.schemas.user import  UserResponse
from typing import List

from app.services.ExcursionService import ExcursionService

user_router = APIRouter(prefix="/users", tags=["User"])


@user_router.post(
    "/me/favorites/{excursion_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Добавить экскурсию в избранное",
    description="Создает связь между текущим пользователем и экскурсией. Возвращает статус операции."
)
async def add_favorite(
        excursion_id: int = Path(..., description="ID экскурсии, которую нужно добавить"),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        excursion_service: ExcursionService = Depends(get_excursion_service)
):
    print(f"{excursion_id}: EXcursion id")
    success = await excursion_service.add_to_favorites(
        user_id=current_user.id,
        excursion_id=excursion_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось добавить экскурсию в избранное (возможно, она уже добавлена или не существует)"
        )

    return {"status": "success", "message": "Экскурсия добавлена в избранное"}


@user_router.delete(
    "/me/favorites/{excursion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить экскурсию из избранного",
    description="Удаляет связь между текущим пользователем и экскурсией. Ничего не возвращает в случае успеха."
)
async def remove_favorite(
        excursion_id: int = Path(..., description="ID экскурсии, которую нужно удалить"),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        excursion_service: ExcursionService = Depends(get_excursion_service)
):
    success = await excursion_service.remove_from_favorites(
        user_id=current_user.id,
        excursion_id=excursion_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось удалить экскурсию из избранного"
        )

    return


@user_router.get(
    "/me/favorites",
    summary="Получить список избранных экскурсий пользователя",
    description="Возвращает облегченный список экскурсий, добавленных в избранное (без тяжелых точек)",
    response_model=List[ExcursionShortRead]  # Защищаем сеть от перегрузок
)
async def get_favorite_excursions(
        current_user: User = Depends(get_current_user),
        excursion_service: ExcursionService = Depends(get_excursion_service)
):
    # Вызываем метод получения избранного из ExcursionService
    excursion = await excursion_service.get_user_favorites(
        user_id=current_user.id
    )

    return excursion

@user_router.get(
    "/me",
    response_model=UserResponse,
    summary="Получить профиль текущего пользователя",
    description="Возвращает данные авторизованного пользователя на основе JWT-токена."
)
async def read_user_me(
    current_user: User = Depends(get_current_user)
):
    return current_user


