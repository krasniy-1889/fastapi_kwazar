from datetime import datetime

from pydantic import BaseModel
from pydantic.networks import EmailStr


class UserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    registration_date: datetime


class UserSchemaAdd(BaseModel):
    username: str
    email: EmailStr


class UserSchemaEdit(UserSchemaAdd): ...


class EmailSchema(BaseModel):
    email: str
