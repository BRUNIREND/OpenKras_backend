from sqlalchemy import Column, Integer, Table, ForeignKey
from .base import Base

excursion_point_association = Table(
    "excursion_point_association",
    Base.metadata,
    Column("excursion_id", ForeignKey("excursions.id"), primary_key=True),
    Column("point_id", ForeignKey("points.id"), primary_key=True),
    Column("order", Integer)  # Порядок точки в конкретной экскурсии
)