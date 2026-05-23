from pydantic import ConfigDict, BaseModel
from typing import Optional

from sqlalchemy import Boolean

from .media import MediaRead
from .point import PointRead, PointCreate

class ExcursionBase(BaseModel):
    title: str
    description: Optional[str] = None

class ExcursionRead(ExcursionBase):
    id: int
    description: str | None = None
    images: list[MediaRead]
    category_id: int
    points: list[PointRead]
    model_config = ConfigDict(from_attributes=True)

class ExcursionCreate(ExcursionBase):
    points: list[PointCreate] = []
    model_config = ConfigDict(from_attributes=True)

class ExcursionUpdate(ExcursionBase):
    id: int
    points: list[PointCreate] = []
    model_config = ConfigDict(from_attributes=True)

