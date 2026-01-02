from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.loan_model import Loan, LoanStatus

from app.models.sanction_model import Sanction
from app.models.book_model import BookCopy, CopyStatus
from app.models.user_model import User
from app.models.reservation_model import Reservation, ReservationStatus
from app.services.policies_service import get_policy_for_role, get_loan_delta_days
from app.schemas.loan_schema import LoanCreate
from sqlalchemy.orm import Session


def list_all_loans(db: Session) -> list[Loan]:
    # Ordenados por fecha de fin (due_date asc)
    return (
        db.query(Loan)
        .order_by(Loan.due_date.asc())
        .all()
    )



def _ensure_user_and_copy(db: Session, user_id: int, copy_id: int) -> tuple[User, BookCopy]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    copy = db.query(BookCopy).filter(BookCopy.id == copy_id).first()
    if not copy:
        raise HTTPException(status_code=404, detail="Ejemplar no encontrado.")

    return user, copy


def create_loan(db: Session, loan_in: LoanCreate) -> Loan:
    # 1) Comprobar copia
    copy = db.query(BookCopy).filter(BookCopy.id == loan_in.copy_id).first()
    if not copy:
        raise HTTPException(status_code=404, detail="Ejemplar no encontrado.")

    if copy.is_reference:
        raise HTTPException(
            status_code=400,
            detail="No se puede prestar un ejemplar de referencia.",
        )

    if copy.status != CopyStatus.AVAILABLE:
        raise HTTPException(
            status_code=409,
            detail="El ejemplar no está disponible para préstamo.",
        )

    # 2) Crear préstamo
    loan_date = datetime.utcnow()
    due_date = loan_date + timedelta(days=15)  # por ejemplo

    loan = Loan(
        user_id=loan_in.user_id,
        copy_id=loan_in.copy_id,
        loan_date=loan_date,
        due_date=due_date,
        status=LoanStatus.ACTIVE,
    )

    # 3) Marcar la copia como prestada
    copy.status = CopyStatus.LOANED

    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


def renew_loan(db: Session, loan_id: int) -> Loan:
    now = datetime.utcnow()

    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado.")

    if loan.status != LoanStatus.ACTIVE:
        raise HTTPException(status_code=409, detail="Solo se pueden renovar préstamos activos.")

    if loan.due_date < now:
        # UC-04 E3
        raise HTTPException(
            status_code=409,
            detail="El préstamo ya está vencido; acuda a la biblioteca para regularizar.",
        )

    user = loan.user
    copy = loan.copy

    # BR-4.1: solo si no hay reservas activas
    has_active_reservation = (
        db.query(Reservation)
        .filter(
            Reservation.book_id == copy.book_id,
            Reservation.status.in_([ReservationStatus.ACTIVE, ReservationStatus.NOTIFIED]),
        )
        .count()
        > 0
    )
    if has_active_reservation:
        raise HTTPException(
            status_code=409,
            detail="No se puede renovar: existen reservas activas.",
        )

    # BR-4.2: máximo de renovaciones configurable por perfil
#    policy = get_policy_for_role(user.role)
#    if loan.renewals_count >= policy["max_renewals"]:
#        raise HTTPException(
#            status_code=400,
#            detail="Se alcanzó el máximo de renovaciones permitidas.",
#        )

    delta = get_loan_delta_days(user.role, is_reference=copy.is_reference)
    loan.due_date = loan.due_date + delta
#    loan.renewals_count += 1

    db.commit()
    db.refresh(loan)
    return loan


def return_loan(db: Session, loan_id: int) -> Loan:
    now = datetime.utcnow()

    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado.")

    if loan.status != LoanStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="El préstamo ya está cerrado.")

    loan.return_date = now

    # comprobar atraso y sanción simple (UC-05, UC-11)
    user = loan.user
    copy = loan.copy
    book = copy.book

    if now > loan.due_date:
        loan.status = LoanStatus.LATE

        # Ejemplo: bloquear 1 día por cada día de retraso
        days_late = (now.date() - loan.due_date.date()).days
        block_days = max(days_late, 1)
        user.blocked_until = now + timedelta(days=block_days)

        # 👇 Crear registro de sanción
        sanction = Sanction(
            user_id=user.id,
            book_id=book.id,
            days=block_days,
        )
        db.add(sanction)
    else:
        loan.status = LoanStatus.RETURNED


    copy = loan.copy

    # comprobar reservas pendientes (UC-05, UC-06)
    next_reservation = (
        db.query(Reservation)
        .filter(
            Reservation.book_id == copy.book_id,
            Reservation.status == ReservationStatus.ACTIVE,
        )
        .order_by(Reservation.created_at.asc())
        .first()
    )

    if next_reservation:
        next_reservation.status = ReservationStatus.NOTIFIED
        next_reservation.notified_at = now
        # ventana de recogida ejemplo: 2 días (BR-6.1: configurable)
        next_reservation.expires_at = now + timedelta(days=2)
        copy.status = CopyStatus.RESERVED
    else:
        copy.status = CopyStatus.AVAILABLE

    db.commit()
    db.refresh(loan)
    return loan


def list_user_loans(db: Session, user_id: int) -> list[Loan]:
    return db.query(Loan).filter(Loan.user_id == user_id).all()
