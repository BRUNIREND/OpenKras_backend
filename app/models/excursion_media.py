from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database.base_class import Base

class ExcursionMediaLink(Base):
    __tablename__ = "excursion_media_link"
    excursion_id = Column(Integer, ForeignKey("excursions.id", ondelete="CASCADE"), primary_key=True)
    media_id = Column(Integer, ForeignKey("media.id", ondelete="CASCADE"), primary_key=True)
    position = Column(Integer, default=0)