# schemas/media.py
from pydantic import BaseModel


class MediaRead(BaseModel):
    file_url: str
    media_type: str # 'IMAGE' или 'AUDIO'

    class Config:
        from_attributes = True

