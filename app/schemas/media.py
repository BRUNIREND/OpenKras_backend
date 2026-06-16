# schemas/media.py
from pydantic import BaseModel


class MediaRead(BaseModel):
    id: int
    file_url: str
    media_type: str

    class Config:
        from_attributes = True

class LinkMediaRequest(BaseModel):
    media_id: int
    position: int = 0


