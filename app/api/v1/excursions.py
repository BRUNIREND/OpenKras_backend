# app/api/v1/excursions.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.crud.excursion import get_excursions


router = APIRouter(prefix="/excursions", tags=["Экскурсии"])





@router.get("/")
async def list_excursions(db: AsyncSession = Depends(get_db)):
    excursions = await get_excursions(db)
    return [
        {
            "id": ex.id,
            "title": ex.title,
            "description": ex.description,
            "created_at": ex.created_at
        }
        for ex in excursions
    ]