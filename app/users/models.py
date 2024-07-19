from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm._orm_constructors import mapped_column
from sqlalchemy.orm.base import Mapped
from sqlalchemy.sql import func

from app.models import Base
from app.users.schema import UserSchema


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(length=60), unique=True)
    email: Mapped[str] = mapped_column(String(length=120), unique=True)
    registration_date: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def to_read_model(self) -> UserSchema:
        return UserSchema(
            id=self.id,
            username=self.username,
            email=self.email,
            registration_date=self.registration_date,
        )
