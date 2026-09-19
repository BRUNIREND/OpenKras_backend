from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Boolean


# 1. Запрос на регистрацию (Шаг 1)
class RegisterRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        description="Электронная почта пользователя для отправки OTP",
        examples=["example@ex.com"]
    )

# 2. Подтверждение регистрации (Шаг 2)
class RegisterVerify(BaseModel):

    email: EmailStr = Field(
        ...,
        description="Электронная почта пользователя для отправки OTP",
        examples=["example@ex.com"]
    )
    name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Имя пользователя",
        examples=["Ivan"]
    )
    # username: str = Field(
    #     ...,
    #     min_length=3,
    #     max_length=30,
    #     description="Уникальный никнейм (ID пользователя)",
    #     examples=["yaro_museum"]
    # )
    password: str = Field(
        ...,
        min_length=6,
        description="Пароль для аккаунта",
        examples=["Super_secret_pass123"]
    )
    code: str = Field(
        ...,
        min_length=6,
        description="OTP код",
        examples=["123456"]
    )



# 3. Вход по паролю (Логин)
class LoginRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        description="Электронная почта пользователя для отправки OTP",
        examples=["yaroslav.losev.2014@mail.ru"]
    )
    password: str = Field(
        ...,
        min_length=6,
        description="Пароль для аккаунта",
        examples=["Abcd26837"]
    )

# 4. Ответ с токенами
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int

class IsUserRegistred(BaseModel):
    email: EmailStr
class IsUserRegistredResponse(BaseModel):
    registred: bool