from sqlalchemy import Column, Integer, Table, ForeignKey
from app.database.base_class import Base

excursion_point_association = Table(
    "excursion_point_association",
    Base.metadata,
    Column("excursion_id", ForeignKey("excursions.id"), primary_key=True),
    Column("point_id", ForeignKey("points.id"), primary_key=True),
    Column("order", Integer)  # Порядок точки в конкретной экскурсии
)


user_favorite_excursions = Table(
    "user_favorite_excursions",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("excursion_id", ForeignKey("excursions.id", ondelete="CASCADE"), primary_key=True),
)