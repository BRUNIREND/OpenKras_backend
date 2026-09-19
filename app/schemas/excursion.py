from pydantic import ConfigDict, BaseModel
from typing import Optional

from sqlalchemy import Boolean

from .media import MediaRead
from .point import PointRead, PointCreate
from ..models.excursion import ExcursionStatus


class ExcursionBase(BaseModel):
    title: str
    description: Optional[str] = None


class ExcursionRead(ExcursionBase):
    id: int
    description: str | None = None
    status: ExcursionStatus = ExcursionStatus.DRAFT
    is_favorite: bool = False
    images: list[MediaRead]
    category_id: int
    points: list[PointRead]
    distance: Optional[float]
    duration: Optional[int]
    model_config = ConfigDict(from_attributes=True)


#Короткий вывод экскурсий для конкретного пользователя
class ExcursionShortRead(BaseModel):
    id: int
    title: str
    category_id: Optional[int] = None
    is_favorite: bool = False
    status: ExcursionStatus = ExcursionStatus.DRAFT
    distance: Optional[float] = None
    duration: Optional[int] = None
    is_completed: bool = False
    images: list[MediaRead]
    model_config = ConfigDict(from_attributes=True)

#Длинный  вывод экскурсий для конкретного пользователя
class ExcursionDetailRead(ExcursionShortRead):
    description: Optional[str] = None
    images: list[MediaRead] = []
    points: list[PointRead] = []


class ExcursionCreate2(ExcursionBase):
    points: list[PointCreate] = []
    model_config = ConfigDict(from_attributes=True)

class ExcursionResponse(BaseModel):
    id: int
    category_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    distance: Optional[float] = None
    duration: Optional[int] = None

class ExcursionCreate(BaseModel):
    category_id: Optional[int] = None
    title: str
    description: Optional[str] = None

class ExcursionUpdate(ExcursionResponse):
    # id: int
    # points: list[PointCreate] = []
    model_config = ConfigDict(from_attributes=True)

