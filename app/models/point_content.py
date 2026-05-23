from sqlalchemy.orm import relationship

from app.database.base_class import Base
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey


class PointContent(Base):
    __tablename__ = "point_content"

    id = Column(Integer, primary_key=True, index=True)
    point_id = Column(Integer, ForeignKey("points.id", ondelete="CASCADE"))
    lang = Column(String(5), default="ru", nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    address = Column(String)

    # Связи
    point = relationship("Point", back_populates="contents")
    # Связь с медиа (фото и аудио) через таблицу ассоциаций
    media = relationship(
        "Media",
             secondary="point_media_link",
             order_by="PointMediaLink.position"
        )

