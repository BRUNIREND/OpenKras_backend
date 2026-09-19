from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_category_service, get_current_admin
from app.database.session import get_db
from app.models import User
from app.schemas.category import CategoryRead, CategoryCreate
from app.services import CategoryService

router = APIRouter(prefix="/category", tags=["Categories"])

@router.get("/", response_model=List[CategoryRead])
async def get_list_categories(
        category_service: CategoryService = Depends(get_category_service),
        current_admin: User = Depends(get_current_admin)
) -> List[CategoryRead]:
    return await category_service.get_list()





