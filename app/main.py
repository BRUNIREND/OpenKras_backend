# app/main.py  — обнови полностью
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.models import APIKeyIn
from fastapi.security import APIKeyHeader
from starlette.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi

from app.core.redis import redis_pool
from app.database.session import engine
from app.database.base_class import Base
from app.api.v1.endpoints import excursions, points, users, auth, category, otp, admin
from app.services.FileService import FileService

# print(f"DEBUG: Point columns: {Point.__table__.columns.keys()}")

prefix = "/api/v1"
app = FastAPI(
    title="Аудио-гид Красноярского музея",
    version="0.1.0",
    docs_url="/docs",
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# origins = [
#     "http://localhost:5173",
#     "http://127.0.0.1:5173",
# ]
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )





async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Запуск инициализации при старте приложения
@app.on_event("startup")
async def startup_event():
    await init_db()
    try:
        # Вызываем асинхронный метод инициализации бакета
        await FileService.init_bucket()
    except Exception as e:
        print(f"❌ Не удалось инициализировать права бакета MinIO: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    # При остановке сервера красиво закрываем пул Redis
    print("💤 Закрытие соединений Redis...")
    await redis_pool.disconnect()

app.include_router(excursions.router, prefix=prefix)
app.include_router(points.router, prefix=prefix)
app.include_router(users.user_router, prefix=prefix)
app.include_router(auth.auth_router, prefix=prefix)
app.include_router(category.router, prefix=prefix)
app.include_router(otp.router, prefix=prefix)
app.include_router(admin.admin_router, prefix=prefix)
