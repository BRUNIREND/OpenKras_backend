from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.user_otp import UserOTP
from datetime import datetime


class AuthRepository:
    async def save_otp(self, db: AsyncSession, email: str, code: str, expireAt):
        # Удаляем старые коды пользователя перед созданием нового
        await db.execute(delete(UserOTP).where(UserOTP.email == email))

        db_otp = UserOTP(email=email,
                         code=code,
                         expires_at=expireAt)
        db.add(db_otp)
        await db.commit()

    async def get_otp_by_email(self, db: AsyncSession, email: str):
        result = await db.execute(
            select(UserOTP).where(UserOTP.email == email)
        )
        return result.scalars().first()

    async def delete_otp(self, db: AsyncSession, email: str):
        await db.execute(delete(UserOTP).where(UserOTP.email == email))
        await db.commit()



auth_repo = AuthRepository()