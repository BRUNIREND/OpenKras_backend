from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.category import category_repo


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(self):
        return await(category_repo.get_all(self.db))