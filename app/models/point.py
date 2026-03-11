# app/models/point.py
from sqlalchemy import Column, Integer, String, Text, Float
from sqlalchemy.orm import relationship
from .base import Base
from .assocations import excursion_point_association

class Point(Base):
    __tablename__ = "points"

    id = Column(Integer, primary_key=True, index=True)
    excursions = relationship("Excursion", secondary=excursion_point_association, back_populates="points")

    title = Column(String(150), nullable=True)
    text = Column(Text, nullable=True)
    address = Column(String)

    # Координаты
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Контент
    audio_url = Column(String, nullable=True)
    image_url = Column(String, nullable=True, default="ХУЙ") #TODO(Поменять)
    radius_meters = Column(Integer, default=50) # Радиус активации аудио для места

