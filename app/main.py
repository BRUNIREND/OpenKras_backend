# app/main.py  — обнови полностью
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from unicodedata import category

from app.api.v1.endpoints.auth import auth_router
from app.database.session import engine
from app.database.base_class import Base          # ← ключевой импорт
from app.api.v1.endpoints import excursions, points, users, auth, category, otp
from app.models.point import Point

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



# Создаем папки, если их нет
os.makedirs("static/images", exist_ok=True)
os.makedirs("static/audio", exist_ok=True)

# Монтируем папку static по адресу /static
app.mount("/static", StaticFiles(directory="static"), name="static")

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Запуск инициализации при старте приложения
@app.on_event("startup")
async def startup_event():
    await init_db()

app.include_router(excursions.router, prefix=prefix)
app.include_router(points.router, prefix=prefix)
app.include_router(users.user_router, prefix=prefix)
app.include_router(auth.auth_router, prefix=prefix)
app.include_router(category.router, prefix=prefix)
app.include_router(otp.router, prefix=prefix)