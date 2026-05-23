import enum

from sqlalchemy.orm import relationship

from app.database.base_class import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.sql import func

from app.models.assocations import user_favorite_excursions


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    favorites = relationship("Excursion", secondary=user_favorite_excursions, backref="favorited_by")

    role = Column(
        Enum(UserRole, name="userrole", create_type=False),
        default=UserRole.USER,
        nullable=False
    )
