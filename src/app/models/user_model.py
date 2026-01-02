from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    STUDENT = "student"      # Estudiante
    STAFF = "staff"          # PAS
    FACULTY = "faculty"      # Profesorado/PDI
    LIBRARIAN = "librarian"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True)  # matrícula, DNI, etc.
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    password_hash = Column(String, nullable=False)
    # Sanción/bloqueo simple por retrasos (UC-11)
    blocked_until = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    loans = relationship("Loan", back_populates="user", cascade="all, delete-orphan")
    reservations = relationship(
        "Reservation",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    sanctions = relationship(
        "Sanction",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    loans = relationship("Loan", back_populates="user")
