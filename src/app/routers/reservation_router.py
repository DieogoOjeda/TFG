from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.reservation_schema import ReservationCreate, ReservationRead
from app.services.reservation_service import (
    create_reservation,
    cancel_reservation,
    list_user_reservations,
    list_reservations,
    list_reservations_by_user_email,
)

from app.utils.security import get_current_user, require_roles
from app.models.user_model import User, UserRole

router = APIRouter()


@router.post("/", response_model=ReservationRead, status_code=201)
def create_reservation_endpoint(
    reservation_in: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Si no es bibliotecario, solo puede reservar para sí mismo
    if current_user.role != UserRole.LIBRARIAN and reservation_in.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No puedes crear reservas para otros usuarios.")

    return create_reservation(db, reservation_in.user_id, reservation_in.book_id)


# ✅ NUEVO: admin ver todas / buscar por email
@router.get("/", response_model=list[ReservationRead])
def list_reservations_endpoint(
    email: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.LIBRARIAN)),
):
    if email:
        return list_reservations_by_user_email(db, email)
    return list_reservations(db)


@router.post("/{reservation_id}/cancel", response_model=ReservationRead, status_code=200)
def cancel_reservation_endpoint(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Política mínima: usuario puede cancelar la suya; admin puede cancelar cualquiera
    reservation = db.query(__import__("app.models.reservation_model", fromlist=["Reservation"]).Reservation).filter_by(id=reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")

    if current_user.role != UserRole.LIBRARIAN and reservation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No puedes cancelar reservas de otros usuarios.")

    return cancel_reservation(db, reservation_id)


@router.get("/user/{user_id}", response_model=list[ReservationRead])
def list_user_reservations_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Política mínima: usuario ve las suyas; admin ve cualquiera
    if current_user.role != UserRole.LIBRARIAN and user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No puedes ver reservas de otros usuarios.")

    return list_user_reservations(db, user_id)
