from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.security import get_current_user, require_roles
from app.models.user_model import User, UserRole

from app.dependencies import get_db
from app.schemas.loan_schema import LoanCreate, LoanRead
from app.services.loan_service import (
    create_loan,
    renew_loan,
    return_loan,
    list_user_loans,
    list_all_loans
)

router = APIRouter()


@router.post("/", response_model=LoanRead, status_code=201)
def create_loan_endpoint(
    loan_in: LoanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Si no es bibliotecario, solo puede crear préstamos para sí mismo
    if current_user.role != UserRole.LIBRARIAN and loan_in.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="No puedes crear préstamos para otros usuarios."
        )

    return create_loan(db, loan_in)



@router.post("/{loan_id}/renew", response_model=LoanRead, status_code=201)
def renew_loan_endpoint(loan_id: int, db: Session = Depends(get_db)):
    return renew_loan(db, loan_id)


@router.post("/{loan_id}/return", response_model=LoanRead, status_code=201)
def return_loan_endpoint(loan_id: int, db: Session = Depends(get_db)):
    return return_loan(db, loan_id)


@router.get("/user/{user_id}", response_model=list[LoanRead])
def list_user_loans_endpoint(user_id: int, db: Session = Depends(get_db)):
    return list_user_loans(db, user_id)


@router.get("/", response_model=list[LoanRead])
def list_loans_endpoint(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.LIBRARIAN)),
):
    """
    Lista todos los préstamos (solo bibliotecario),
    ordenados por fecha de fin (due_date).
    """
    return list_all_loans(db)