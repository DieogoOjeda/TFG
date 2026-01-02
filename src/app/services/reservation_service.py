from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy import func

from app.models.reservation_model import Reservation, ReservationStatus
from app.models.book_model import Book, BookCopy
from app.models.user_model import User
from app.models.loan_model import Loan, LoanStatus


def create_reservation(db: Session, user_id: int, book_id: int) -> Reservation:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado.")

    now = datetime.now(timezone.utc)

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo.")

    if user.blocked_until and user.blocked_until > now:
        raise HTTPException(status_code=400, detail="Usuario bloqueado por sanciones.")

    # No reservar material de referencia
    if book.access_level == book.access_level.REFERENCE:
        raise HTTPException(
            status_code=400,
            detail="Este material de referencia no admite reservas.",
        )

    # No duplicar reserva del mismo título
    existing = (
        db.query(Reservation)
        .filter(
            Reservation.user_id == user.id,
            Reservation.book_id == book.id,
            Reservation.status.in_([ReservationStatus.ACTIVE, ReservationStatus.NOTIFIED]),
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Ya tienes una reserva activa para este título.",
        )

    # ✅ Regla pedida: SOLO se puede reservar si TODAS las copias están prestadas
    total_copies = db.query(func.count(BookCopy.id)).filter(BookCopy.book_id == book.id).scalar() or 0
    if total_copies == 0:
        raise HTTPException(status_code=400, detail="Este libro no tiene copias disponibles en el sistema.")

    active_loans = (
        db.query(func.count(Loan.id))
        .join(BookCopy, BookCopy.id == Loan.copy_id)
        .filter(
            BookCopy.book_id == book.id,
            Loan.status == LoanStatus.ACTIVE,
        )
        .scalar()
        or 0
    )

    # Si hay al menos una copia NO prestada, no permitimos reservar
    if active_loans < total_copies:
        raise HTTPException(
            status_code=409,
            detail="Hay copias disponibles; no se permite reservar si el libro puede prestarse.",
        )

    reservation = Reservation(user_id=user.id, book_id=book.id, status=ReservationStatus.ACTIVE)
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


def cancel_reservation(db: Session, reservation_id: int) -> Reservation:
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")

    if reservation.status not in (ReservationStatus.ACTIVE, ReservationStatus.NOTIFIED):
        raise HTTPException(status_code=400, detail="La reserva no está activa.")

    reservation.status = ReservationStatus.CANCELLED
    db.commit()
    db.refresh(reservation)
    return reservation


def list_user_reservations(db: Session, user_id: int) -> list[Reservation]:
    return (
        db.query(Reservation)
        .filter(
            Reservation.user_id == user_id,
            Reservation.status.in_([ReservationStatus.ACTIVE, ReservationStatus.NOTIFIED, ReservationStatus.FULFILLED]),
        )
        .order_by(Reservation.created_at.desc())
        .all()
    )


# ✅ NUEVO: admin lista todas
def list_reservations(db: Session) -> list[Reservation]:
    return (
        db.query(Reservation)
        .order_by(Reservation.created_at.desc())
        .all()
    )


# ✅ NUEVO: admin filtra por email
def list_reservations_by_user_email(db: Session, email: str) -> list[Reservation]:
    email = (email or "").strip().lower()
    return (
        db.query(Reservation)
        .join(User, User.id == Reservation.user_id)
        .filter(User.email.ilike(f"%{email}%"))
        .order_by(Reservation.created_at.desc())
        .all()
    )
