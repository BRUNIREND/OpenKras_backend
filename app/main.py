import asyncio

# app/main.py  — обнови полностью
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.session import engine
from app.models.base import Base          # ← ключевой импорт
from app.api.v1 import excursions        # даже если пустой — оставь

app = FastAPI(
    title="Аудио-гид Красноярского музея",
    version="0.1.0",
    docs_url="/docs",
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # потом сузишь
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Только для разработки! В продакшене используй alembic


async def init_db():
    async with engine.begin() as conn:
        # drop_all — только если хочешь полностью пересоздать таблицы при каждом запуске (для тестов)
        # await conn.run_sync(Base.metadata.drop_all)

        await conn.run_sync(Base.metadata.create_all)


# Запуск инициализации при старте приложения
@app.on_event("startup")
async def startup_event():
    await init_db()

app.include_router(excursions.router, prefix="/api/v1")