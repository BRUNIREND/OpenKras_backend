from pydantic import BaseModel, EmailStr, ConfigDict
from app.models.user import UserRole

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole = UserRole.USER

class UserCreate(UserBase):
    password: str  # Только для создания

class UserRead(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(UserBase):
    id: int
    name: str | None = None
    email: EmailStr | None = None

    model_config = ConfigDict(from_attributes=True)

class FavoriteUpdate(BaseModel):
    excursion_id: int

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)