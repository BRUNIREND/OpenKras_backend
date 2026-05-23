import enum

from sqlalchemy import Column, Integer, String, Enum

from app.database.base_class import Base


class MediaType(str, enum.Enum):
    IMAGE = 'image'
    AUDIO = 'audio'

class Media(Base):
    __tablename__ = "media"

    id = Column(Integer,primary_key=True, index=True)
    file_url = Column(String, nullable=False)
    media_type = Column(
        Enum(MediaType, name="media_type", create_type=False),
        default=MediaType.IMAGE,
        nullable=False
    )

