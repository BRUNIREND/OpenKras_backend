from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from watchfiles import awatch

from app.models import Category
from app.repositories.category import category_repo
from app.schemas.category import CategoryCreate, CategoryDelete, CategoryRead


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(self):
        return await(category_repo.get_all(self.db))

    async def create(self, category_in: CategoryCreate) -> CategoryRead:
        existing = await self._get_by_name(category_in.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Категория с таким названием уже существует"
            )
        db_category = await category_repo.create(self.db, obj_in=category_in)
        return CategoryRead.model_validate(db_category)

    async def delete(self, category_id: int) -> None:
        deleted = await category_repo.remove(self.db, id=category_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена"
            )

    async def _get_by_name(self, name: str) -> Optional[Category]:
        """Приватный метод для поиска категории по имени """
        result = await self.db.execute(
            select(Category).where(Category.name == name)
        )
        return result.scalar_one_or_none()
