from typing import List

from fastapi import APIRouter, Depends

from app.core.deps import  get_category_service
from app.schemas.category import CategoryRead
from app.services import CategoryService

router = APIRouter(prefix="/category", tags=["Categories"])

@router.get("/", response_model=List[CategoryRead])
async def get_list_categories(
        category_service: CategoryService = Depends(get_category_service),
) -> List[CategoryRead]:
    return await category_service.get_list()