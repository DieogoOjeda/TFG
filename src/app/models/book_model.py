from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class AccessLevel(str, enum.Enum):
    GENERAL = "general"      # Prestables normalmente
    REFERENCE = "reference"  # Material de referencia (UC-10)


class CopyStatus(str, enum.Enum):
    AVAILABLE = "available"
    LOANED = "loaned"
    RESERVED = "reserved"
    NOT_LOANABLE = "not_loanable"  # Por política
    LOST = "lost"
    DAMAGED = "damaged"


class Book(Base):
    """
    Título (UC-01, UC-02, UC-12)
    """
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    authors = Column(String, nullable=False)  # "Autor1; Autor2"
    isbn = Column(String, index=True, nullable=True)
    edition = Column(String, nullable=True)
    subject = Column(String, nullable=True)

    access_level = Column(Enum(AccessLevel), nullable=False, default=AccessLevel.GENERAL)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    copies = relationship("BookCopy", back_populates="book", cascade="all, delete-orphan")
    reservations = relationship("Reservation", back_populates="book", cascade="all, delete-orphan")

    sanctions = relationship("Sanction", back_populates="book", cascade="all, delete-orphan")



class BookCopy(Base):
    """
    Ejemplar físico con código único (RB-02, BR-1.2)
    """
    __tablename__ = "book_copies"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)

    barcode = Column(String, unique=True, index=True, nullable=False)  # identificador ejemplar
    is_reference = Column(Boolean, default=False)  # si es material de referencia

    status = Column(Enum(CopyStatus), nullable=False, default=CopyStatus.AVAILABLE)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    book = relationship("Book", back_populates="copies")
    loans = relationship("Loan", back_populates="copy")
