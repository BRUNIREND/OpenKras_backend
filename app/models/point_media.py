from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from app.database.base_class import Base

# Связь Контент Точки <-> Медиа
class PointMediaLink(Base):
    __tablename__ = "point_media_link"
    point_content_id = Column(Integer, ForeignKey("point_content.id", ondelete="CASCADE"), primary_key=True)
    media_id = Column(Integer, ForeignKey("media.id", ondelete="CASCADE"), primary_key=True)
    position = Column(Integer, default=0)
