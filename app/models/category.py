from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.base_class import Base

class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    icon_url = Column(String, nullable=True) # Ссылка на иконку в /static/icons/

    excursions = relationship("Excursion", back_populates="category")