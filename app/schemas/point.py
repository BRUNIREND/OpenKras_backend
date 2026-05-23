from pydantic import ConfigDict, BaseModel, Field, model_validator

from app.schemas.media import MediaRead


class PointBase(BaseModel):
    id: int



class PointCreate(PointBase):
    excursion_id: int

class PointUpdate(PointBase):
    id: int


class PointContentRead(BaseModel):
    name: str
    description: str | None
    lang: str
    address: str | None = None

    # Разделяем медиа в ответе API
    media: list[MediaRead] = []
    # audio: list[MediaRead] = []
    # images: list[MediaRead]
    # audio: list[MediaRead]

    class Config:
        from_attributes = True

    # @property
    # def images(self):
    #     return [m for m in self.media if m.media_type == "IMAGE"]
    #
    # @property
    # def audio(self):
    #     return [m for m in self.media if m.media_type == "AUDIO"]

class PointRead(PointBase):
    id: int
    latitude: float
    longitude: float
    radius_meters: int
    contents: list[PointContentRead] = []

    class Config:
        from_attributes = True
