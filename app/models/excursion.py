# app/models/excursions.py
import enum

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .assocations import excursion_point_association
from app.database.base_class import Base



class ExcursionStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"

class Excursion(Base):
    __tablename__ = "excursions"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("category.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    status = Column(Enum(ExcursionStatus), default=ExcursionStatus.DRAFT, nullable=False)

    duration = Column(Integer, nullable=True)
    distance = Column(Float, nullable=True)

    points = relationship("Point", secondary=excursion_point_association, back_populates="excursions", order_by="Point.position")
    category = relationship("Category", back_populates="excursions")
    images = relationship("Media", secondary="excursion_media_link", order_by="ExcursionMediaLink.position")

