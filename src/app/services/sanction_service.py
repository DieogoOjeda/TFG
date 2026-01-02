from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.sanction_model import Sanction
from app.models.book_model import BookCopy
from app.models.user_model import User
from app.schemas.sanction_schema import SanctionCreate


def create_sanction(db: Session, sanction_in: SanctionCreate) -> Sanction:
    # 1) Buscar la copia
    copy = db.query(BookCopy).filter(BookCopy.id == sanction_in.copy_id).first()
    if not copy:
        raise HTTPException(status_code=404, detail="Ejemplar (copia) no encontrado.")

    # 2) Determinar book_id
    book_id = sanction_in.book_id if sanction_in.book_id is not None else copy.book_id

    # 3) Crear sanción
    sanction = Sanction(
        user_id=sanction_in.user_id,
        book_id=book_id,
        copy_id=sanction_in.copy_id,
        days=sanction_in.days,
        created_at=datetime.utcnow(),
    )

    db.add(sanction)
    db.commit()
    db.refresh(sanction)
    return sanction


def list_sanctions_by_user(db: Session, user_id: int) -> list[Sanction]:
    return (
        db.query(Sanction)
        .filter(Sanction.user_id == user_id)
        .order_by(Sanction.created_at.desc())
        .all()
    )


# ✅ NUEVO: listar todas
def list_sanctions(db: Session) -> list[Sanction]:
    return (
        db.query(Sanction)
        .order_by(Sanction.created_at.desc())
        .all()
    )


# ✅ NUEVO: listar por email (búsqueda parcial, case-insensitive)
def list_sanctions_by_user_email(db: Session, email: str) -> list[Sanction]:
    email = (email or "").strip().lower()

    return (
        db.query(Sanction)
        .join(User, User.id == Sanction.user_id)
        .filter(User.email.ilike(f"%{email}%"))
        .order_by(Sanction.created_at.desc())
        .all()
    )
