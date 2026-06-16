from typing import Optional, List

from pydantic import ConfigDict, BaseModel, Field, model_validator

from app.schemas.media import MediaRead


class PointBase(BaseModel):
    id: int

class PointUpdate(PointBase):
    id: int

class PointMediaAttachment(BaseModel):
    media_id: int
    position: int = 1

# Обновляем схему создания контента
class PointContentCreate(BaseModel):
    lang: str = Field(default="ru", max_length=5)
    name: str
    description: Optional[str] = None
    address: Optional[str] = None

    media_ids: List[int] = Field(default=[])

class PointCreate(BaseModel):
    excursion_id: int
    latitude: float
    longitude: float
    radius_meters: int = 20
    position: int = 0
    contents: List[PointContentCreate] = Field(default=[])

class PointContentRead(BaseModel):
    id: int
    point_id: int
    lang: str
    name: str
    description: Optional[str]
    address: Optional[str]
    media: List[MediaRead] = []

    class Config:
        from_attributes = True

class PointRead(PointBase):
    id: int
    latitude: float
    longitude: float
    radius_meters: int
    contents: list[PointContentRead] = []

    class Config:
        from_attributes = True