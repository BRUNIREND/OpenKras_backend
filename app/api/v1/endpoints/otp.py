from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.services.AuthService import AuthService
from pydantic import EmailStr, BaseModel

router = APIRouter()

class OTPRequest(BaseModel):
    email: EmailStr

@router.post("/request-otp")
async def request_otp(data: OTPRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    try:
        return await service.request_otp(data.email)
    except Exception as e:
        # Логируем ошибку отправки почты
        raise HTTPException(status_code=500, detail=f"Ошибка отправки почты: {str(e)}")