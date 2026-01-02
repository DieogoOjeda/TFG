from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy import or_

from app.models.book_model import Book, BookCopy, CopyStatus
from app.schemas.book_schema import BookCreate, BookUpdate, BookCopyCreate


def create_book_with_copy(db: Session, book_in: BookCreate) -> Book:
    if not book_in.title or not book_in.authors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Título y autores son obligatorios.",
        )

    book = Book(
        title=book_in.title,
        authors=book_in.authors,
        isbn=book_in.isbn,
        edition=book_in.edition,
        subject=book_in.subject,
        access_level=book_in.access_level,
    )
    db.add(book)
    db.flush()

    copy = BookCopy(
        book_id=book.id,
        barcode=book_in.first_copy_barcode,
        is_reference=book_in.first_copy_is_reference,
        status=CopyStatus.AVAILABLE
        if not book_in.first_copy_is_reference
        else CopyStatus.NOT_LOANABLE,
    )
    db.add(copy)
    db.commit()
    db.refresh(book)
    return book

def get_last_copy_barcode(db: Session, book_id: int) -> str | None:
    last_copy = (
        db.query(BookCopy)
        .filter(BookCopy.book_id == book_id)
        .order_by(BookCopy.id.desc())   # o .order_by(BookCopy.created_at.desc()) si tienes fecha
        .first()
    )

    if last_copy is None:
        return None  # el libro no tiene copias

    return last_copy.barcode


def create_book_copy(db: Session, book_id: int, copy_in: BookCopyCreate) -> BookCopy:
    # Comprobar que el libro existe
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado."
        )

    # (Opcional) evitar códigos de barra duplicados
    existing = db.query(BookCopy).filter(BookCopy.barcode == copy_in.barcode).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una copia con ese código de barras."
        )

    status_copy = (
        CopyStatus.NOT_LOANABLE if copy_in.is_reference else CopyStatus.AVAILABLE
    )

    copy = BookCopy(
        book_id=book.id,
        barcode=copy_in.barcode,
        is_reference=copy_in.is_reference,
        status=status_copy,
    )

    db.add(copy)
    db.commit()
    db.refresh(copy)
    return copy


def list_books(db: Session) -> list[Book]:
    return db.query(Book).all()


def get_book(db: Session, book_id: int) -> Book:
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado.")
    return book


def update_book(db: Session, book_id: int, book_in: BookUpdate) -> Book:
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado.")

    data = book_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(book, field, value)

    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, book_id: int) -> None:
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado.")

    db.delete(book)
    db.commit()


def search_books(db: Session, q: str) -> list[Book]:
    q_like = f"%{q}%"
    return (
        db.query(Book)
        .filter(
            or_(
                Book.title.ilike(q_like),
                Book.authors.ilike(q_like),
                Book.isbn.ilike(q_like),
                Book.subject.ilike(q_like),
            )
        )
        .all()
    )

def delete_book_copy(db: Session, book_id: int, copy_id: int) -> None:
    copy = (
        db.query(BookCopy)
        .filter(BookCopy.id == copy_id, BookCopy.book_id == book_id)
        .first()
    )
    if not copy:
        raise HTTPException(status_code=404, detail="Copia no encontrada")

    db.delete(copy)
    db.commit()
