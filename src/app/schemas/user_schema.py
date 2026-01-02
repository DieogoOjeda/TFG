from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.models.user_model import UserRole
from enum import Enum

#class UserRole(str, Enum):
#    STUDENT = "student"      # Estudiante
#    STAFF = "staff"          # PAS
#    FACULTY = "faculty"      # Profesorado/PDI
#    LIBRARIAN = "librarian"  # Bibliotecario/administrador


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole


class UserCreate(UserBase):
    external_id: str
    password: str = Field(min_length=8)


class UserRead(UserBase):
    id: int
    is_active: bool
    blocked_until: datetime | None = None
    role: UserRole

    class Config:
        from_attributes = True
