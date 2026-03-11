# app/database/session.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=False,               # True — если хочешь видеть все SQL-запросы в консоли
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Зависимость, которую будем использовать в эндпоинтах
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session