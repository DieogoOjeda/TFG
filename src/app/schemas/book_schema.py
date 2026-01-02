from datetime import datetime
from pydantic import BaseModel
from app.models.book_model import AccessLevel, CopyStatus


class BookCopyBase(BaseModel):
    barcode: str
    is_reference: bool = False

class BookCopyCreate(BookCopyBase):
    """
    Datos para crear una nueva copia de un libro existente.
    """
    pass

class BookCopyRead(BookCopyBase):
    id: int
    status: CopyStatus

    class Config:
        from_attributes = True


class BookBase(BaseModel):
    title: str
    authors: str
    isbn: str | None = None
    edition: str | None = None
    subject: str | None = None
    access_level: AccessLevel = AccessLevel.GENERAL


class BookCreate(BookBase):
    # Alta de libro + 1 ejemplar
    first_copy_barcode: str
    first_copy_is_reference: bool = False


class BookUpdate(BaseModel):
    title: str | None = None
    authors: str | None = None
    isbn: str | None = None
    edition: str | None = None
    subject: str | None = None
    access_level: AccessLevel | None = None


class BookRead(BookBase):
    id: int
    created_at: datetime
    copies: list[BookCopyRead] = []

    class Config:
        from_attributes = True
