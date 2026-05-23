# app/models/point.py
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base_class import Base
from .assocations import excursion_point_association

class Point(Base):
    __tablename__ = "points"

    id = Column(Integer, primary_key=True, index=True)
    # Координаты
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius_meters = Column(Integer, default=20, nullable=False) # Радиус активации аудио для места
    excursion_id = Column(Integer, ForeignKey("excursions.id", ondelete="CASCADE"))

    excursions = relationship("Excursion", secondary=excursion_point_association, back_populates="points")
    contents = relationship("PointContent", back_populates="point", cascade="all, delete-orphan")
    position = Column(Integer, default=0)