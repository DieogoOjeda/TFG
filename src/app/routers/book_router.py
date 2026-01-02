from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.book_schema import BookCreate, BookRead, BookUpdate, BookCopyCreate, BookCopyRead
from app.services.book_service import delete_book_copy, create_book_with_copy, create_book_copy, list_books, get_book, update_book, delete_book, search_books
from app.utils.security import require_roles
from app.models.user_model import UserRole

router = APIRouter()


@router.post("/", response_model=BookRead, status_code=201)
def create_book(
    book_in: BookCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.LIBRARIAN)),
):
    return create_book_with_copy(db, book_in)


@router.get("/", response_model=list[BookRead])
def get_books(db: Session = Depends(get_db)):
    return list_books(db)


@router.get("/search", response_model=list[BookRead])
def search_books_endpoint(q: str, db: Session = Depends(get_db)):
    """
    Buscar libros por título, autor, isbn o materia.
    """
    return search_books(db, q)


@router.get("/{book_id}", response_model=BookRead)
def get_book_detail(book_id: int, db: Session = Depends(get_db)):
    return get_book(db, book_id)


@router.put("/{book_id}", response_model=BookRead)
def update_book_endpoint(
    book_id: int,
    book_in: BookUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.LIBRARIAN)),
):
    return update_book(db, book_id, book_in)


@router.delete("/{book_id}", status_code=204)
def delete_book_endpoint(
    book_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.LIBRARIAN)),
):
    delete_book(db, book_id)
    return

@router.post("/{book_id}/copies", response_model=BookCopyRead, status_code=201)
def create_book_copy_endpoint(
    book_id: int,
    copy_in: BookCopyCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.LIBRARIAN)),
):
    return create_book_copy(db, book_id, copy_in)

@router.delete("/{book_id}/copies/{copy_id}", status_code=204)
def delete_book_copy_endpoint(
    book_id: int,
    copy_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.LIBRARIAN)),
):
    delete_book_copy(db, book_id, copy_id)
    return