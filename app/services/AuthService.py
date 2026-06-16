import os
import random

from dotenv import load_dotenv
from fastapi import HTTPException, status
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from app.core.config import settings
from app.core.otp_message import create_otp_html
from app.core.security import verify_password, create_access_token
from app.repositories.otp_repository import OTPRepository
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
    def __init__(self, db: AsyncSession, redis_client: Redis):
        self.db = db
        self.user_service = UserService(db)
        self.otp_repository = OTPRepository(redis_client)

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
        user = await user_repo.get_by_email(self.db, email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email уже занят"
            )

        otp_code = f"{random.randint(100000, 999999)}"

        await self.otp_repository.save_otp(
            email=email,
            code=otp_code,
            expire_seconds=settings.OTP_EXPIRE_SECONDS
        )

        # 4. Формируем и отправляем письмо
        message = MessageSchema(
            subject=f"{settings.project_name} - Код подтверждения",
            recipients=[email],
            body=create_otp_html(otp_code),
            subtype="html"
        )

        try:
            fm = FastMail(mail_conf)
            await fm.send_message(message)
        except Exception as e:
            # Если почта сломалась — подчищаем за собой созданный ключ в Redis
            await self.otp_repository.delete_otp(email)
            print(f"❌ Ошибка отправки почты: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось отправить письмо с кодом подтверждения"
            )

        return {"message": "OTP sent successfully", "debug_code": otp_code}

    async def verify_and_register(self, data: RegisterVerify):
        # 1. Запрашиваем код напрямую из оперативной памяти Redis
        saved_code = await self.otp_repository.get_otp(data.email)

        # 2. Если кода в Redis нет или он не совпадает
        if not saved_code or saved_code != data.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный код или срок его действия истек"
            )

        # 3. Код верный. Регистрируем нового пользователя в Postgres через UserService
        user_in = UserCreate(
            name=data.name,
            email=data.email,
            password=data.password,
        )
        new_user = await self.user_service.create_user(user_in)

        # 4. Сразу стираем код из Redis, так как он одноразовый
        await self.otp_repository.delete_otp(data.email)

        # 5. Генерируем JWT-токен для мгновенного логина
        token = create_access_token({"sub": str(new_user.id), "role": new_user.role})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": new_user.id
        }
