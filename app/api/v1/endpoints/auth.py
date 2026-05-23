from fastapi import APIRouter, Depends

from starlette import status

from app.core.deps import get_auth_service
from app.schemas.auth import RegisterRequest,  RegisterVerify, LoginRequest
from app.services.AuthService import AuthService

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


# Отправляем запрос на регистрацию, генерируем OTP код
@auth_router.post(
    "/register/request",
    status_code=status.HTTP_200_OK,
    summary="Запрос на регистрацию пользователя",
    description="Принимает email пользователя, генерирует OTP и отправляет на почту."
)
async def request_otp(
        data: RegisterRequest,
        auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.request_otp(data.email)

# Получаем и сравнием код из прошлого этапа регистрации, создаем пользователя
@auth_router.post(
    "/register/verify",
    status_code=status.HTTP_200_OK,
    summary="Регистрация пользователя",
    description="Принимает данные пользователя, сохраняется в бд, проверяет корректность OTP кода"
)
async def verify_otp(
        data: RegisterVerify,
        auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.verify_and_register(data)

# Дефолтный вход
@auth_router.post("/login")
async def login(
        data: LoginRequest,
        auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.login_for_access_token(data)