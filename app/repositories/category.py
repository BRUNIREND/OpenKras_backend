from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import CRUDBase
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryBase

class CategoryRepository(CRUDBase[Category, CategoryCreate, CategoryBase]):
    async def get_all(self, db: AsyncSession):
        result = await db.execute(select(Category).order_by(Category.id))

        return result.scalars().all()

category_repo = CategoryRepository(Category)