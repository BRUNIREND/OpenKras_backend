from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime
from app.database.base_class import Base


class UserOTP(Base):
    __tablename__ = "user_otps"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    code = Column(String, nullable=False)
    expires_at = Column(
        DateTime,
        nullable=False,
        default=lambda : datetime.utcnow() + timedelta(minutes=5)
    )

    @property
    def is_expired(self):
        return datetime.utcnow() > self.expires_at