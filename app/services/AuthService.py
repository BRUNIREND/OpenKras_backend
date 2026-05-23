import os
import random
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from app.core.otp_message import create_otp_html
from app.core.security import verify_password, create_access_token
from app.repositories.auth_repository import auth_repo
from app.repositories.user import user_repo
from app.schemas.auth import RegisterVerify, LoginRequest
from app.schemas.user import UserCreate
from app.services.UserService import UserService

load_dotenv()
mail_conf = ConnectionConfig(
    # Используем "or", чтобы Pydantic не видел None
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME"),
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True
)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_service = UserService(db)

    async def authenticate_user(self, email: str, password: str):
        user = await user_repo.get_by_email(self.db, email=email)

        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )
        return user

    async def login_for_access_token(self, data: LoginRequest):
        user = await self.authenticate_user(data.email, data.password)
        access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }

    async def request_otp(self, email: str):
        # 1. Проверка на существование юзера
        user = await user_repo.get_by_email(self.db, email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email уже занят"
            )

        expiratAt = datetime.utcnow() + timedelta(minutes=5)
        otp_code = f"{random.randint(100000, 999999)}"
        await auth_repo.save_otp(self.db, email, otp_code, expiratAt)

        # 3. Отправка письма
        message = MessageSchema(
            subject="Открой Красноярск - Код подтверждения",
            recipients=[email],
            body=create_otp_html(otp_code),
            subtype="html"
        )

        try:
            fm = FastMail(mail_conf)
            await fm.send_message(message)
        except Exception as e:
            print(f"Ошибка почты: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось отправить письмо"
            )

        return {"message": "OTP sent successfully"}

    async def verify_and_register(self, data: RegisterVerify):
        # 1. Получаем код из БД
        db_otp = await auth_repo.get_otp_by_email(self.db, data.email)

        if not db_otp or db_otp.code != data.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный код"
            )

        # 2. Проверка времени жизни (utcnow)
        if datetime.utcnow() > db_otp.expires_at:
            await auth_repo.delete_otp(self.db, data.email)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Код просрочен"
            )

        # 3. Создаем пользователя через UserService
        user_in = UserCreate(
            name=data.name,
            email=data.email,
            password=data.password,
        )
        new_user = await self.user_service.create_user(user_in)

        # 4. Удаляем использованный код
        await auth_repo.delete_otp(self.db, data.email)

        # 5. Генерируем токен для мгновенного входа после регистрации
        token = create_access_token({"sub": str(new_user.id), "role": new_user.role})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": new_user.id
        }
